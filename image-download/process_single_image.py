#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단일 이미지에서 텍스트를 추출하여 markdown 형식으로 저장하는 스크립트

"""

import os
import sys
from pathlib import Path
import time
import subprocess
import logging

# PaddleOCR 설치 확인 및 설치 안내
try:
    from paddleocr import PaddleOCR
except ImportError:
    print("PaddleOCR이 설치되지 않았습니다.")
    print("다음 명령어로 설치해주세요:")
    print("pip install paddlepaddle paddleocr")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SingleImageProcessor:
    def __init__(self):
        """단일 이미지 처리기 초기화"""
        self.ocr = PaddleOCR(
            use_textline_orientation=True,
            lang='korean'
        )

        self.script_dir = Path(__file__).parent
        self.images_dir = self.script_dir / "images"
        self.ocr_dir = self.script_dir / "ocr"

        # OCR 결과 디렉토리 생성
        self.ocr_dir.mkdir(exist_ok=True)

    def preprocess_image(self, image_path: Path) -> np.ndarray:
        """이미지 전처리"""
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")

        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 노이즈 제거
        denoised = cv2.fastNlMeansDenoising(gray)

        # 대비 향상
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        return enhanced

    def extract_text_from_image(self, image_path: Path) -> str:
        """이미지에서 텍스트 추출"""
        try:
            logger.info(f"텍스트 추출 중: {image_path.name}")

            # 이미지 전처리
            processed_image = self.preprocess_image(image_path)

            # OCR 실행
            ocr_result = self.ocr.predict(processed_image)

            if not ocr_result:
                logger.warning(f"텍스트를 찾을 수 없습니다: {image_path.name}")
                return f"# {image_path.stem}\n\n텍스트를 찾을 수 없습니다.\n"

            # markdown 형식으로 변환
            markdown_content = f"# {image_path.stem}\n\n"

            # 텍스트 추출
            text_lines = []
            for item in ocr_result:
                if item.get('text'):
                    text = item['text']
                    confidence = item['confidence']
                    if confidence > 0.3:  # 신뢰도가 30% 이상인 텍스트만
                        text_lines.append(text)

            if text_lines:
                markdown_content += "\n".join(text_lines) + "\n"
            else:
                markdown_content += "텍스트를 찾을 수 없습니다.\n"

            return markdown_content

        except Exception as e:
            logger.error(f"텍스트 추출 중 오류 발생: {image_path.name} - {str(e)}")
            return f"# {image_path.stem}\n\n텍스트 추출 중 오류가 발생했습니다: {str(e)}\n"

    def process_image(self, image_filename: str) -> None:
        """단일 이미지 처리"""
        image_path = self.images_dir / image_filename

        if not image_path.exists():
            logger.error(f"이미지 파일을 찾을 수 없습니다: {image_filename}")
            return

        try:
            # 텍스트 추출
            markdown_content = self.extract_text_from_image(image_path)

            # markdown 파일로 저장
            output_path = self.ocr_dir / f"{image_path.stem}.md"

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"완료: {image_path.name} -> {output_path.name}")

        except Exception as e:

            logger.error(f"처리 중 오류 발생: {image_path.name} - {str(e)}")

def main():

    """시스템 기동"""
    if len(sys.argv) != 2:
        print("사용법: python process_single_image.py <이미지파일명>")
        print("예시: python process_single_image.py 1fa7af9dea9e1.png")
        sys.exit(1)

    image_filename = sys.argv[1]

    print(f"이미지 처리 시작: {image_filename}")

    # 이미지 처리기 초기화
    processor = SingleImageProcessor()

    # 이미지 처리
    processor.process_image(image_filename)

    print("처리 완료!")

if __name__ == "__main__":
    main()
