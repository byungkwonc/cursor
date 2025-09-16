#!/bin/bash

# OCR 텍스트 추출 스크립트 실행

echo "=== 이미지 텍스트 추출기 ==="
echo "한글 인식률이 높은 PaddleOCR 엔진을 사용합니다."
echo ""

# Python 가상환경 확인 및 활성화
echo "Python 가상환경 확인..."

# 기존 가상환경이 있는지 확인
if [ -d "venv-image-download" ]; then
    echo "기존 가상환경을 활성화합니다..."
    source venv-image-download/bin/activate
else
    echo "새로운 가상환경을 생성합니다..."
    python3 -m venv ./venv-image-download
    source venv-image-download/bin/activate
fi

# 필요한 패키지 설치 확인
echo "필요한 패키지들을 설치합니다..."
pip install -r requirements_ocr.txt

# OCR 스크립트 실행
echo ""
echo "텍스트 추출을 시작합니다..."
python extract_text_from_images.py

echo ""
echo "완료! 결과는 ocr/ 폴더에 저장되었습니다."

# Python 가상환경 종료
echo "Python 가상환경 종료..."
deactivate

echo ""
echo "가상환경을 유지합니다. 삭제하려면 다음 명령어를 실행하세요:"
echo "rm -rf venv-image-download/"
