#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이미지에서 텍스트를 추출하여 markdown 형식으로 저장하는 스크립트
한글 인식률이 높은 PaddleOCR 엔진 사용
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import re
from typing import List, Dict, Tuple, Optional
import logging

# 설정 관리 모듈 임포트
from config import config_manager, AppConfig

# PaddleOCR 설치 확인 및 설치 안내
try:
    from paddleocr import PaddleOCR
except ImportError:
    print("PaddleOCR이 설치되지 않았습니다.")
    print("다음 명령어로 설치해주세요:")
    print("pip install paddlepaddle paddleocr")
    print("또는")
    print("pip install paddlepaddle-gpu paddleocr")  # GPU 사용시
    sys.exit(1)

# 설정 로드
config = config_manager.get_config()

# 로깅 설정
def setup_logging(config: AppConfig) -> None:
    """로깅 설정 초기화"""
    # logs 디렉토리 생성
    logs_dir = Path(__file__).parent / config.paths.logs_dir
    logs_dir.mkdir(exist_ok=True)
    
    # 로깅 레벨 설정
    log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
    
    # 핸들러 설정
    handlers = []
    
    if config.logging.log_to_file:
        handlers.append(
            logging.FileHandler(logs_dir / 'ocr_extraction.log', encoding='utf-8')
        )
    
    if config.logging.log_to_console:
        handlers.append(logging.StreamHandler())
    
    logging.basicConfig(
        level=log_level,
        format=config.logging.format,
        handlers=handlers
    )

# 로깅 설정 적용
setup_logging(config)
logger = logging.getLogger(__name__)

class ImageTextExtractor:
    def __init__(self, config: AppConfig):
        """
        이미지 텍스트 추출기 초기화

        Args:
            config: 애플리케이션 설정
        """
        self.config = config
        
        # OCR 엔진 초기화
        self.ocr = PaddleOCR(
            use_textline_orientation=config.ocr.use_textline_orientation,
            lang=config.ocr.language
        )

        # 현재 스크립트 디렉토리
        self.script_dir = Path(__file__).parent
        self.images_dir = self.script_dir / config.paths.images_dir
        self.ocr_dir = self.script_dir / config.paths.ocr_dir

        # OCR 결과 디렉토리 생성
        self.ocr_dir.mkdir(exist_ok=True)

        logger.info(f"이미지 디렉토리: {self.images_dir}")
        logger.info(f"OCR 결과 디렉토리: {self.ocr_dir}")
        logger.info(f"OCR 언어: {config.ocr.language}")
        logger.info(f"GPU 사용: {config.ocr.use_gpu}")

    def preprocess_image(self, image_path: Path) -> np.ndarray:
        """
        이미지 전처리

        Args:
            image_path: 이미지 파일 경로

        Returns:
            전처리된 이미지 배열
        """
        # 이미지 읽기
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")

        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 노이즈 제거 (설정에 따라)
        if self.config.image_processing.denoise_enabled:
            denoised = cv2.fastNlMeansDenoising(gray)
        else:
            denoised = gray

        # 대비 향상 (설정에 따라)
        if self.config.image_processing.contrast_enhancement_enabled:
            clahe = cv2.createCLAHE(
                clipLimit=self.config.image_processing.clip_limit, 
                tileGridSize=self.config.image_processing.tile_grid_size
            )
            enhanced = clahe.apply(denoised)
        else:
            enhanced = denoised

        return enhanced

    def detect_table_structure(self, ocr_result: List) -> Dict:
        """
        OCR 결과에서 표 구조 감지

        Args:
            ocr_result: PaddleOCR 결과

        Returns:
            표 구조 정보
        """
        if not ocr_result:
            return {"is_table": False, "rows": []}

        # 텍스트 박스들의 y좌표를 기준으로 그룹화
        y_coordinates = []
        for item in ocr_result:
            if item.get('text'):  # 텍스트가 있는 경우
                box = item['bbox']
                y_center = sum(point[1] for point in box) / 4
                y_coordinates.append(y_center)

        if not y_coordinates:
            return {"is_table": False, "rows": []}

        # y좌표를 정렬하여 행 구분
        y_coordinates.sort()

        # 행 간격 분석
        row_groups = []
        current_group = [y_coordinates[0]]

        for y in y_coordinates[1:]:
            if y - current_group[-1] < self.config.ocr.row_distance_threshold:  # 설정된 픽셀 이내면 같은 행
                current_group.append(y)
            else:
                row_groups.append(current_group)
                current_group = [y]

        row_groups.append(current_group)

        # 표 여부 판단 (2행 이상이고 일정한 간격을 가진 경우)
        is_table = len(row_groups) >= 2

        return {
            "is_table": is_table,
            "rows": row_groups
        }

    def format_table_markdown(self, ocr_result: List, table_info: Dict) -> str:
        """
        표를 markdown 형식으로 변환

        Args:
            ocr_result: PaddleOCR 결과
            table_info: 표 구조 정보

        Returns:
            markdown 형식의 표
        """
        if not table_info["is_table"]:
            return ""

        # 각 텍스트를 y좌표 기준으로 그룹화
        text_by_row = {}

        for item in ocr_result:
            if item.get('text'):  # 텍스트가 있는 경우
                text = item['text']
                confidence = item['confidence']
                box = item['bbox']
                y_center = sum(point[1] for point in box) / 4
                x_center = sum(point[0] for point in box) / 4

                # 가장 가까운 행 찾기
                min_distance = float('inf')
                closest_row = 0

                for i, row_y_coords in enumerate(table_info["rows"]):
                    row_y_avg = sum(row_y_coords) / len(row_y_coords)
                    distance = abs(y_center - row_y_avg)
                    if distance < min_distance:
                        min_distance = distance
                        closest_row = i

                if closest_row not in text_by_row:
                    text_by_row[closest_row] = []

                text_by_row[closest_row].append((x_center, text, confidence))

        # 각 행의 텍스트를 x좌표 순으로 정렬
        for row in text_by_row:
            text_by_row[row].sort(key=lambda x: x[0])

        # markdown 표 생성
        markdown_table = ""

        # 헤더 행
        if 0 in text_by_row:
            header_cells = [item[1] for item in text_by_row[0]]
            markdown_table += "| " + " | ".join(header_cells) + " |\n"
            markdown_table += "| " + " | ".join(["---"] * len(header_cells)) + " |\n"

        # 데이터 행들
        for row_idx in sorted(text_by_row.keys()):
            if row_idx == 0:  # 헤더는 이미 처리됨
                continue

            cells = [item[1] for item in text_by_row[row_idx]]
            markdown_table += "| " + " | ".join(cells) + " |\n"

        return markdown_table

    def extract_text_from_image(self, image_path: Path) -> str:
        """
        이미지에서 텍스트 추출

        Args:
            image_path: 이미지 파일 경로

        Returns:
            추출된 텍스트 (markdown 형식)
        """
        try:
            logger.info(f"텍스트 추출 중: {image_path.name}")

            # 이미지 전처리
            processed_image = self.preprocess_image(image_path)

            # OCR 실행 (최신 predict 메서드 사용)
            ocr_result = self.ocr.predict(processed_image)

            if not ocr_result:
                logger.warning(f"텍스트를 찾을 수 없습니다: {image_path.name}")
                return f"# {image_path.stem}\n\n텍스트를 찾을 수 없습니다.\n"

            # 표 구조 감지
            table_info = self.detect_table_structure(ocr_result)

            # markdown 형식으로 변환
            markdown_content = f"# {image_path.stem}\n\n"

            if table_info["is_table"]:
                # 표가 있는 경우
                table_markdown = self.format_table_markdown(ocr_result, table_info)
                if table_markdown:
                    markdown_content += "## 표\n\n"
                    markdown_content += table_markdown + "\n"

                # 표 외 텍스트도 추가
                regular_text = []
                for item in ocr_result:
                    if item.get('text'):  # 텍스트가 있는 경우
                        text = item['text']
                        confidence = item['confidence']
                        if confidence > self.config.ocr.confidence_threshold_table:  # 설정된 신뢰도 이상인 텍스트만
                            regular_text.append(text)

                if regular_text:
                    markdown_content += "## 텍스트\n\n"
                    markdown_content += "\n".join(regular_text) + "\n"
            else:
                # 일반 텍스트인 경우
                text_lines = []
                for item in ocr_result:
                    if item.get('text'):  # 텍스트가 있는 경우
                        text = item['text']
                        confidence = item['confidence']
                        if confidence > self.config.ocr.confidence_threshold_text:  # 설정된 신뢰도 이상인 텍스트만
                            text_lines.append(text)

                if text_lines:
                    markdown_content += "\n".join(text_lines) + "\n"
                else:
                    markdown_content += "텍스트를 찾을 수 없습니다.\n"

            return markdown_content

        except Exception as e:
            logger.error(f"텍스트 추출 중 오류 발생: {image_path.name} - {str(e)}")
            return f"# {image_path.stem}\n\n텍스트 추출 중 오류가 발생했습니다: {str(e)}\n"

    def process_all_images(self) -> None:
        """
        images 폴더의 모든 이미지에서 텍스트 추출
        """
        # 지원하는 이미지 확장자 (설정에서 가져오기)
        image_extensions = set(self.config.supported_image_extensions)

        # 이미지 파일들 찾기
        image_files = []
        for ext in image_extensions:
            image_files.extend(self.images_dir.glob(f"*{ext}"))
            image_files.extend(self.images_dir.glob(f"*{ext.upper()}"))

        if not image_files:
            logger.warning("처리할 이미지 파일을 찾을 수 없습니다.")
            return

        logger.info(f"총 {len(image_files)}개의 이미지 파일을 처리합니다.")

        # 각 이미지 처리
        for image_path in sorted(image_files):
            try:
                # 텍스트 추출
                markdown_content = self.extract_text_from_image(image_path)

                # markdown 파일로 저장
                output_path = self.ocr_dir / f"{image_path.stem}.md"

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)

                logger.info(f"완료: {image_path.name} -> {output_path.name}")

            except Exception as e:
                logger.error(f"처리 실패: {image_path.name} - {str(e)}")

        logger.info("모든 이미지 처리 완료!")

def main():
    """메인 함수"""
    print("이미지 텍스트 추출기 시작...")
    print("한글 인식률이 높은 PaddleOCR 엔진을 사용합니다.")

    # GPU 사용 가능 여부 확인 및 설정 업데이트
    try:
        import paddle
        if paddle.is_compiled_with_cuda():
            config.ocr.use_gpu = True
            print("GPU 가속을 사용합니다.")
        else:
            config.ocr.use_gpu = False
            print("CPU 모드로 실행합니다.")
    except:
        config.ocr.use_gpu = False
        print("CPU 모드로 실행합니다.")

    # 설정 정보 출력
    print(f"OCR 언어: {config.ocr.language}")
    print(f"이미지 디렉토리: {config.paths.images_dir}")
    print(f"결과 디렉토리: {config.paths.ocr_dir}")
    print(f"로그 레벨: {config.logging.level}")

    # 텍스트 추출기 초기화
    extractor = ImageTextExtractor(config)

    # 모든 이미지 처리
    extractor.process_all_images()

    print("텍스트 추출 완료!")
    print(f"결과는 {extractor.ocr_dir} 폴더에 저장되었습니다.")

if __name__ == "__main__":
    main()
