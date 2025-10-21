"""
gandol2-ocr: 이미지 섹션 분리와 OCR을 통합한 Python 유틸리티

세로로 긴 상세페이지 이미지를 시각적 경계 기준으로 안전하게 섹션 분리하고,
각 섹션에 대해 OCR을 수행할 수 있습니다.
"""

__version__ = "0.0.2"

# Splitter 모듈 import
from .splitter import (
    ImageSectionSplitter,
    SectionInfo,
    split_image_sections,
)

# OCR 모듈 import
from .image_ocr.ocr import run_ocr

__all__ = [
    "ImageSectionSplitter",
    "SectionInfo",
    "split_image_sections",
    "run_ocr",
]
