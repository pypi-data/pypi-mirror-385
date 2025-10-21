"""
Image Section Splitter

세로로 긴 상세페이지 이미지를 시각적 경계 기준으로 안전하게 섹션 분리
"""

__version__ = "1.0.0"

from .splitter import (
    ImageSectionSplitter,
    SectionInfo,
    split_image_sections,
)

__all__ = [
    "ImageSectionSplitter",
    "SectionInfo",
    "split_image_sections",
]
