"""
PDF text extraction pipeline for Nepali legal documents.

Automatically classifies PDFs into three categories and applies the right method:

1. **Unicode PDFs** (DOC/DOCX → PDF) — extract with pypdf/fitz, no OCR.
2. **Legacy-font PDFs** (Preeti, Kantipur, Himali, …) — extract text, convert to Unicode.
3. **Scanned PDFs** — OCR at 300–400 DPI with image preprocessing.

OCR is used only as a last resort to avoid degrading text-based PDF quality.
"""

from __future__ import annotations

import io
import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from legal_information_assistance_system.legal_ai.services.nepali_font_converter import (
    convert_legacy_to_unicode,
    is_legacy_font,
    is_unicode_text,
)

try:
    import fitz
except ImportError:  # PyMuPDF optional fallback
    fitz = None

try:
    import numpy as np
except ImportError:  # type: ignore[assignment]
    np = None

try:
    from PIL import Image, ImageOps
except ImportError:  # type: ignore[assignment]
    Image = None
    ImageOps = None

try:
    import pytesseract
except ImportError:  # type: ignore[assignment]
    pytesseract = None

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PAGE_NUMBER_PATTERN = re.compile(r"^\s*\d{1,4}\s*$")
WATERMARK_PATTERNS = [
    re.compile(r"draft", re.I),
    re.compile(r"confidential", re.I),
    re.compile(r"do not distribute", re.I),
]

# Minimum average printable characters per page to consider text extraction usable.
MIN_CHARS_PER_PAGE = 30

# Fraction of page area covered by images above which a page is image-dominant.
IMAGE_COVERAGE_THRESHOLD = 0.55

# OCR rendering DPI (300–400 recommended for Nepali Devanagari).
OCR_DPI = 350

# Tesseract config: LSTM engine, uniform text block.
TESSERACT_CONFIG = "--oem 3 --psm 6"

# Backward-compatible alias used by existing tests.
TEXT_BASED_THRESHOLD = 0.15


# ---------------------------------------------------------------------------
# Text-quality helpers
# ---------------------------------------------------------------------------


def _devanagari_ratio(text: str) -> float:
    if not text:
        return 0.0
    letters = re.findall(r"[\w\u0900-\u097F\uA8E0-\uA8FF]", text, re.UNICODE)
    if not letters:
        return 0.0
    devanagari = len(re.findall(r"[\u0900-\u097F\uA8E0-\uA8FF]", text))
    return devanagari / len(letters)


def _combined_text(pages: List[str]) -> str:
    return "\n".join(page for page in pages if page and page.strip())


def _average_chars_per_page(pages: List[str]) -> float:
    non_empty = [page for page in pages if page.strip()]
    if not non_empty:
        return 0.0
    return sum(len(page.strip()) for page in non_empty) / len(non_empty)


def _has_extractable_text(pages: List[str]) -> bool:
    """True when pages contain enough printable text to be worth classifying."""
    return _average_chars_per_page(pages) >= MIN_CHARS_PER_PAGE


def _text_quality_score(text: str) -> float:
    """Backward-compatible quality metric (Devanagari letter ratio)."""
    return _devanagari_ratio(text)


# ---------------------------------------------------------------------------
# PDF-type detection
# ---------------------------------------------------------------------------


def is_scanned_pdf(file_path: str | Path, pages: List[str]) -> bool:
    """
    True when the PDF appears to be a scanned image document.

    A PDF is treated as scanned when:
    - Extracted text is sparse or empty, AND
    - Pages are dominated by embedded images (checked via PyMuPDF when available).

    Legacy-font and Unicode PDFs are never classified as scanned even when
    Devanagari is absent, because they still carry extractable (encoded) text.
    """
    path = Path(file_path)
    combined = _combined_text(pages)

    # Unicode or legacy-font PDFs have real text layers — skip OCR.
    if is_unicode_text(combined):
        return False
    if is_legacy_font(combined):
        return False

    # Substantial ASCII/English text layer — not a scan.
    if _has_extractable_text(pages):
        return False

    # No fitz available: fall back to "no text means scanned".
    if fitz is None:
        return not _has_extractable_text(pages)

    return _pages_are_image_dominant(path)


def _pages_are_image_dominant(path: Path) -> bool:
    """Return True when most pages are covered primarily by raster images."""
    if fitz is None:
        return True

    try:
        with fitz.open(str(path)) as doc:
            if not doc.page_count:
                return True

            image_dominant_pages = 0
            checked_pages = 0

            for page in doc:
                checked_pages += 1
                page_area = page.rect.width * page.rect.height
                if page_area <= 0:
                    continue

                image_area = 0.0
                for img_info in page.get_images(full=True):
                    try:
                        xref = img_info[0]
                        for img_rect in page.get_image_rects(xref):
                            image_area += img_rect.width * img_rect.height
                    except Exception:
                        continue

                text = page.get_text("text") or ""
                text_chars = len(text.strip())

                coverage = min(1.0, image_area / page_area)
                if coverage >= IMAGE_COVERAGE_THRESHOLD and text_chars < MIN_CHARS_PER_PAGE:
                    image_dominant_pages += 1

            if checked_pages == 0:
                return True
            return image_dominant_pages / checked_pages >= 0.6
    except Exception:
        return True


# ---------------------------------------------------------------------------
# Extraction backends
# ---------------------------------------------------------------------------


def extract_with_pypdf(file_path: str | Path) -> List[str]:
    """Extract per-page text using pypdf (fast, works for most Unicode PDFs)."""
    path = Path(file_path)
    pages: List[str] = []
    try:
        reader = PdfReader(str(path))
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
            pages.append(page_text.strip())
    except Exception:
        return []
    return pages


def extract_with_fitz(file_path: str | Path) -> List[str]:
    """Extract per-page text using PyMuPDF (better font/layout handling)."""
    if fitz is None:
        return []

    path = Path(file_path)
    pages: List[str] = []
    try:
        with fitz.open(str(path)) as doc:
            for page in doc:
                page_text = page.get_text("text") or ""
                pages.append(page_text.strip())
    except Exception:
        return []
    return pages


def _preprocess_for_ocr(image: Image.Image) -> Image.Image:
    """
    Prepare a page image for Tesseract OCR.

    Steps: grayscale → contrast normalisation → Otsu-style threshold → deskew.
    """
    if Image is None:
        return image

    gray = image.convert("L")
    if ImageOps is not None:
        gray = ImageOps.autocontrast(gray)

    if np is not None:
        arr = np.array(gray)
        threshold = float(np.mean(arr))
        gray = gray.point(lambda px, t=threshold: 255 if px > t else 0, mode="1").convert("L")
        gray = _deskew_image(gray)
    else:
        gray = gray.point(lambda px: 255 if px > 128 else 0, mode="1").convert("L")

    return gray


def _deskew_image(image: Image.Image) -> Image.Image:
    """
    Correct slight page rotation using a projection-profile search.

    Tests small angles (±5°) and picks the one with the sharpest horizontal
    text-line projection — a reliable deskew heuristic for document scans.
    """
    if np is None or Image is None:
        return image

    try:
        from scipy.ndimage import rotate as ndimage_rotate
    except ImportError:
        return image

    arr = np.array(image)
    if arr.ndim == 3:
        arr = np.mean(arr, axis=2)
    binary = arr < np.mean(arr)

    def projection_score(angle: float) -> float:
        rotated = ndimage_rotate(binary, angle, reshape=False, order=0, mode="constant", cval=0)
        projection = np.sum(rotated, axis=1)
        return float(np.sum(projection ** 2))

    best_angle = 0.0
    best_score = projection_score(0.0)
    for angle in np.arange(-5.0, 5.5, 0.5):
        score = projection_score(float(angle))
        if score > best_score:
            best_score = score
            best_angle = float(angle)

    if abs(best_angle) > 0.25:
        return image.rotate(-best_angle, expand=True, fillcolor=255)
    return image


def extract_with_ocr(file_path: str | Path, dpi: int = OCR_DPI) -> List[str]:
    """
    OCR each page at high DPI with Nepali+English language support.

    Only called for scanned PDFs — never for text-based Unicode or legacy-font PDFs.
    """
    if fitz is None or Image is None or pytesseract is None:
        return []

    path = Path(file_path)
    pages: List[str] = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    try:
        with fitz.open(str(path)) as doc:
            for page in doc:
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                img_bytes = pix.tobytes("ppm")
                image = Image.open(io.BytesIO(img_bytes))
                processed = _preprocess_for_ocr(image)
                ocr_text = pytesseract.image_to_string(
                    processed,
                    lang="nep+eng",
                    config=TESSERACT_CONFIG,
                )
                pages.append(ocr_text.strip())
    except Exception:
        return []
    return pages


# ---------------------------------------------------------------------------
# Classification and normalisation
# ---------------------------------------------------------------------------


def _classify_and_normalize(pages: List[str]) -> List[str]:
    """
    Inspect extracted pages and convert legacy-font text to Unicode when needed.

    Returns pages unchanged for Unicode PDFs, converted for legacy-font PDFs.
    Handles mixed content by checking each page individually.
    """
    combined = _combined_text(pages)
    if not combined.strip():
        return pages

    # Check each page individually for legacy font content
    legacy_pages = [i for i, page in enumerate(pages) if page.strip() and is_legacy_font(page)]
    unicode_pages = [i for i, page in enumerate(pages) if page.strip() and is_unicode_text(page)]
    
    # If most pages are legacy font, convert all
    if len(legacy_pages) > len(unicode_pages):
        return [convert_legacy_to_unicode(page) for page in pages]
    
    # If mixed content, convert only legacy pages
    if legacy_pages and unicode_pages:
        return [
            convert_legacy_to_unicode(page) if i in legacy_pages else page
            for i, page in enumerate(pages)
        ]
    
    # If all pages are Unicode, no conversion needed
    if not legacy_pages and unicode_pages:
        return pages
    
    # If overall text is legacy font, convert all pages
    if is_legacy_font(combined):
        return [convert_legacy_to_unicode(page) for page in pages]

    return pages


def _pick_better_pages(candidate: List[str], current: List[str]) -> List[str]:
    """Prefer the extraction with more content or higher Devanagari quality."""
    if not candidate:
        return current
    if not current:
        return candidate

    cand_chars = _average_chars_per_page(candidate)
    curr_chars = _average_chars_per_page(current)
    if cand_chars > curr_chars * 1.2:
        return candidate

    cand_score = _devanagari_ratio(_combined_text(candidate))
    curr_score = _devanagari_ratio(_combined_text(current))
    if cand_score > curr_score + 0.05:
        return candidate

    return current if curr_chars >= cand_chars else candidate


# ---------------------------------------------------------------------------
# Page cleaning (headers, footers, watermarks)
# ---------------------------------------------------------------------------


def _extract_pdf_metadata(path: Path) -> dict:
    metadata = {}
    try:
        reader = PdfReader(str(path))
        info = reader.metadata
        if info:
            for key, value in info.items():
                if key and value:
                    clean_key = key.lstrip("/").lower()
                    metadata[clean_key] = value
    except Exception:
        pass
    return metadata


def _get_page_count(path: Path) -> int:
    try:
        reader = PdfReader(str(path))
        return len(reader.pages)
    except Exception:
        if fitz is not None:
            try:
                with fitz.open(str(path)) as doc:
                    return doc.page_count
            except Exception:
                pass
        return 0


def _detect_repeated_lines(pages: List[str], min_ratio: float = 0.6) -> set[str]:
    """Find header/footer lines repeated across most pages."""
    if len(pages) < 3:
        return set()

    threshold = max(2, int(len(pages) * min_ratio))
    first_lines: Counter[str] = Counter()
    last_lines: Counter[str] = Counter()

    for page in pages:
        lines = [line.strip() for line in page.splitlines() if line.strip()]
        if not lines:
            continue
        first_lines[lines[0]] += 1
        if len(lines) > 1:
            last_lines[lines[-1]] += 1

    repeated: set[str] = set()
    for line, count in first_lines.items():
        if count >= threshold and len(line) < 120:
            repeated.add(line)
    for line, count in last_lines.items():
        if count >= threshold and len(line) < 120:
            repeated.add(line)
    return repeated


def _clean_page(page_text: str, repeated_lines: set[str]) -> str:
    lines = page_text.splitlines()
    cleaned_lines: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        if stripped in repeated_lines:
            continue
        if PAGE_NUMBER_PATTERN.match(stripped):
            continue
        if any(pattern.search(stripped) for pattern in WATERMARK_PATTERNS):
            continue
        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def _finalize_pages(pages: List[str]) -> str:
    """Remove repeated headers/footers and join pages."""
    repeated_lines = _detect_repeated_lines(pages)
    cleaned_pages = [_clean_page(page, repeated_lines) for page in pages]
    cleaned_pages = [page for page in cleaned_pages if page.strip()]
    return "\n\n".join(cleaned_pages)


# ---------------------------------------------------------------------------
# Backward-compatible helper
# ---------------------------------------------------------------------------


def _is_text_based(pages: List[str]) -> bool:
    """
    Return True when pages contain usable Nepali/Unicode text.

    Checks raw Unicode content and legacy-font text after conversion.
    """
    if not pages:
        return False

    combined = _combined_text(pages)
    if is_unicode_text(combined):
        return True

    if is_legacy_font(combined):
        converted = convert_legacy_to_unicode(combined)
        return is_unicode_text(converted)

    return _devanagari_ratio(combined) >= TEXT_BASED_THRESHOLD


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_pdf_text(file_path: str) -> Tuple[str, int]:
    """
    Extract text from a Nepali legal PDF using automatic type detection.

    Pipeline:
    1. Extract with pypdf.
    2. Classify: Unicode → use as-is; legacy-font → convert to Unicode.
    3. If extraction is poor, retry with PyMuPDF.
    4. OCR only when the PDF is scanned (image-only) or has no usable text.

    Returns:
        (extracted_text, page_count)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    try:
        page_count = _get_page_count(path)
    except PdfReadError as exc:
        raise ValueError(f"Unable to parse PDF document: {exc}") from exc

    if page_count == 0:
        raise ValueError(f"Unable to parse PDF document: {path}")

    # --- Step 1: pypdf extraction ---
    pages = extract_with_pypdf(path)

    if _has_extractable_text(pages):
        pages = _classify_and_normalize(pages)
        # Text-based PDF (Unicode, legacy-font, or English) — never OCR.
        if not is_scanned_pdf(path, pages):
            return _finalize_pages(pages), page_count

    # --- Step 2: PyMuPDF fallback (better encoding handling) ---
    fitz_pages = extract_with_fitz(path)
    if fitz_pages and _has_extractable_text(fitz_pages):
        fitz_pages = _classify_and_normalize(fitz_pages)
        pages = _pick_better_pages(fitz_pages, pages)
        if not is_scanned_pdf(path, pages):
            return _finalize_pages(pages), page_count

    # --- Step 3: OCR for scanned PDFs only ---
    if is_scanned_pdf(path, pages):
        ocr_pages = extract_with_ocr(path)
        if ocr_pages and _has_extractable_text(ocr_pages):
            pages = ocr_pages

    return _finalize_pages(pages), page_count
