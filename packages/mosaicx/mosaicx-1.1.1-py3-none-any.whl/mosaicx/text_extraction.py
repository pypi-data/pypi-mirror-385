"""
Layered text extraction pipeline for MOSAICX.

Provides a three-stage fallback strategy:
1. Native Docling extraction (text layer)
2. Forced OCR via Docling (EasyOCR)
3. Vision-language transcription via Ollama (default gemma3:27b)
"""

from __future__ import annotations

import base64
import io
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Union

try:
    import requests  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    requests = None  # type: ignore[assignment]

from .constants import (
    DEFAULT_VLM_BASE_URL,
    DEFAULT_VLM_MODEL,
    DEFAULT_OCR_LANGS,
    DEFAULT_FORCE_OCR,
)
from .document_loader import (
    DOC_SUFFIXES,
    DocumentLoadingError,
    LoadedDocument,
    PageAnalysis,
    PLAIN_TEXT_SUFFIXES,
    load_document,
)

VLM_PROMPT = (
    "You are a medical document transcription assistant. "
    "Transcribe all text from the provided page image faithfully. "
    "Preserve medical terminology, numbers, and formatting. "
    "Return plain text only."
)

MIN_TOTAL_CHARS = int(os.getenv("MOSAICX_MIN_TOTAL_CHARS", "200"))
MIN_PAGE_CHARS = int(os.getenv("MOSAICX_MIN_PAGE_CHARS", "80"))
MAX_VLM_PAGES = int(os.getenv("MOSAICX_MAX_VLM_PAGES", "6"))


class TextExtractionError(RuntimeError):
    """Raised when layered text extraction fails."""


@dataclass(slots=True)
class LayeredTextResult:
    markdown: str
    mode: str
    page_analysis: List[PageAnalysis]
    attempts: List[str]
    vlm_pages: List[int]


def _has_sufficient_text(
    loaded: LoadedDocument,
    *,
    min_total_chars: int = MIN_TOTAL_CHARS,
    min_page_chars: int = MIN_PAGE_CHARS,
) -> bool:
    text = (loaded.markdown or "").strip()
    total_chars = len(text)
    if total_chars >= min_total_chars:
        return True

    if total_chars >= min_page_chars * max(1, len(loaded.page_analysis)):
        return True

    for page in loaded.page_analysis:
        if page.text_chars >= min_page_chars:
            return True

    return False


def _image_to_base64(image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _call_ollama_vlm(
    image_b64: str,
    prompt: str,
    *,
    model: str,
    base_url: str,
    timeout: float = 120.0,
) -> str:
    if requests is None:  # pragma: no cover - optional dependency
        raise TextExtractionError("The 'requests' package is required for VLM fallback but is not installed.")

    url = base_url.rstrip("/") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "images": [image_b64],
    }
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "")


def _vlm_transcribe_pages(
    loaded: LoadedDocument,
    *,
    model: str,
    base_url: str,
    pages_to_process: Iterable[int],
) -> Tuple[str, List[int]]:
    if not loaded.conversion_result or not hasattr(loaded.conversion_result, "pages"):
        return "", []

    pages = list(loaded.conversion_result.pages)
    transcripts: List[str] = []
    processed: List[int] = []

    for page_number in pages_to_process:
        if page_number < 1 or page_number > len(pages):
            continue
        page_item = pages[page_number - 1]
        image = getattr(page_item, "image", None)
        if image is None:
            continue
        try:
            encoded = _image_to_base64(image)
            transcript = _call_ollama_vlm(encoded, VLM_PROMPT, model=model, base_url=base_url)
        except Exception:
            continue
        transcript = (transcript or "").strip()
        if not transcript:
            continue
        transcripts.append(f"# Page {page_number}\n{transcript}")
        processed.append(page_number)
        if len(processed) >= MAX_VLM_PAGES:
            break

    return ("\n\n".join(transcripts).strip(), processed)


def extract_text_with_fallback(
    path: Union[str, Path],
    *,
    vlm_model: Optional[str] = None,
    vlm_base_url: Optional[str] = None,
    ocr_languages: Optional[List[str]] = None,
) -> LayeredTextResult:
    """
    Extract markdown from ``path`` using native, OCR, and VLM fallbacks.
    """
    doc_path = Path(path)
    suffix = doc_path.suffix.lower()

    if suffix in PLAIN_TEXT_SUFFIXES:
        try:
            text = doc_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = doc_path.read_text(encoding="latin-1")
        text = text.strip()
        if not text:
            raise TextExtractionError(f"No text content found in {doc_path}")
        return LayeredTextResult(
            markdown=text,
            mode="plain",
            page_analysis=[],
            attempts=["plain"],
            vlm_pages=[],
        )

    if suffix not in DOC_SUFFIXES:
        raise TextExtractionError(
            f"Unsupported file extension: {doc_path.suffix or '<none>'}. "
            f"Supported extensions: {', '.join(sorted(DOC_SUFFIXES))}."
        )

    attempts: List[str] = []
    languages = ocr_languages or DEFAULT_OCR_LANGS
    if not languages:
        languages = ["en"]

    try:
        if DEFAULT_FORCE_OCR:
            primary = load_document(
                doc_path,
                force_ocr=True,
                languages=languages,
                generate_images=True,
                images_scale=1.5,
            )
            attempts.append("ocr")
        else:
            primary = load_document(doc_path)
            attempts.append("native")
    except DocumentLoadingError as exc:
        raise TextExtractionError(str(exc)) from exc

    if _has_sufficient_text(primary):
        return LayeredTextResult(
            markdown=primary.markdown,
            mode=attempts[-1],
            page_analysis=primary.page_analysis,
            attempts=attempts,
            vlm_pages=[],
        )

    native = primary

    ocr_loaded: Optional[LoadedDocument] = None
    if not DEFAULT_FORCE_OCR and doc_path.suffix.lower() == ".pdf":
        try:
            ocr_loaded = load_document(
                doc_path,
                force_ocr=True,
                languages=languages,
                generate_images=True,
                images_scale=1.5,
            )
            attempts.append("ocr")
            if _has_sufficient_text(ocr_loaded):
                return LayeredTextResult(
                    markdown=ocr_loaded.markdown,
                    mode="ocr",
                    page_analysis=ocr_loaded.page_analysis,
                    attempts=attempts,
                    vlm_pages=[],
                )
        except DocumentLoadingError:
            ocr_loaded = None

    doc_for_vlm = ocr_loaded or native

    vlm_model = vlm_model or DEFAULT_VLM_MODEL
    vlm_base_url = vlm_base_url or DEFAULT_VLM_BASE_URL

    if not vlm_model:
        raise TextExtractionError("No VLM model configured for fallback.")

    pages_to_process = [
        page.page_number
        for page in doc_for_vlm.page_analysis
        if page.text_chars < MIN_PAGE_CHARS
    ]

    vlm_text, processed_pages = _vlm_transcribe_pages(
        doc_for_vlm,
        model=vlm_model,
        base_url=vlm_base_url,
        pages_to_process=pages_to_process,
    )

    if not vlm_text:
        fallback_doc = doc_for_vlm if doc_for_vlm.markdown.strip() else native
        return LayeredTextResult(
            markdown=fallback_doc.markdown,
            mode=attempts[-1],
            page_analysis=fallback_doc.page_analysis,
            attempts=attempts,
            vlm_pages=[],
        )

    attempts.append("vlm")
    combined = f"{(doc_for_vlm.markdown or '').strip()}\n\n{vlm_text}".strip()
    return LayeredTextResult(
        markdown=combined,
        mode="vlm",
        page_analysis=doc_for_vlm.page_analysis,
        attempts=attempts,
        vlm_pages=processed_pages,
    )


__all__ = ["extract_text_with_fallback", "LayeredTextResult", "TextExtractionError"]
