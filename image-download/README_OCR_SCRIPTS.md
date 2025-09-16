# OCR 이미지 처리 스크립트 가이드

이 프로젝트는 이미지에서 텍스트를 추출하여 마크다운 형식으로 변환하는 Python 스크립트들을 포함합니다.

## 📁 파일 구조

```
image-download/
├── images/                    # 처리할 이미지 파일들
├── ocr/                      # OCR 결과 마크다운 파일들
├── process_single_image.py   # 단일 이미지 처리 스크립트
├── process_all_images.py     # 모든 이미지 배치 처리 스크립트
├── extract_text_from_images.py  # 기존 OCR 스크립트
└── README_OCR_SCRIPTS.md     # 이 파일
```

## 🚀 스크립트 개요

### 1. process_single_image.py
- **목적**: 단일 이미지에서 텍스트를 추출하여 마크다운으로 변환
- **사용법**: 명령행에서 특정 이미지 파일명을 지정하여 실행
- **출력**: `ocr/` 폴더에 마크다운 파일 생성

### 2. process_all_images.py
- **목적**: `images/` 폴더의 모든 이미지를 순차적으로 처리
- **사용법**: 명령행에서 실행하면 모든 이미지를 자동으로 처리
- **출력**: 각 이미지별로 `ocr/` 폴더에 마크다운 파일 생성

## 📋 사전 요구사항

### Python 패키지 설치
```bash
pip install paddlepaddle paddleocr opencv-python numpy
```

### 가상환경 사용 (권장)
```bash
# 가상환경 생성
python -m venv venv-image-download

# 가상환경 활성화
# Windows
venv-image-download\Scripts\activate
# macOS/Linux
source venv-image-download/bin/activate

# 패키지 설치
pip install -r requirements_ocr.txt
```

## 🔧 사용법

### 단일 이미지 처리

```bash
python process_single_image.py <이미지파일명>
```

**예시:**
```bash
python process_single_image.py 1fa7af9dea9e1.png
```

**결과:**
- `ocr/1fa7af9dea9e1.md` 파일이 생성됩니다.

### 모든 이미지 배치 처리

```bash
python process_all_images.py
```

**결과:**
- `images/` 폴더의 모든 이미지가 순차적으로 처리됩니다.
- 각 이미지별로 `ocr/` 폴더에 마크다운 파일이 생성됩니다.

## 📊 지원 이미지 형식

- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## 🎯 주요 기능

### 이미지 전처리
- 그레이스케일 변환
- 노이즈 제거
- 대비 향상 (CLAHE)

### OCR 처리
- PaddleOCR 엔진 사용
- 한국어 모델 적용
- 텍스트 방향 자동 감지

### 텍스트 필터링
- 신뢰도 30% 이상인 텍스트만 추출
- 빈 텍스트 제거
- 중복 텍스트 정리

### 마크다운 변환
- 체계적인 헤딩 구조
- 깔끔한 포맷팅
- UTF-8 인코딩 지원

## 📝 출력 형식

### 마크다운 파일 구조
```markdown
# 이미지파일명

추출된 텍스트 내용...

## 섹션 제목

더 많은 텍스트 내용...
```

### 파일명 규칙
- 입력: `1fa7af9dea9e1.png`
- 출력: `1fa7af9dea9e1.md`

## ⚙️ 설정 옵션

### process_single_image.py 설정
```python
# 신뢰도 임계값 조정
if confidence > 0.3:  # 기본값: 0.3 (30%)

# 이미지 전처리 파라미터
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
```

### process_all_images.py 설정
```python
# 처리 간격 조정
time.sleep(1)  # 기본값: 1초

# 로그 레벨 조정
logging.basicConfig(level=logging.INFO)
```

## 🐛 문제 해결

### 일반적인 오류

#### 1. PaddleOCR 설치 오류
```bash
# 해결방법
pip install paddlepaddle paddleocr
```

#### 2. 이미지 파일을 찾을 수 없음
```bash
# 확인사항
ls images/
# 이미지 파일이 images/ 폴더에 있는지 확인
```

#### 3. 메모리 부족 오류
```bash
# 해결방법: 이미지 크기 줄이기 또는 배치 크기 조정
```

#### 4. 인코딩 오류
```bash
# 해결방법: UTF-8 인코딩 확인
export PYTHONIOENCODING=utf-8
```

### 로그 확인
```bash
# 상세한 로그 확인
python process_single_image.py image.png 2>&1 | tee log.txt
```

## 📈 성능 최적화

### 처리 속도 향상
1. **GPU 사용** (가능한 경우)
   ```python
   # GPU 사용 설정
   use_gpu = True
   ```

2. **이미지 크기 최적화**
   ```python
   # 이미지 리사이즈
   image = cv2.resize(image, (width, height))
   ```

3. **배치 처리**
   ```python
   # 여러 이미지 동시 처리
   ```

### 메모리 사용량 최적화
1. **이미지 전처리 최적화**
2. **불필요한 변수 제거**
3. **가비지 컬렉션 활용**

## 🔄 스크립트 확장

### 새로운 기능 추가
```python
class SingleImageProcessor:
    def __init__(self):
        # 새로운 설정 추가
        self.custom_setting = True

    def custom_preprocessing(self, image):
        # 커스텀 전처리 로직
        pass
```

### 다른 OCR 엔진 사용
```python
# Tesseract 사용 예시
import pytesseract
text = pytesseract.image_to_string(image, lang='kor+eng')
```

## 📚 참고 자료

- [PaddleOCR 공식 문서](https://github.com/PaddlePaddle/PaddleOCR)
- [OpenCV Python 튜토리얼](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [마크다운 가이드](https://www.markdownguide.org/)

## 🤝 기여하기

1. 이슈 리포트
2. 기능 요청
3. 코드 개선 제안
4. 문서 개선

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

문제가 있거나 질문이 있으시면 이슈를 생성해주세요.

---

**마지막 업데이트**: 2024년 12월
