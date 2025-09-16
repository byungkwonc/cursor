#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 이미지를 순차적으로 처리하는 배치 스크립트
"""

import os
import sys
import time
from pathlib import Path
import subprocess

def get_image_files():
    """images 폴더에서 모든 이미지 파일 목록을 가져옴"""
    images_dir = Path(__file__).parent / "images"
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}

    image_files = []
    for ext in image_extensions:
        image_files.extend(images_dir.glob(f"*{ext}"))
        image_files.extend(images_dir.glob(f"*{ext.upper()}"))

    return sorted(image_files)

def process_all_images():
    """모든 이미지를 순차적으로 처리"""
    image_files = get_image_files()

    if not image_files:
        print("처리할 이미지 파일을 찾을 수 없습니다.")
        return

    print(f"총 {len(image_files)}개의 이미지 파일을 처리합니다.")
    print("=" * 50)

    for i, image_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] 처리 중: {image_path.name}")
        print("-" * 30)

        try:
            # 단일 이미지 처리 스크립트 실행
            result = subprocess.run([
                sys.executable,
                "process_single_image.py",
                image_path.name
            ], capture_output=True, text=True, encoding='utf-8')

            if result.returncode == 0:
                print(f"✅ 완료: {image_path.name}")
                if result.stdout:
                    print(result.stdout.strip())
            else:
                print(f"❌ 실패: {image_path.name}")
                if result.stderr:
                    print(f"오류: {result.stderr.strip()}")

        except Exception as e:
            print(f"❌ 처리 중 오류 발생: {image_path.name} - {str(e)}")

        # 다음 이미지 처리 전 잠시 대기
        if i < len(image_files):
            print("다음 이미지 처리 준비 중...")
            time.sleep(1)

    print("\n" + "=" * 50)
    print("모든 이미지 처리 완료!")
    print(f"결과는 ocr 폴더에 저장되었습니다.")

def main():
    """메인 함수"""
    print("이미지 배치 처리기 시작...")

    # process_single_image.py 파일이 있는지 확인
    single_processor = Path(__file__).parent / "process_single_image.py"
    if not single_processor.exists():
        print("process_single_image.py 파일을 찾을 수 없습니다.")
        sys.exit(1)

    # 모든 이미지 처리
    process_all_images()

if __name__ == "__main__":
    main()
