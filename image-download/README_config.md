# 설정 관리 가이드

## 개요

이미지 텍스트 추출기는 유연한 설정 관리 시스템을 제공합니다. 설정은 다음 우선순위로 적용됩니다:

1. **환경변수** (최우선)
2. **설정 파일** (config.json)
3. **기본값** (코드 내 정의)

## 설정 파일 (config.json)

기본 설정 파일은 다음과 같습니다:

```json
{
  "ocr": {
    "use_gpu": false,
    "language": "korean",
    "use_textline_orientation": true,
    "confidence_threshold_table": 0.5,
    "confidence_threshold_text": 0.3,
    "row_distance_threshold": 20
  },
  "image_processing": {
    "clip_limit": 2.0,
    "tile_grid_size": [8, 8],
    "denoise_enabled": true,
    "contrast_enhancement_enabled": true
  },
  "paths": {
    "images_dir": "images",
    "ocr_dir": "ocr",
    "logs_dir": "logs",
    "config_file": "config.json"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "log_to_file": true,
    "log_to_console": true
  }
}
```

## 환경변수

다음 환경변수들을 사용하여 설정을 오버라이드할 수 있습니다:

### OCR 설정
- `OCR_USE_GPU`: GPU 사용 여부 (true/false)
- `OCR_LANGUAGE`: OCR 언어 (korean, english, chinese 등)
- `OCR_USE_TEXTLINE_ORIENTATION`: 텍스트 방향 자동 감지 (true/false)
- `OCR_CONFIDENCE_THRESHOLD_TABLE`: 표 텍스트 신뢰도 임계값 (0.0-1.0)
- `OCR_CONFIDENCE_THRESHOLD_TEXT`: 일반 텍스트 신뢰도 임계값 (0.0-1.0)
- `OCR_ROW_DISTANCE_THRESHOLD`: 표 행 간격 임계값 (픽셀)

### 이미지 처리 설정
- `IMG_CLIP_LIMIT`: CLAHE 클립 제한값
- `IMG_DENOISE_ENABLED`: 노이즈 제거 활성화 (true/false)
- `IMG_CONTRAST_ENHANCEMENT_ENABLED`: 대비 향상 활성화 (true/false)

### 경로 설정
- `IMAGES_DIR`: 이미지 디렉토리 경로
- `OCR_DIR`: OCR 결과 디렉토리 경로
- `LOGS_DIR`: 로그 디렉토리 경로

### 로깅 설정
- `LOG_LEVEL`: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_TO_FILE`: 파일 로깅 활성화 (true/false)
- `LOG_TO_CONSOLE`: 콘솔 로깅 활성화 (true/false)

## 사용 예시

### 환경변수로 설정 오버라이드

```bash
# GPU 사용 활성화
export OCR_USE_GPU=true

# 신뢰도 임계값 조정
export OCR_CONFIDENCE_THRESHOLD_TEXT=0.4

# 로그 레벨 변경
export LOG_LEVEL=DEBUG

# 스크립트 실행
python extract_text_from_images.py
```

### 설정 파일 수정

```bash
# 설정 파일 편집
nano config.json

# 또는 샘플 설정 파일 생성
python -c "from config import config_manager; config_manager.create_sample_config()"
```

### Docker 환경에서 사용

```dockerfile
# Dockerfile
FROM python:3.9

# 환경변수 설정
ENV OCR_USE_GPU=false
ENV OCR_LANGUAGE=korean
ENV LOG_LEVEL=INFO

# 애플리케이션 복사 및 실행
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "extract_text_from_images.py"]
```

## 설정 검증

설정이 올바르게 로드되었는지 확인하려면:

```python
from config import config_manager

config = config_manager.get_config()
print(f"OCR 언어: {config.ocr.language}")
print(f"GPU 사용: {config.ocr.use_gpu}")
print(f"이미지 디렉토리: {config.paths.images_dir}")
```

## 주의사항

1. **타입 변환**: 환경변수는 문자열로 전달되므로 적절한 타입 변환이 필요합니다.
2. **유효성 검사**: 설정값의 유효성은 런타임에 검사됩니다.
3. **기본값**: 잘못된 설정값이 제공되면 기본값이 사용됩니다.
4. **로그**: 설정 로드 과정은 로그에 기록됩니다.