"""
Splitter 모듈 - 최상위 레벨에서 접근 가능하도록 re-export
"""

from .splitter.splitter import (
    ImageSectionSplitter,
    SectionInfo,
    split_image_sections,
)

__all__ = [
    "ImageSectionSplitter",
    "SectionInfo",
    "split_image_sections",
]
