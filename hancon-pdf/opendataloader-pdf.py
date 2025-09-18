# pip install -U opendataloader-pdf

import argparse
import os
import opendataloader_pdf


def main():
    parser = argparse.ArgumentParser(description="Run opendataloader-pdf with selectable input path")
    parser.add_argument("input_path", nargs="?", help="Path to input PDF file")
    parser.add_argument("-o", dest="output_folder", default="./", help="Output folder (default: ./)")
    parser.add_argument("-no-md", dest="generate_markdown", action="store_false", help="Disable markdown generation")
    parser.add_argument("-no-html", dest="generate_html", action="store_false", help="Disable html generation")
    parser.add_argument("-no-pdf", dest="generate_annotated_pdf", action="store_false", help="Disable annotated PDF generation")
    args = parser.parse_args()

    input_path = args.input_path
    if not input_path:
        try:
            input_path = input("input-path를 입력하세요 (예: file.pdf): ")
        except EOFError:
            input_path = None

    if not input_path:
        print("오류: 입력 파일 경로가 필요합니다.")
        return

    if not os.path.isfile(input_path):
        print(f"오류: 파일을 찾을 수 없습니다: {input_path}")
        return

    opendataloader_pdf.run(
        input_path=input_path,
        output_folder=args.output_folder,
        generate_markdown=args.generate_markdown,
        generate_html=args.generate_html,
        generate_annotated_pdf=args.generate_annotated_pdf,
    )


if __name__ == "__main__":
    main()