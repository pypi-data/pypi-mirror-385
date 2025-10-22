# PaddleOCR 실행 모듈
from typing import List
from paddleocr import PaddleOCR
import paddle
import os


def run_ocr(
    input_image: str,
    output_dir: str = ".",
    lang: str = "korean",
    device: str = "cpu",  # "gpu" or "cpu"
    debug_verbose=True,
):
    """이미지 한 장을 OCR하여 주석 이미지와 JSON을 저장.

    Args:
        input_image: 입력 이미지 경로
        output_dir: 출력 폴더
        lang: 언어 (예: "korean")
        device: "cpu" 또는 "gpu"

    Returns:
        PaddleOCR.predict(...) 결과 리스트
    """
    if device not in {"cpu", "gpu"}:
        raise ValueError("device는 'cpu' 또는 'gpu'여야 합니다.")

    if device == "gpu":
        paddle.set_device("gpu")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # GPU/CPU 선택은 paddle 내부 설정에 의해 이루어지며,
    # 사용자는 환경이 준비된 상태여야 합니다.
    ocr = PaddleOCR(
        lang=lang,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    result = ocr.predict(input=input_image)
    for res in result:
        if debug_verbose:
            res.print()
        res.save_to_img(output_dir)
        res.save_to_json(output_dir)
    return result
