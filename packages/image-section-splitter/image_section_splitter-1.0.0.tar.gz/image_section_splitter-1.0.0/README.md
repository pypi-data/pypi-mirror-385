# Image Section Splitter

세로로 긴 상세페이지 이미지를 시각적 경계 기준으로 안전하게 섹션 분리합니다.

## 특징

- ✅ 시각적 경계 자동 감지 (여백/디바이더/콘텐츠 변화)
- ✅ 텍스트 컷 방지 (섹션 안의 글자 절대 안 잘림)
- ✅ 허프 변환 기반 가로선 검출
- ✅ 최소 섹션 높이 자동 병합
- ✅ 진단 플롯 생성

## 설치

```bash
# uv 사용
uv add image-section-splitter
# or
uv add git+https://github.com/gandol2/image-section-splitter.git

# pip 사용
pip install image-section-splitter
or
pip install git+https://github.com/gandol2/image-section-splitter.git
```

## 사용법

### 기본 사용

```python
from image_section_splitter import split_image_sections

sections = split_image_sections(
    image_path="./input.png",
    output_dir="./sections"
)

for section in sections:
    print(f"Section {section.order}: {section.height}px")
```

### 클래스 사용 (커스터마이징)

```python
from image_section_splitter import ImageSectionSplitter

splitter = ImageSectionSplitter(debug_verbose=True)

sections = splitter.split(
    image_path="./input.png",
    output_dir="./sections",
    save_diagnostic=True
)
```

## 출력

- `sections/section_XXXX_YYYYYY-ZZZZZZ.png`: 분리된 섹션 이미지들
- `sections/sections.csv`: 섹션 정보 (순서, 좌표, 높이, 경로)
- `sections/diagnostic.png`: 진단 플롯 (선택적)

## 라이센스

```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
