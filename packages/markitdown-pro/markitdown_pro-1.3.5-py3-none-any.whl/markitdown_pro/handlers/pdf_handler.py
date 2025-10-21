import asyncio
import os
import re
import tempfile
from contextlib import contextmanager
from enum import Enum
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import Optional

import fitz

from ..common.logger import logger
from ..common.utils import detect_extension
from ..converters.azure_doc_intel_wrapper import DocIntelligenceWrapper
from ..converters.gpt_vision_wrapper import GPTVisionWrapper
from ..converters.markitdown_wrapper import MarkItDownWrapper
from ..converters.pymupdf_wrapper import PyMuPDFWrapper
from ..converters.unstructured_wrapper import UnstructuredWrapper
from .base_handler import BaseHandler


class ConversionError(Exception):
    pass


# region helpers: page parsing / slicing
def _parse_pages_spec(pages: str | list[int], total_pages: int) -> list[int]:
    """Return a sorted, de-duped, 0-based list of page indexes within bounds."""
    if pages is None:
        return list(range(total_pages))
    if isinstance(pages, (list, tuple)):
        idxs = [int(p) - 1 if p >= 1 else int(p) for p in pages]  # allow 1-based
    else:
        idxs = []
        for tok in re.split(r"[,\s]+", pages.strip()):
            if not tok:
                continue
            if "-" in tok:
                a, b = tok.split("-", 1)
                a, b = int(a), int(b)
                if a > b:
                    a, b = b, a
                idxs.extend(range(a - 1, b))  # user passes 1-based
            else:
                idxs.append(int(tok) - 1)
    idxs = sorted(set(i for i in idxs if 0 <= i < total_pages))
    return idxs


def _coalesce_runs(idxs: list[int]) -> list[tuple[int, int]]:
    """Turn [0,1,2,4,7,8] into [(0,2),(4,4),(7,8)]"""
    runs = []
    for k, g in groupby(enumerate(idxs), key=lambda t: t[0] - t[1]):
        group = list(map(itemgetter(1), g))
        runs.append((group[0], group[-1]))
    return runs


@contextmanager
def _maybe_slice_pdf(src_path: str, page_idxs: list[int], total_pages: int):
    """Yield original pdf if full-range, else a temp sliced pdf with selected pages."""
    full_range = (
        len(page_idxs) == total_pages and page_idxs[0] == 0 and page_idxs[-1] == total_pages - 1
    )
    if full_range:
        yield src_path
        return
    import fitz

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    try:
        with fitz.open(src_path) as src:
            dst = fitz.open()
            for start, end in _coalesce_runs(page_idxs):
                dst.insert_pdf(src, from_page=start, to_page=end)
            dst.save(tmp.name)
            dst.close()
        yield tmp.name
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass


# endregion


class PDFType(Enum):
    """
    Simple classification of a PDF based on page contents.

    - TEXT_ONLY:        Every page has "enough" extractable text; no pages contain images.
    - TEXT_PLUS_IMAGES: At least one page contains text and at least one page contains images.
    - ALL_IMAGES:       Every page has at least one image and no page has "enough" text
                        (typical of scanned/image-only PDFs).
    """

    TEXT_ONLY = "TEXT_ONLY"
    TEXT_PLUS_IMAGES = "TEXT_PLUS_IMAGES"
    ALL_IMAGES = "ALL_IMAGES"


class PDFHandler(BaseHandler):
    """
    Orchestrates PDF → Markdown conversion by trying a sequence of converters
    chosen from a text-oriented pipeline or an image/OCR pipeline depending
    on a quick content scan of the PDF.

    The flow is:
      1) `_detect_pdf_type` runs a fast pass over the PDF (offloaded to a thread)
         to count text-bearing and image-bearing pages.
      2) Based on the detected `PDFType`, choose a pipeline:
           - TEXT_ONLY:         text pipeline
           - ALL_IMAGES:        image pipeline (OCR)
           - TEXT_PLUS_IMAGES:  image pipeline (OCR)
      3) Iterate the chosen converters in order until one returns acceptable Markdown.

    Notes:
    - Converters MUST implement an async `convert(file_path: str) -> Optional[str]`.
    - `ensure_minimum_content` is used to filter out trivial/empty results.
    """

    # File extensions handled by this handler
    SUPPORTED_EXTENSIONS = frozenset([".pdf"])

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Text-first converters (fastest/cheapest first, progressively more robust)
        self.markitdown = MarkItDownWrapper()
        self.unstructured = UnstructuredWrapper()
        self.pymu = PyMuPDFWrapper()
        self.azure_docint = DocIntelligenceWrapper()

        # OCR-based converter for scanned/image-only PDFs
        self.gpt_vision = GPTVisionWrapper()

        # Pipelines in the order they should be attempted
        self.text_pipeline = [self.markitdown, self.unstructured, self.pymu, self.azure_docint]
        self.image_pipeline = [self.gpt_vision]

    async def handle(self, file_path: str, *args, **kwargs) -> Optional[str]:
        """
        Convert a PDF to Markdown, honoring page selection from kwargs only.

        Expected kwargs:
        - pages: list[int] (1-based page numbers). If absent/invalid → process all pages.
        """
        try:
            # Resolve selection to 0-based page indexes (offloaded: PyMuPDF is CPU-bound)
            def _resolve():
                with fitz.open(file_path) as doc:
                    total = doc.page_count
                pages_kw = kwargs.get("pages", None)
                if isinstance(pages_kw, list) and all(isinstance(p, int) for p in pages_kw):
                    idxs = sorted(set(p - 1 for p in pages_kw))
                    idxs = [i for i in idxs if 0 <= i < total]
                    if not idxs:
                        logger.warning(
                            f"PDFHandler: 'pages' kwarg produced no valid pages for {file_path}; defaulting to all pages."
                        )
                        idxs = list(range(total))
                else:
                    if pages_kw is not None:
                        logger.warning(
                            "PDFHandler: 'pages' must be a list[int] (1-based). Defaulting to all pages."
                        )
                    idxs = list(range(total))
                return idxs, total

            page_idxs, total_pages = await asyncio.to_thread(_resolve)

            # Detect type using only the selected pages
            pdf_type = await self._detect_pdf_type(file_path, page_indexes=page_idxs)
            pipeline = (
                self.image_pipeline
                if pdf_type in (PDFType.ALL_IMAGES, PDFType.TEXT_PLUS_IMAGES)
                else self.text_pipeline
            )

            # Slice once and feed to converters
            with _maybe_slice_pdf(file_path, page_idxs, total_pages) as to_process:
                for converter in pipeline:
                    preview = [i + 1 for i in page_idxs[:5]]
                    logger.info(
                        f"PDFHandler: Trying {converter.name} for {file_path} pages={preview}{'...' if len(page_idxs) > 5 else ''}"
                    )
                    try:
                        md_content = await converter.convert(to_process)
                        return md_content
                    except Exception as e:
                        logger.error(
                            f"PDFHandler: Converter {converter.name} failed for subset {file_path}: {e}"
                        )

            raise RuntimeError(f"PDF conversion failed with all converters for {file_path}")
        except Exception as e:
            logger.error(f"PDFHandler: Error handling PDF '{file_path}': {e}")
            return None

    async def _detect_pdf_type(
        self,
        file_path: str,
        page_indexes: list[int] | None = None,
    ) -> PDFType:
        """
        Quickly scan the PDF to decide which pipeline to run.

        Heuristic
        ---------
        - A page is considered to have "text" if the extracted text length ≥ `min_text_length_threshold`.
        - A page is considered to have "images" if `page.get_images(full=True)` returns any entries.
        - The final classification is derived from counts across all pages.

        Parameters
        ----------
        file_path : str
            Path to the input PDF.

        Returns
        -------
        PDFType
            Classification result used to pick the processing pipeline.

        Raises
        ------
        Exception
            If the file cannot be opened or scanned.
        """
        min_text_length_threshold = 20
        try:

            def _scan() -> PDFType:
                with fitz.open(file_path) as doc:
                    total_pages = doc.page_count
                    idxs = page_indexes or list(range(total_pages))
                    pages_with_text = 0
                    pages_with_images = 0
                    for i in idxs:
                        page = doc.load_page(i)
                        if not page:
                            continue
                        if len((page.get_text() or "").strip()) >= min_text_length_threshold:
                            pages_with_text += 1
                        if page.get_images(full=True):
                            pages_with_images += 1
                    is_text_only = pages_with_text == len(idxs) and pages_with_images == 0
                    is_all_images = pages_with_images == len(idxs) and pages_with_text == 0
                    has_text_and_images = pages_with_text > 0 and pages_with_images > 0
                    if is_text_only:
                        return PDFType.TEXT_ONLY
                    elif is_all_images:
                        return PDFType.ALL_IMAGES
                    elif has_text_and_images:
                        return PDFType.TEXT_PLUS_IMAGES
                    return PDFType.TEXT_PLUS_IMAGES

            return await asyncio.to_thread(_scan)
        except Exception as e:
            logger.error(f"PDFHandler: Error analyzing PDF '{file_path}': {e}")
            raise

    async def get_page_count(self, file_path: str | os.PathLike) -> Optional[int]:
        p = Path(file_path)
        ext = detect_extension(str(p.absolute()))
        if ext not in self.SUPPORTED_EXTENSIONS:
            logger.warning(f"DocumentIntelligenceHandler: Unsupported file format: {ext}")
            return None
        if ext in self.SUPPORTED_EXTENSIONS:
            try:
                import pypdf as _pypdf

                try:
                    reader = _pypdf.PdfReader(str(p))
                except Exception:
                    with open(p, "rb") as fh:
                        reader = _pypdf.PdfReader(fh)
                return len(reader.pages)
            except Exception as e_pdf:
                logger.warning(
                    f"DocumentIntelligenceHandler: local PDF page count failed for '{p}': {e_pdf}"
                )

    # async def _run_soffice_convert(
    #     self, file_path: Path, filter_name: Optional[str] = None, timeout_s: int = 180
    # ) -> Path:
    #     """
    #     Generic converter via LibreOffice 'soffice' headless CLI.
    #     `filter_name` can be 'writer_pdf_Export' for DOCX or 'impress_pdf_Export' for PPTX.
    #     Returns final PDF path placed next to the source file.
    #     """
    #     soffice = shutil.which("soffice") or shutil.which("libreoffice")
    #     if not soffice:
    #         raise ConversionError("LibreOffice not found on PATH (need 'soffice').")

    #     if not file_path.exists():
    #         raise FileNotFoundError(file_path)

    #     # Output to a temp dir, then move next to source
    #     tmp_out = Path(tempfile.mkdtemp())
    #     try:
    #         convert_to = "pdf" if not filter_name else f"pdf:{filter_name}"
    #         cmd = [
    #             soffice,
    #             "--headless",
    #             "--invisible",
    #             "--norestore",
    #             "--nodefault",
    #             "--nolockcheck",
    #             "--nofirststartwizard",
    #             "--convert-to",
    #             convert_to,
    #             str(file_path),
    #             "--outdir",
    #             str(tmp_out),
    #         ]

    #         proc = await asyncio.create_subprocess_exec(
    #             *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    #         )
    #         try:
    #             stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
    #         except asyncio.TimeoutError:
    #             proc.kill()
    #             raise ConversionError("LibreOffice timed out during conversion")

    #         if proc.returncode != 0:
    #             raise ConversionError(
    #                 f"LibreOffice failed (code {proc.returncode}). Stderr: {stderr.decode(errors='ignore')}"
    #             )

    #         produced = tmp_out / (file_path.stem + ".pdf")
    #         if not produced.exists():
    #             # Some LO versions may change the output name; find the first PDF
    #             candidates = list(tmp_out.glob("*.pdf"))
    #             if not candidates:
    #                 raise ConversionError("Expected PDF not created by LibreOffice")
    #             produced = candidates[0]

    #         final_pdf = file_path.with_suffix(".pdf")
    #         if final_pdf.exists():
    #             final_pdf.unlink()
    #         produced.replace(final_pdf)
    #         return final_pdf
    #     finally:
    #         try:
    #             # Clean temp dir
    #             for f in tmp_out.glob("*"):
    #                 try:
    #                     f.unlink()
    #                 except Exception:
    #                     pass
    #             tmp_out.rmdir()
    #         except Exception:
    #             pass

    # async def docx_to_pdf(self, file_path: str | Path, timeout_s: int = 180) -> Path:
    #     src = Path(file_path).resolve()
    #     if src.suffix.lower() != ".docx":
    #         raise ValueError("docx_to_pdf expects a .docx file")
    #     # writer filter produces better pagination on Writer docs
    #     return await self._run_soffice_convert(
    #         src, filter_name="writer_pdf_Export", timeout_s=timeout_s
    #     )

    # async def pptx_to_pdf(self, file_path: str | Path, timeout_s: int = 180) -> Path:
    #     src = Path(file_path).resolve()
    #     if src.suffix.lower() != ".pptx":
    #         raise ValueError("pptx_to_pdf expects a .pptx file")
    #     # impress filter produces better pagination on Impress/PowerPoint
    #     return await self._run_soffice_convert(
    #         src, filter_name="impress_pdf_Export", timeout_s=timeout_s
    #     )
