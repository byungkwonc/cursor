# 이미지 텍스트 추출기 (OCR)

이 스크립트는 이미지에서 텍스트를 추출하여 markdown 형식으로 저장하는 도구입니다.

## 특징

- **한글 인식률이 높은 PaddleOCR 엔진** 사용
- **무료/오픈소스** 엔진으로 유료 API 불필요
- **표 인식 및 markdown 변환** 지원
- **이미지 전처리**로 인식률 향상
- **GPU 가속** 지원 (선택사항)

## 요구사항

- Python 3.7 이상
- 필요한 패키지들 (requirements_ocr.txt 참조)

## 설치 및 실행

### 1. 패키지 설치

```bash
pip install -r requirements_ocr.txt
```

또는 개별 설치:

```bash
pip install paddlepaddle paddleocr opencv-python numpy
```

### 2. 스크립트 실행

#### 방법 1: Python 직접 실행
```bash
python extract_text_from_images.py
```

#### 방법 2: Shell 스크립트 사용
```bash
chmod +x run_ocr.sh
./run_ocr.sh
```

## 사용법

1. `images/` 폴더에 텍스트를 추출할 이미지들을 넣습니다.
2. 스크립트를 실행합니다.
3. 추출된 텍스트는 `ocr/` 폴더에 markdown 형식으로 저장됩니다.

## 지원하는 이미지 형식

- PNG
- JPG/JPEG
- BMP
- TIFF/TIF

## 출력 형식

각 이미지에 대해 `{이미지명}.md` 파일이 생성됩니다:

```markdown
# 이미지명

## 표 (표가 있는 경우)
| 컬럼1 | 컬럼2 | 컬럼3 |
|-------|-------|-------|
| 데이터1 | 데이터2 | 데이터3 |

## 텍스트
추출된 일반 텍스트들...
```

## 주요 기능

### 1. 이미지 전처리
- 그레이스케일 변환
- 노이즈 제거
- 대비 향상

### 2. 표 인식
- 자동 표 구조 감지
- 행/열 정렬
- Markdown 표 형식 변환

### 3. 텍스트 추출
- 한글 최적화 모델 사용
- 신뢰도 기반 필터링
- 텍스트 방향 자동 감지

## 로그

실행 중 로그는 `logs/ocr_extraction.log` 파일에 저장됩니다.

## GPU 가속

GPU가 있는 경우 자동으로 감지하여 가속을 사용합니다.
수동으로 GPU 버전을 설치하려면:

```bash
pip install paddlepaddle-gpu paddleocr
```

## 문제 해결

### PaddleOCR 설치 오류
```bash
# CPU 버전
pip install paddlepaddle paddleocr

# GPU 버전 (CUDA 지원)
pip install paddlepaddle-gpu paddleocr
```

### 메모리 부족 오류
- 이미지 크기가 큰 경우 이미지를 리사이즈 후 사용
- 배치 크기 조정

### 한글 인식률 향상
- 이미지 품질 개선
- 적절한 해상도 유지
- 대비가 명확한 이미지 사용

## 라이선스

PaddleOCR은 Apache 2.0 라이선스 하에 배포됩니다.
