# CLI 진입점
import argparse
from .ocr import run_ocr

def main():
    parser = argparse.ArgumentParser(description="PaddleOCR 기반 이미지 OCR")
    parser.add_argument("--input", required=True, help="입력 이미지 경로")
    parser.add_argument("--output", default=".", help="출력 폴더 경로")
    parser.add_argument("--lang", default="korean", help="OCR 언어 (기본: korean)")
    parser.add_argument("--device", default="cpu", choices=["cpu", "gpu"], help="장치 선택 (cpu/gpu)")
    args = parser.parse_args()

    run_ocr(
        input_image=args.input,
        output_dir=args.output,
        lang=args.lang,
        device=args.device,
    )

if __name__ == "__main__":
    main()
