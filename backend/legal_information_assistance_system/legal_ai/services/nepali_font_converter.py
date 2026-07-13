"""
Legacy Nepali font detection and Unicode conversion.

Handles Preeti, Kantipur, Sagarmatha, and Himali (Himalb) encodings that
appear as ASCII gibberish when extracted from text-based PDFs, e.g.:

    xjfO{ ;'/Iff -Joj:yf_ lgodfjnL  →  हवाई सरक्षा (व्यवस्था) नियमावली
"""

from __future__ import annotations

import re
from functools import lru_cache

try:
    from nepali_converter import convert as _convert_font
    from nepali_converter import detect_font as _detect_font
except ImportError:  # pragma: no cover - optional dependency
    _convert_font = None
    _detect_font = None

# Supported legacy encodings (Himali is stored as "himalb" in nepali-converter).
SUPPORTED_LEGACY_FONTS: tuple[str, ...] = ("preeti", "kantipur", "sagarmatha", "himalb")
FONT_ALIASES: dict[str, str] = {
    "himali": "himalb",
    "himali_tt": "himalb",
    "fontasy_himali_tt": "himalb",
    "pcs_nepali": "preeti",
}

DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F\uA8E0-\uA8FF]")
LETTER_PATTERN = re.compile(r"[\w\u0900-\u097F\uA8E0-\uA8FF]", re.UNICODE)

# Ratio of Devanagari letters needed to classify text as Unicode Nepali.
UNICODE_THRESHOLD = 0.15

# Brackets, pipes, and slashes used as matras/conjuncts in legacy fonts.
LEGACY_SPECIAL_CHARS = set("{}[]|\\/:;'_")

# Minimum non-space characters before attempting legacy-font classification.
MIN_TEXT_LENGTH = 20


def _devanagari_ratio(text: str) -> float:
    """Return the fraction of letter-like characters that are Devanagari."""
    if not text:
        return 0.0
    letters = LETTER_PATTERN.findall(text)
    if not letters:
        return 0.0
    devanagari_count = len(DEVANAGARI_PATTERN.findall(text))
    return devanagari_count / len(letters)


def _legacy_special_ratio(text: str) -> float:
    """Return the fraction of non-space chars that look like legacy-font markers."""
    non_space = [ch for ch in text if not ch.isspace()]
    if not non_space:
        return 0.0
    special = sum(1 for ch in non_space if ch in LEGACY_SPECIAL_CHARS or ord(ch) > 127)
    return special / len(non_space)


def _normalize_font_name(font: str | None) -> str | None:
    if not font:
        return None
    normalized = font.strip().lower().replace("-", "_").replace(" ", "_")
    return FONT_ALIASES.get(normalized, normalized)


def is_unicode_text(text: str) -> bool:
    """
    True when extracted text already contains meaningful Unicode Devanagari.

    DOC/DOCX-converted PDFs and OCR output typically pass this check.
    """
    if not text or not text.strip():
        return False
    return _devanagari_ratio(text) >= UNICODE_THRESHOLD


def is_legacy_font(text: str) -> bool:
    """
    True when text looks like a legacy Nepali font encoding rather than Unicode.

    Detection strategy:
    1. Reject empty or already-Unicode text.
    2. Look for legacy structural markers (brackets, high-byte chars).
    3. Confirm by trial conversion — the best font mapping must yield Unicode Nepali.
    """
    if not text or not text.strip() or len(text.strip()) < MIN_TEXT_LENGTH:
        return False
    if is_unicode_text(text):
        return False

    # Pure English legal PDFs have low legacy markers and fail conversion scoring.
    if _legacy_special_ratio(text) < 0.02 and _detect_legacy_font_name(text) is None:
        return False

    converted, _font = _best_legacy_conversion(text)
    return converted is not None and is_unicode_text(converted)


@lru_cache(maxsize=4)
def _cached_convert(text: str, font: str) -> str:
    if _convert_font is None:
        return text
    return _convert_font(text, font)


def _score_converted_text(text: str) -> float:
    """Score converted output — higher means more plausible Nepali Unicode."""
    ratio = _devanagari_ratio(text)
    if ratio == 0:
        return 0.0
    # Penalise outputs that still contain many legacy marker characters.
    legacy_penalty = _legacy_special_ratio(text) * 0.5
    return max(0.0, ratio - legacy_penalty)


def _best_legacy_conversion(text: str) -> tuple[str | None, str | None]:
    """
    Try all supported fonts and return the conversion with the highest Unicode score.
    """
    if _convert_font is None:
        return None, None

    candidates: list[tuple[float, str, str]] = []

    detected = _detect_legacy_font_name(text)
    fonts_to_try = [detected] if detected else []
    fonts_to_try.extend(font for font in SUPPORTED_LEGACY_FONTS if font not in fonts_to_try)

    for font in fonts_to_try:
        if not font:
            continue
        try:
            converted = _cached_convert(text, font)
        except Exception:
            continue
        score = _score_converted_text(converted)
        if score > 0:
            candidates.append((score, font, converted))

    if not candidates:
        return None, None

    candidates.sort(key=lambda item: item[0], reverse=True)
    _score, best_font, best_text = candidates[0]
    return best_text, best_font


def _detect_legacy_font_name(text: str) -> str | None:
    """Detect the most likely legacy font using nepali-converter heuristics."""
    if _detect_font is None:
        return None
    try:
        return _normalize_font_name(_detect_font(text))
    except Exception:
        return None


def convert_legacy_to_unicode(text: str, font: str | None = None) -> str:
    """
    Convert legacy-font text to Unicode Devanagari.

    When *font* is omitted the encoding is auto-detected.  Falls back to
    trial conversion across all supported fonts when detection is uncertain.
    """
    if not text or not text.strip():
        return text
    if is_unicode_text(text):
        return text
    if _convert_font is None:
        return text

    normalized_font = _normalize_font_name(font)
    if normalized_font and normalized_font in SUPPORTED_LEGACY_FONTS:
        try:
            converted = _cached_convert(text, normalized_font)
            if _score_converted_text(converted) > 0:
                return converted
        except Exception:
            pass

    converted, _detected_font = _best_legacy_conversion(text)
    return converted if converted is not None else text


def detect_legacy_font(text: str) -> str | None:
    """Return the detected legacy font name, or None if text is not legacy-encoded."""
    if not is_legacy_font(text):
        return None
    detected = _detect_legacy_font_name(text)
    if detected:
        return detected
    _converted, font = _best_legacy_conversion(text)
    return font
