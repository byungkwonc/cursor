#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
설정 관리 모듈
환경변수, 설정 파일, 기본값을 통합 관리
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class OCRConfig:
    """OCR 관련 설정"""
    use_gpu: bool = False
    language: str = 'korean'
    use_textline_orientation: bool = True
    confidence_threshold_table: float = 0.5
    confidence_threshold_text: float = 0.3
    row_distance_threshold: int = 20


@dataclass
class ImageProcessingConfig:
    """이미지 처리 관련 설정"""
    clip_limit: float = 2.0
    tile_grid_size: tuple = (8, 8)
    denoise_enabled: bool = True
    contrast_enhancement_enabled: bool = True


@dataclass
class PathConfig:
    """경로 관련 설정"""
    images_dir: str = "images"
    ocr_dir: str = "ocr"
    logs_dir: str = "logs"
    config_file: str = "config.json"


@dataclass
class LoggingConfig:
    """로깅 관련 설정"""
    level: str = "INFO"
    format: str = '%(asctime)s - %(levelname)s - %(message)s'
    log_to_file: bool = True
    log_to_console: bool = True


@dataclass
class AppConfig:
    """전체 애플리케이션 설정"""
    ocr: OCRConfig = field(default_factory=OCRConfig)
    image_processing: ImageProcessingConfig = field(default_factory=ImageProcessingConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # 지원하는 이미지 확장자
    supported_image_extensions: List[str] = field(
        default_factory=lambda: ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
    )


class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        설정 관리자 초기화
        
        Args:
            config_file_path: 설정 파일 경로 (선택사항)
        """
        self.config_file_path = config_file_path or "config.json"
        self._config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """설정 로드 (환경변수 > 설정파일 > 기본값 순서)"""
        # 기본 설정으로 시작
        config = AppConfig()
        
        # 설정 파일에서 로드
        config = self._load_from_file(config)
        
        # 환경변수에서 오버라이드
        config = self._load_from_env(config)
        
        return config
    
    def _load_from_file(self, config: AppConfig) -> AppConfig:
        """설정 파일에서 로드"""
        config_path = Path(self.config_file_path)
        
        if not config_path.exists():
            logger.info(f"설정 파일이 없습니다: {config_path}. 기본 설정을 사용합니다.")
            return config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # OCR 설정
            if 'ocr' in file_config:
                ocr_config = file_config['ocr']
                config.ocr.use_gpu = ocr_config.get('use_gpu', config.ocr.use_gpu)
                config.ocr.language = ocr_config.get('language', config.ocr.language)
                config.ocr.use_textline_orientation = ocr_config.get('use_textline_orientation', config.ocr.use_textline_orientation)
                config.ocr.confidence_threshold_table = ocr_config.get('confidence_threshold_table', config.ocr.confidence_threshold_table)
                config.ocr.confidence_threshold_text = ocr_config.get('confidence_threshold_text', config.ocr.confidence_threshold_text)
                config.ocr.row_distance_threshold = ocr_config.get('row_distance_threshold', config.ocr.row_distance_threshold)
            
            # 이미지 처리 설정
            if 'image_processing' in file_config:
                img_config = file_config['image_processing']
                config.image_processing.clip_limit = img_config.get('clip_limit', config.image_processing.clip_limit)
                config.image_processing.tile_grid_size = tuple(img_config.get('tile_grid_size', config.image_processing.tile_grid_size))
                config.image_processing.denoise_enabled = img_config.get('denoise_enabled', config.image_processing.denoise_enabled)
                config.image_processing.contrast_enhancement_enabled = img_config.get('contrast_enhancement_enabled', config.image_processing.contrast_enhancement_enabled)
            
            # 경로 설정
            if 'paths' in file_config:
                path_config = file_config['paths']
                config.paths.images_dir = path_config.get('images_dir', config.paths.images_dir)
                config.paths.ocr_dir = path_config.get('ocr_dir', config.paths.ocr_dir)
                config.paths.logs_dir = path_config.get('logs_dir', config.paths.logs_dir)
                config.paths.config_file = path_config.get('config_file', config.paths.config_file)
            
            # 로깅 설정
            if 'logging' in file_config:
                log_config = file_config['logging']
                config.logging.level = log_config.get('level', config.logging.level)
                config.logging.format = log_config.get('format', config.logging.format)
                config.logging.log_to_file = log_config.get('log_to_file', config.logging.log_to_file)
                config.logging.log_to_console = log_config.get('log_to_console', config.logging.log_to_console)
            
            logger.info(f"설정 파일에서 로드됨: {config_path}")
            
        except Exception as e:
            logger.warning(f"설정 파일 로드 실패: {e}. 기본 설정을 사용합니다.")
        
        return config
    
    def _load_from_env(self, config: AppConfig) -> AppConfig:
        """환경변수에서 설정 오버라이드"""
        # OCR 설정
        config.ocr.use_gpu = self._get_bool_env('OCR_USE_GPU', config.ocr.use_gpu)
        config.ocr.language = os.getenv('OCR_LANGUAGE', config.ocr.language)
        config.ocr.use_textline_orientation = self._get_bool_env('OCR_USE_TEXTLINE_ORIENTATION', config.ocr.use_textline_orientation)
        config.ocr.confidence_threshold_table = self._get_float_env('OCR_CONFIDENCE_THRESHOLD_TABLE', config.ocr.confidence_threshold_table)
        config.ocr.confidence_threshold_text = self._get_float_env('OCR_CONFIDENCE_THRESHOLD_TEXT', config.ocr.confidence_threshold_text)
        config.ocr.row_distance_threshold = self._get_int_env('OCR_ROW_DISTANCE_THRESHOLD', config.ocr.row_distance_threshold)
        
        # 이미지 처리 설정
        config.image_processing.clip_limit = self._get_float_env('IMG_CLIP_LIMIT', config.image_processing.clip_limit)
        config.image_processing.denoise_enabled = self._get_bool_env('IMG_DENOISE_ENABLED', config.image_processing.denoise_enabled)
        config.image_processing.contrast_enhancement_enabled = self._get_bool_env('IMG_CONTRAST_ENHANCEMENT_ENABLED', config.image_processing.contrast_enhancement_enabled)
        
        # 경로 설정
        config.paths.images_dir = os.getenv('IMAGES_DIR', config.paths.images_dir)
        config.paths.ocr_dir = os.getenv('OCR_DIR', config.paths.ocr_dir)
        config.paths.logs_dir = os.getenv('LOGS_DIR', config.paths.logs_dir)
        
        # 로깅 설정
        config.logging.level = os.getenv('LOG_LEVEL', config.logging.level)
        config.logging.log_to_file = self._get_bool_env('LOG_TO_FILE', config.logging.log_to_file)
        config.logging.log_to_console = self._get_bool_env('LOG_TO_CONSOLE', config.logging.log_to_console)
        
        return config
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """환경변수에서 boolean 값 가져오기"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def _get_int_env(self, key: str, default: int) -> int:
        """환경변수에서 int 값 가져오기"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"환경변수 {key}의 값 '{value}'을 int로 변환할 수 없습니다. 기본값 {default}를 사용합니다.")
            return default
    
    def _get_float_env(self, key: str, default: float) -> float:
        """환경변수에서 float 값 가져오기"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            logger.warning(f"환경변수 {key}의 값 '{value}'을 float로 변환할 수 없습니다. 기본값 {default}를 사용합니다.")
            return default
    
    def get_config(self) -> AppConfig:
        """현재 설정 반환"""
        return self._config
    
    def save_config(self, config: Optional[AppConfig] = None) -> None:
        """설정을 파일로 저장"""
        config_to_save = config or self._config
        config_path = Path(self.config_file_path)
        
        try:
            # dataclass를 dict로 변환
            config_dict = {
                'ocr': {
                    'use_gpu': config_to_save.ocr.use_gpu,
                    'language': config_to_save.ocr.language,
                    'use_textline_orientation': config_to_save.ocr.use_textline_orientation,
                    'confidence_threshold_table': config_to_save.ocr.confidence_threshold_table,
                    'confidence_threshold_text': config_to_save.ocr.confidence_threshold_text,
                    'row_distance_threshold': config_to_save.ocr.row_distance_threshold,
                },
                'image_processing': {
                    'clip_limit': config_to_save.image_processing.clip_limit,
                    'tile_grid_size': list(config_to_save.image_processing.tile_grid_size),
                    'denoise_enabled': config_to_save.image_processing.denoise_enabled,
                    'contrast_enhancement_enabled': config_to_save.image_processing.contrast_enhancement_enabled,
                },
                'paths': {
                    'images_dir': config_to_save.paths.images_dir,
                    'ocr_dir': config_to_save.paths.ocr_dir,
                    'logs_dir': config_to_save.paths.logs_dir,
                    'config_file': config_to_save.paths.config_file,
                },
                'logging': {
                    'level': config_to_save.logging.level,
                    'format': config_to_save.logging.format,
                    'log_to_file': config_to_save.logging.log_to_file,
                    'log_to_console': config_to_save.logging.log_to_console,
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"설정이 저장되었습니다: {config_path}")
            
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
    
    def create_sample_config(self) -> None:
        """샘플 설정 파일 생성"""
        sample_config = AppConfig()
        self.save_config(sample_config)
        logger.info(f"샘플 설정 파일이 생성되었습니다: {self.config_file_path}")


# 전역 설정 관리자 인스턴스
config_manager = ConfigManager()