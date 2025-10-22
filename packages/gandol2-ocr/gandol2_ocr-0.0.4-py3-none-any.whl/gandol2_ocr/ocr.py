"""
OCR 모듈 - 최상위 레벨에서 접근 가능하도록 re-export
"""

from .image_ocr.ocr import run_ocr

__all__ = ["run_ocr"]
