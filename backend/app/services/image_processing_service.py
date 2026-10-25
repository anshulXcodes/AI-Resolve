"""Safe OpenCV processing for campus-report evidence.

This service deliberately uses computer vision for image integrity and visual
similarity only. It does not claim to classify a campus issue from a photo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import cv2
import numpy as np
from fastapi import UploadFile

from app.core.config import settings


class ImageValidationError(ValueError):
    """Raised for a client-provided image that is unsafe or unsupported."""


@dataclass
class PreparedImage:
    original_filename: str
    content_type: str
    content: bytes
    width: int
    height: int
    perceptual_hash: str
    blur_variance: float
    quality_warning: str | None
    visual_analysis: dict[str, object] | None = None


class ImageProcessingService:
    _SIGNATURES = {
        "image/jpeg": lambda data: data.startswith(b"\xff\xd8\xff"),
        "image/png": lambda data: data.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": lambda data: len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP",
    }

    @classmethod
    async def prepare_uploads(cls, files: Iterable[UploadFile]) -> List[PreparedImage]:
        files = list(files)
        if len(files) > settings.MAX_IMAGES_PER_CASE:
            raise ImageValidationError(
                f"A report can contain at most {settings.MAX_IMAGES_PER_CASE} images."
            )
        return [await cls.prepare_upload(file) for file in files]

    @classmethod
    async def prepare_upload(cls, upload: UploadFile) -> PreparedImage:
        # Read a bounded amount, rather than trusting an unbounded multipart part.
        content = await upload.read(settings.MAX_IMAGE_BYTES + 1)
        await upload.close()
        if not content:
            raise ImageValidationError("One selected image was empty.")
        if len(content) > settings.MAX_IMAGE_BYTES:
            raise ImageValidationError(
                f"{upload.filename or 'Image'} exceeds the {settings.MAX_IMAGE_BYTES // (1024 * 1024)} MB limit."
            )

        actual_type = cls._detect_content_type(content)
        if not actual_type:
            raise ImageValidationError("Upload a real JPG, PNG, or WEBP image; the file contents could not be verified.")

        # Reject common decompression-bomb dimensions before cv2 allocates a
        # full BGR matrix. Decode remains the final source of truth below.
        declared_dimensions = cls._read_declared_dimensions(content, actual_type)
        if declared_dimensions and declared_dimensions[0] * declared_dimensions[1] > settings.MAX_IMAGE_PIXELS:
            raise ImageValidationError("Image dimensions are too large to process safely. Please resize and try again.")

        image = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None or image.size == 0:
            raise ImageValidationError("The image is corrupted or could not be decoded safely.")

        height, width = image.shape[:2]
        if width < settings.MIN_IMAGE_DIMENSION or height < settings.MIN_IMAGE_DIMENSION:
            raise ImageValidationError(
                f"Images must be at least {settings.MIN_IMAGE_DIMENSION}×{settings.MIN_IMAGE_DIMENSION} pixels."
            )
        if width * height > settings.MAX_IMAGE_PIXELS:
            raise ImageValidationError("Image dimensions are too large to process safely. Please resize and try again.")

        normalized = cls._normalize_for_features(image)
        grayscale = cv2.cvtColor(normalized, cv2.COLOR_BGR2GRAY)
        blur_variance = float(cv2.Laplacian(grayscale, cv2.CV_64F).var())
        mean_brightness = float(np.mean(grayscale))
        contrast = float(np.std(grayscale))

        quality_warning = None
        if blur_variance < settings.BLUR_VARIANCE_THRESHOLD:
            quality_warning = "Image appears blurry; it was retained but may require manual review."
        elif mean_brightness < 35:
            quality_warning = "Image appears underexposed/dark; retained for review."
        elif mean_brightness > 225:
            quality_warning = "Image appears overexposed; retained for review."

        visual_analysis = {
            "brightness": round(mean_brightness, 1),
            "contrast": round(contrast, 1),
            "sharpness": round(blur_variance, 1),
            "resolution": f"{width}x{height}",
            "aspect_ratio": round(width / max(1, height), 2),
            "is_blurry": blur_variance < settings.BLUR_VARIANCE_THRESHOLD,
            "is_dark": mean_brightness < 35,
            "is_overexposed": mean_brightness > 225,
        }

        return PreparedImage(
            original_filename=upload.filename or "campus-evidence",
            content_type=actual_type,
            content=content,
            width=width,
            height=height,
            perceptual_hash=cls._difference_hash(normalized),
            blur_variance=round(blur_variance, 2),
            quality_warning=quality_warning,
            visual_analysis=visual_analysis,
        )

    @classmethod
    def _detect_content_type(cls, content: bytes) -> str | None:
        for content_type, matches in cls._SIGNATURES.items():
            if matches(content):
                return content_type
        return None

    @staticmethod
    def _read_declared_dimensions(content: bytes, content_type: str) -> tuple[int, int] | None:
        """Read lightweight headers before decoding; malformed data falls through to cv2."""
        if content_type == "image/png" and len(content) >= 24:
            return int.from_bytes(content[16:20], "big"), int.from_bytes(content[20:24], "big")
        if content_type == "image/jpeg":
            index = 2
            # JPEG stores dimensions in a Start Of Frame marker. Cap scanning
            # to the small header region so crafted metadata cannot add work.
            while index + 9 < min(len(content), 256 * 1024):
                if content[index] != 0xFF:
                    index += 1
                    continue
                marker = content[index + 1]
                index += 2
                while marker == 0xFF and index < len(content):
                    marker = content[index]
                    index += 1
                if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
                    continue
                if index + 2 > len(content):
                    return None
                segment_length = int.from_bytes(content[index:index + 2], "big")
                if segment_length < 2 or index + segment_length > len(content):
                    return None
                if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                    return (
                        int.from_bytes(content[index + 7:index + 9], "big"),
                        int.from_bytes(content[index + 5:index + 7], "big"),
                    )
                index += segment_length
        if content_type == "image/webp" and len(content) >= 30:
            chunk = content[12:16]
            if chunk == b"VP8X":
                width = 1 + int.from_bytes(content[24:27], "little")
                height = 1 + int.from_bytes(content[27:30], "little")
                return width, height
            if chunk == b"VP8 " and len(content) >= 30:
                return int.from_bytes(content[26:28], "little") & 0x3FFF, int.from_bytes(content[28:30], "little") & 0x3FFF
        return None

    @staticmethod
    def _normalize_for_features(image: np.ndarray) -> np.ndarray:
        """Resize only the analysis copy; Cloudinary receives the original evidence."""
        height, width = image.shape[:2]
        largest = max(height, width)
        if largest <= settings.MAX_IMAGE_DIMENSION:
            return image
        scale = settings.MAX_IMAGE_DIMENSION / largest
        return cv2.resize(
            image,
            (max(1, round(width * scale)), max(1, round(height * scale))),
            interpolation=cv2.INTER_AREA,
        )

    @staticmethod
    def _difference_hash(image: np.ndarray) -> str:
        """A portable 64-bit dHash, implemented with cv2 rather than cv2-contrib."""
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(grayscale, (9, 8), interpolation=cv2.INTER_AREA)
        bits = resized[:, 1:] > resized[:, :-1]
        packed = np.packbits(bits.astype(np.uint8).reshape(-1))
        return packed.tobytes().hex()

    @staticmethod
    def hash_similarity(first_hash: str, second_hash: str) -> float:
        if not first_hash or not second_hash or len(first_hash) != len(second_hash):
            return 0.0
        first = int(first_hash, 16)
        second = int(second_hash, 16)
        bit_count = len(first_hash) * 4
        return round(1 - ((first ^ second).bit_count() / bit_count), 3)
