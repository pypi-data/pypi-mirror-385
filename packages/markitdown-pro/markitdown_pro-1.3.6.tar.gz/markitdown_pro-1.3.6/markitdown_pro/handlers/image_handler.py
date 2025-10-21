import contextlib
from pathlib import Path
from typing import Optional

from ..common.logger import logger
from ..common.utils import detect_extension
from ..converters.gpt_vision_wrapper import GPTVisionWrapper
from .base_handler import BaseHandler


class ImageHandler(BaseHandler):
    SUPPORTED_EXTENSIONS = GPTVisionWrapper.SUPPORTED_EXTENSIONS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpt_vision = GPTVisionWrapper()

    async def handle(self, file_path, *args, **kwargs) -> Optional[str]:
        """
        Handles image files by converting them to Markdown using GPT Vision.

        Args:
            file_path: Path to the image file.

        Returns:
            Markdown string representing the image content (OCR and analysis),
            or an error message.
        """
        logger.info(f"Processing image file: {file_path}")
        try:
            md_content = await self.gpt_vision.convert(file_path)
            return md_content
        except Exception as e:
            logger.error(f"ImageHandler: Error handling image file '{file_path}': {e}")
            return None
        finally:
            # Prevent "Event loop is closed" from httpx finalizers during pytest teardown
            with contextlib.suppress(Exception):
                if hasattr(self.gpt_vision, "gpt_vision"):
                    await self.gpt_vision.gpt_vision.aclose()

    async def get_page_count(self, file_path: str | Path) -> Optional[int]:
        """
        Determines the number of pages in the given image file.
        """
        p = Path(file_path)
        ext = detect_extension(str(p.absolute()))
        if ext not in self.SUPPORTED_EXTENSIONS:
            logger.warning(f"ImageHandler: Unsupported file format: {ext}")
            return None

        if ext in {".tif", ".tiff"}:
            try:
                from PIL import Image, ImageSequence  # optional dependency

                with Image.open(str(p)) as im:
                    return sum(1 for _ in ImageSequence.Iterator(im)) or 1
            except Exception as e_tiff:
                logger.warning(f"ImageHandler: local TIFF page count failed for '{p}': {e_tiff}")
        else:
            return 1

    async def aclose(self) -> None:
        if hasattr(self, "gpt_vision") and self.gpt_vision:
            await self.gpt_vision.aclose()
