# gandol2-image-ocr-v2

PaddleOCR 기반의 간단한 이미지 OCR(PNG/JPG 등) 유틸리티입니다. GPU/CPU 선택, 한국어(`korean`) 포함 다국어 OCR, 결과물(주석 이미지/JSON) 저장을 지원합니다.

> 이 패키지는 사용자가 제공한 코드(`main.py`)를 기반으로 PyPI 배포가 가능하도록 정리한 것입니다. 의존성은 사용자가 제공한 `pyproject.toml`의 값을 그대로 반영했습니다.

## ✨ 기능

- 🖼️ 단일 이미지 OCR 실행
- 🌐 언어 선택: `korean`(기본) 등 PaddleOCR 지원 언어
- 🧠 PaddleOCR 옵션(문서 기울임/펴기 등) 기본 비활성화
- 💾 출력 저장: 주석(바운딩박스) 이미지와 JSON 결과를 지정 경로에 저장
- ⚙️ CLI 제공: `gandol2-image-ocr` 명령으로 바로 실행
- 🚀 GPU/CPU 전환 옵션

## 📦 설치

> **주의:** 아래 의존성은 `pyproject.toml`의 값을 그대로 사용하며, `paddlepaddle-gpu==3.2.0`, `paddleocr>=3.2.0`이 포함됩니다. 환경(파이썬/CUDA/드라이버)에 따라 설치가 제한될 수 있습니다.

```bash
# pyproject.toml 의존성을 지정후 설치해주세요.

dependencies = [
    ...
    "paddlepaddle-gpu==3.2.0"
    ...
]

[tool.uv.sources]
paddlepaddle-gpu = { index = "paddle" }

[[tool.uv.index]]
name = "paddle"
url = "https://www.paddlepaddle.org.cn/packages/stable/cu126/"
explicit = true

```

```bash
# uv 사용
uv add gandol2-image-ocr-v2

# pip 사용
pip install gandol2-image-ocr-v2
```

또는 소스에서 설치:

```bash
# uv 사용
uv add git+https://github.com/gandol2/gandol2-image-ocr-v2.git

# pip 사용
pip install git+https://github.com/gandol2/gandol2-image-ocr-v2.git
```

## 🖥️ 요구 사항

- Python **3.12 Ver Only** (`pyproject.toml`에 명시됨)
- (선택) NVIDIA GPU + CUDA 12.6 환경(`paddlepaddle-gpu==3.2.0`과 호환되는 환경)

## 🚚 사용법

### 1) CLI

```bash
gandol2-image-ocr --input image.png --output ./out --lang korean --device gpu
```

옵션:

- `--input` (필수): 입력 이미지 경로
- `--output` (선택): 출력 폴더 경로 (기본: 현재 폴더)
- `--lang` (선택): OCR 언어, 기본 `korean`
- `--device` (선택): `gpu` 또는 `cpu` (기본: `cpu`)

출력:

- `*_ocr.jpg`: 감지 결과가 그려진 이미지
- `*_ocr.json`: 인식 텍스트/좌표 등 JSON 결과

### 2) 파이썬 API

```python
from gandol2_image_ocr import run_ocr

# 간단 실행
result = run_ocr(
    input_image="image.png",
    output_dir="./out",
    lang="korean",
    device="cpu",  # or "gpu"
)

# result는 PaddleOCR의 predict 결과 객체 리스트입니다.
for r in result:
    r.print()
```

## 🧱 디렉터리 구조

```
gandol2-image-ocr/
├─ pyproject.toml
├─ README.md
├─ LICENSE
├─ src/
│  └─ gandol2_image_ocr/
│     ├─ __init__.py
│     ├─ ocr.py
│     └─ cli.py
├─ tests/
│  └─ test_import.py
└─ examples/
   └─ sample.py
```

## 🛠️ 개발 및 배포

### 로컬 빌드

```bash
python -m build
```

생성물:

- `dist/*.tar.gz`
- `dist/*.whl`

### TestPyPI 업로드(권장)

```bash
python -m twine upload --repository testpypi dist/*
```

### PyPI 업로드

```bash
python -m twine upload dist/*
```

> 업로드 전 `README.md` 렌더링 오류, 메타데이터 등을 `twine check dist/*`로 검증하세요.

## 🔎 참고/제약

- 이 패키지는 의존성을 **있는 그대로** 사용합니다(`paddleocr>=3.2.0`, `paddlepaddle-gpu==3.2.0`, `numpy>=2.3.3`). 환경이 맞지 않으면 설치가 실패할 수 있습니다.
- `paddlepaddle-gpu`는 CUDA, 드라이버 버전 제약이 있으므로, 공식 가이드에 따라 환경을 준비하세요.
- Windows/WSL에서 GPU 사용 시, 드라이버/WSL GPU 지원이 필요합니다.

## 📄 라이선스

MIT License
