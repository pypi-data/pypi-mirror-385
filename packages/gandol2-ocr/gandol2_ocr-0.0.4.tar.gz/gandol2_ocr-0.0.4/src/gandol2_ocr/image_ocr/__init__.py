"""gandol2-image-ocr: PaddleOCR 기반 OCR 유틸리티."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("gandol2-image-ocr")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .ocr import run_ocr
