# -*- coding: utf-8 -*-
"""
상세페이지 이미지 섹션 분리 모듈

세로로 긴 상세페이지 이미지를 시각적 경계 기준으로 안전하게 섹션 분리
"""

import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List
from dataclasses import dataclass


@dataclass
class SectionInfo:
    """섹션 정보"""

    order: int
    top: int
    bottom: int
    height: int
    path: str


class ImageSectionSplitter:
    """상세페이지 이미지 섹션 분리기"""

    def __init__(self, debug_verbose: bool = True):
        """
        Args:
            debug_verbose: 디버그 출력 여부
        """
        self.DEBUG_VERBOSE = debug_verbose

        # --- 파라미터(운영 기본값) - 원본 그대로 ---
        self.REF_W = 860

        # 분할 파라미터
        self.MIN_SECTION_H = 600
        self.MIN_GAP_PX = 1
        self.MERGE_NEAR = 400

        # 신호 결합 가중치
        self.EDGE_WEIGHT = 0.90
        self.VAR_WEIGHT = 0.8
        self.SMOOTH_SIGMA = 0.2
        self.GAP_THRESH = 0.99

        # 허프 가로선 검출
        self.LINE_BAND = 10
        self.LINE_THRESH = 0.18

        # 텍스트 컷 방지 스냅
        self.EDGE_CUT_T = 0.035
        self.STD_CUT_T = 0.055
        self.SEARCH_UP = 40
        self.SEARCH_DOWN = 1
        self.LINE_SNAP_BAND = 1

    def _dbg(self, msg: str) -> None:
        """디버그 메시지 출력"""
        if self.DEBUG_VERBOSE:
            print(f"[디버그] {msg}")

    def split(
        self,
        image_path: str,
        output_dir: str,
        save_diagnostic: bool = True,
    ) -> List[SectionInfo]:
        """
        이미지를 섹션으로 분리

        Args:
            image_path: 입력 이미지 경로
            output_dir: 출력 디렉토리
            save_diagnostic: 진단 이미지 저장 여부

        Returns:
            List[SectionInfo]: 섹션 정보 리스트
        """
        # --- 0) 출력 초기화 ---
        os.makedirs(output_dir, exist_ok=True)
        for file in os.listdir(output_dir):
            try:
                os.remove(os.path.join(output_dir, file))
            except Exception:
                pass

        # --- 1) 이미지 로드 + 가로폭 860px 강제 변환 ---
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")

        h0, w0 = img.shape[:2]
        if w0 != self.REF_W:
            scale = self.REF_W / float(w0)
            new_h = int(round(h0 * scale))
            interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
            img = cv2.resize(img, (self.REF_W, new_h), interpolation=interp)

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # --- 2) 에지 맵 (Canny, 자동 임계값) ---
        med = np.median(gray)
        low = int(max(0, 0.66 * med))
        high = int(min(255, 1.33 * med))
        edges = cv2.Canny(gray, threshold1=low, threshold2=high)

        # Hough 민감도 향상을 위한 수평 클로징(얇은 끊김 메움)
        _h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 1))
        edges_hough = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, _h_kernel)

        # --- 2.5) 가로선 강도(line_strength) 계산 (허프 직선 기반) ---
        HOUGH_MIN_LEN = int(0.40 * w)
        HOUGH_MAX_GAP = 10
        HOUGH_THRESH = 90

        line_strength = np.zeros(h, dtype=np.float32)
        lines = cv2.HoughLinesP(
            edges_hough,
            rho=1,
            theta=np.pi / 180,
            threshold=HOUGH_THRESH,
            minLineLength=HOUGH_MIN_LEN,
            maxLineGap=HOUGH_MAX_GAP,
        )
        if lines is not None:
            for l in lines.reshape(-1, 4):
                x1, y1, x2, y2 = map(int, l)
                dy = abs(y2 - y1)
                dx = abs(x2 - x1) + 1e-6
                if dy / dx <= 0.1:  # 수평에 가까운 선만
                    y_center = int(round(0.5 * (y1 + y2)))
                    y0 = max(0, y_center - self.LINE_BAND)
                    y1b = min(h - 1, y_center + self.LINE_BAND)
                    line_strength[y0 : y1b + 1] += 1.0
        if line_strength.max() > 0:
            line_strength /= line_strength.max()

        # --- 3) 행(row) 단위 신호 만들기 ---
        # 에지 밀도(행별 에지 비율)
        edge_density = (edges > 0).astype(np.float32).mean(axis=1)
        # 행 밝기 표준편차 정규화
        row_std = gray.astype(np.float32).std(axis=1)
        row_std_norm = (row_std - row_std.min()) / (
            row_std.max() - row_std.min() + 1e-6
        )
        # 수직 그래디언트(가로 경계에 민감) 보조 신호
        sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_y = np.abs(sobel_y).mean(axis=1)
        grad_y = (grad_y - grad_y.min()) / (grad_y.max() - grad_y.min() + 1e-6)
        # 결합 신호(콘텐츠 강도)
        signal = self.EDGE_WEIGHT * edge_density + self.VAR_WEIGHT * row_std_norm
        signal = np.maximum(signal, 0.6 * grad_y)  # 가로 경계가 강하면 신호 상향
        signal = np.clip(signal, 0.0, 1.0)

        # --- 4) 1D 스무딩 ---
        sig = signal.reshape(-1, 1).astype(np.float32)
        sig_blur = cv2.GaussianBlur(sig, ksize=(0, 0), sigmaX=self.SMOOTH_SIGMA).ravel()
        sig_blur = (sig_blur - sig_blur.min()) / (
            sig_blur.max() - sig_blur.min() + 1e-6
        )
        # 여백성
        gapness = 1.0 - sig_blur

        # --- 5) 경계 후보 추출(여백 OR 라인) ---
        is_gap = gapness > self.GAP_THRESH
        is_line = line_strength > self.LINE_THRESH
        is_boundary_mask = np.logical_or(is_gap, is_line)

        boundaries = []  # 경계 y 리스트(스냅 전)
        boundary_types = {}  # y -> 'line' | 'gap'

        in_run = False
        run_start = 0
        for y in range(h):
            if is_boundary_mask[y] and not in_run:
                in_run = True
                run_start = y
            if (not is_boundary_mask[y] or y == h - 1) and in_run:
                in_run = False
                run_end = y if not is_boundary_mask[y] else y
                run_len = run_end - run_start + 1
                contains_line = bool(is_line[run_start : run_end + 1].any())
                mid = (run_start + run_end) // 2
                # 라인이 있으면 길이와 무관하게 우선 채택
                if contains_line or run_len >= self.MIN_GAP_PX:
                    boundaries.append(mid)
                    boundary_types[mid] = "line" if contains_line else "gap"
                    self._dbg(
                        f"경계 후보 추가: y={mid} (구간 {run_start}-{run_end}, 길이={run_len}, 타입={'line' if contains_line else 'gap'})"
                    )
                else:
                    self._dbg(
                        f"경계 후보 제외(짧음): 구간 {run_start}-{run_end}, 길이={run_len} < {self.MIN_GAP_PX}"
                    )

        # 병합/스냅 전 비교용: 원시 경계 스냅샷 저장
        boundaries_raw = boundaries.copy()

        # --- 6) 경계 병합(라인 우선 보존) ---
        if boundaries:
            boundaries.sort()
            self._dbg(f"경계 후보(병합 전): {boundaries}")
            merged = [boundaries[0]]
            for b in boundaries[1:]:
                if b - merged[-1] < self.MERGE_NEAR:
                    a = merged[-1]
                    ty_a = boundary_types.get(a, "gap")
                    ty_b = boundary_types.get(b, "gap")
                    if ty_a == "line" and ty_b != "line":
                        keep = a
                    elif ty_b == "line" and ty_a != "line":
                        keep = b
                    elif ty_a == "line" and ty_b == "line":
                        keep = a if line_strength[a] >= line_strength[b] else b
                    else:
                        keep = int((a + b) // 2)
                    self._dbg(
                        f"경계 병합: {a} & {b} -> {keep} (타입 a={ty_a}, b={ty_b})"
                    )
                    merged[-1] = keep
                    boundary_types[keep] = (
                        "line" if (ty_a == "line" or ty_b == "line") else "gap"
                    )
                    if keep != a:
                        boundary_types.pop(a, None)
                else:
                    merged.append(b)
            boundaries = merged
            self._dbg(f"경계(병합 후): {boundaries}")
            # 비교용: 병합 후 스냅샷 저장
            boundaries_merged = boundaries.copy()
        else:
            boundaries_merged = []

        # --- 6.5) 텍스트 컷 방지 스냅 ---
        edges_bin = (edges > 0).astype(np.float32)
        edge_row = edges_bin.mean(axis=1).astype(np.float32)
        row_std = gray.astype(np.float32).std(axis=1)
        row_std_norm = (row_std - row_std.min()) / (
            row_std.max() - row_std.min() + 1e-6
        )

        snapped = []
        for b in boundaries:
            ty = boundary_types.get(b, "gap")
            best = b

            def is_safe_row(y: int) -> bool:
                return (
                    (0 <= y < h)
                    and (edge_row[y] <= self.EDGE_CUT_T)
                    and (row_std_norm[y] <= self.STD_CUT_T)
                )

            if ty == "line":
                for dy in range(-self.LINE_SNAP_BAND, self.LINE_SNAP_BAND + 1):
                    y = b + dy
                    if is_safe_row(y):
                        best = y
                        break
            else:
                found = False
                for dy in range(0, self.SEARCH_UP + 1):
                    y = b - dy
                    if is_safe_row(y):
                        best = y
                        found = True
                        break
                if not found:
                    for dy in range(1, self.SEARCH_DOWN + 1):
                        y = b + dy
                        if is_safe_row(y):
                            best = y
                            break
            snapped.append(int(best))
            if best != b:
                self._dbg(
                    f"경계 스냅: {b} -> {best} (타입={ty}, edge={edge_row[best]:.3f}, std={row_std_norm[best]:.3f})"
                )

        snapped = sorted(set([y for y in snapped if 5 <= y <= h - 6]))
        refined = []
        for y in snapped:
            if not refined or (y - refined[-1]) > max(5, int(self.MERGE_NEAR * 0.3)):
                refined.append(y)
        boundaries = refined
        self._dbg(f"경계(스냅 후): {boundaries}")
        # 비교용: 최종 경계 스냅샷 저장
        boundaries_final = boundaries.copy()

        # --- 7) 섹션으로 분할(전체 커버 보장) ---
        cuts = [0] + boundaries + [h]
        sections = []
        for i in range(len(cuts) - 1):
            top, bot = int(cuts[i]), int(cuts[i + 1])
            if bot > top:
                sections.append((top, bot))
                self._dbg(f"섹션 추가(원본): {top}-{bot} (높이={bot - top})")

        # 최소 높이 병합(너무 작은 구간 제거)
        i = 0
        while i < len(sections):
            top, bot = sections[i]
            if (bot - top) < self.MIN_SECTION_H and len(sections) > 1:
                if i > 0:
                    prev_top, prev_bot = sections[i - 1]
                    sections[i - 1] = (prev_top, bot)
                    sections.pop(i)
                    i = max(0, i - 1)
                elif i + 1 < len(sections):
                    next_top, next_bot = sections[i + 1]
                    sections[i] = (top, next_bot)
                    sections.pop(i + 1)
                else:
                    i += 1
            else:
                i += 1

        # 안전 클램프
        safe_sections = []
        for top, bot in sections:
            top = max(0, min(h - 1, int(top)))
            bot = max(top + 1, min(h, int(bot)))
            if bot > top:
                safe_sections.append((top, bot))
        sections = safe_sections

        # 연속성 체크
        assert sections and sections[0][0] == 0 and sections[-1][1] == h
        for i in range(len(sections) - 1):
            assert sections[i][1] == sections[i + 1][0]

        # --- 8) 저장 ---
        rows = []
        for idx, (top, bot) in enumerate(sections, start=1):
            crop = img[top:bot, :]
            out_path = os.path.join(
                output_dir, f"section_{idx:04d}_{top:06d}-{bot:06d}.png"
            )
            cv2.imwrite(out_path, crop)
            rows.append(
                {
                    "order": idx,
                    "top": top,
                    "bottom": bot,
                    "height": bot - top,
                    "path": out_path,
                }
            )

        df = (
            pd.DataFrame(rows, columns=["order", "top", "bottom", "height", "path"])
            if rows
            else pd.DataFrame(columns=["order", "top", "bottom", "height", "path"])
        )
        csv_path = os.path.join(output_dir, "sections.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8")

        # --- 9) 진단 플롯 (좌: 신호, 우: 원본 이미지+경계) ---
        if save_diagnostic:
            fig = plt.figure(figsize=(10, 10))

            # 좌/우 패널 배치 사양: [left, bottom, width, height] (figure 좌표)
            left_rect = [0.07, 0.04, 0.48, 0.92]  # 좌측 그래프 폭 고정(0.48)
            gap = 0.004  # 두 패널 간 간격(거의 밀착)
            right_margin = 0.02  # 우측 바깥 여백

            ax = fig.add_axes([0.07, 0.04, 0.43, 0.92])  # 좌측: 그래프(고정 폭)
            left_img = left_rect[0] + left_rect[2] + gap
            ax_img = fig.add_axes(
                [left_img, left_rect[1], 1.0 - left_img - right_margin, left_rect[3]]
            )

            # 좌측: 신호
            ax.plot(sig_blur, np.arange(h), lw=1.0, label="content-signal (smoothed)")
            ax.plot(gapness, np.arange(h), lw=1.0, label="gapness")
            for b in boundaries_raw:
                ax.axhline(b, color="gray", lw=0.6, alpha=0.5, linestyle=":")
            for b in boundaries_merged:
                ax.axhline(b, color="orange", lw=0.8, alpha=0.6, linestyle="--")
            for b in boundaries_final:
                ax.axhline(b, color="red", lw=1.0, alpha=0.8)
            # 축 범위 고정: 상단 여백 제거 (y축 0~h를 정확히 사용)
            ax.set_xlim(0.0, 1.0)
            ax.set_ylim(h - 0.5, -0.5)
            ax.margins(x=0.0, y=0.0)
            ax.set_xlabel("value (0~1)")
            ax.set_ylabel("y (px)")
            ax.legend(loc="lower right", frameon=False)
            ax.spines["right"].set_visible(False)

            # 우측: 이미지(동일 y스케일)
            gap = 0.005  # 거의 밀착
            bbox = ax.get_position()  # figure 좌표계
            left_img = bbox.x1 + gap
            width_img = 1.0 - left_img - 0.04  # 우측 여백(0.04)은 상황에 맞게
            ax_img = fig.add_axes([left_img, bbox.y0, width_img, bbox.height])
            im = ax_img.imshow(
                cv2.cvtColor(img, cv2.COLOR_BGR2RGB), extent=(0, w, h, 0)
            )
            # 좌측 정렬: 축 앵커를 서쪽(W)으로 고정하고 종횡비 유지
            ax_img.set_xlim(0, w)
            ax_img.set_ylim(h, 0)
            ax_img.set_aspect("equal", adjustable="box")
            ax_img.set_anchor("W")
            for b in boundaries_raw:
                ax_img.axhline(b, color="gray", lw=0.6, alpha=0.5, linestyle=":")
            for b in boundaries_merged:
                ax_img.axhline(b, color="orange", lw=0.8, alpha=0.6, linestyle="--")
            for b in boundaries_final:
                ax_img.axhline(b, color="red", lw=1.0, alpha=0.8)
            # 우측 이미지 축 라벨/눈금/테두리 숨김
            ax_img.set_xlabel("")
            ax_img.set_ylabel("")
            ax_img.tick_params(
                left=False, labelleft=False, bottom=False, labelbottom=False
            )
            ax_img.set_xticks([])
            ax_img.set_yticks([])
            for spine in ax_img.spines.values():
                spine.set_visible(False)

            # 저장(여백 최소화, 폭 고정 유지)
            plt.savefig(
                os.path.join(output_dir, "diagnostic.png"), dpi=150, pad_inches=0.02
            )
            plt.close(fig)

        print(f"✅ 완료(v2). 섹션 개수: {len(sections)}")
        print(f"- CSV 경로: {csv_path}")
        if save_diagnostic:
            print(f"- 진단 이미지: {os.path.join(output_dir, 'diagnostic.png')}")

        # SectionInfo 리스트 생성
        section_infos = [
            SectionInfo(
                order=row["order"],
                top=row["top"],
                bottom=row["bottom"],
                height=row["height"],
                path=row["path"],
            )
            for row in rows
        ]

        return section_infos


# 편의 함수
def split_image_sections(
    image_path: str,
    output_dir: str,
    debug_verbose: bool = True,
    save_diagnostic: bool = True,
) -> List[SectionInfo]:
    """
    이미지를 섹션으로 분리 (단일 API)

    Args:
        image_path: 입력 이미지 경로
        output_dir: 출력 디렉토리
        debug_verbose: 디버그 출력 여부
        save_diagnostic: 진단 이미지 저장 여부

    Returns:
        List[SectionInfo]: 섹션 정보 리스트
    """
    splitter = ImageSectionSplitter(debug_verbose=debug_verbose)
    return splitter.split(
        image_path=image_path, output_dir=output_dir, save_diagnostic=save_diagnostic
    )


if __name__ == "__main__":
    # 테스트
    sections = split_image_sections(image_path="./image.png", output_dir="./result")

    print(f"\n총 {len(sections)}개 섹션 생성:")
    for section in sections:
        print(f"  {section.order}. {section.top}-{section.bottom} ({section.height}px)")
