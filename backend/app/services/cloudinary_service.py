"""Backend-mediated Cloudinary uploads with rollback on a partial failure."""

from __future__ import annotations

import asyncio
import io
import uuid
from datetime import datetime, timezone
from typing import Iterable, List

from app.core.config import settings
from app.models.schemas import ProblemImage
from app.services.image_processing_service import PreparedImage


class CloudinaryStorageError(RuntimeError):
    pass


class CloudinaryStorageService:
    @staticmethod
    def is_configured() -> bool:
        if bool(settings.CLOUDINARY_URL):
            return True
        return bool(
            settings.CLOUDINARY_CLOUD_NAME
            and settings.CLOUDINARY_API_KEY
            and settings.CLOUDINARY_API_SECRET
        )

    @classmethod
    def get_configuration_status(cls) -> dict[str, object]:
        has_url = bool(settings.CLOUDINARY_URL)
        has_api_key = bool(settings.CLOUDINARY_API_KEY) or has_url
        has_cloud_name = bool(settings.CLOUDINARY_CLOUD_NAME) or has_url
        has_api_secret = bool(settings.CLOUDINARY_API_SECRET) or has_url
        missing: list[str] = []
        if not has_cloud_name:
            missing.append("CLOUDINARY_CLOUD_NAME")
        if not has_api_key:
            missing.append("CLOUDINARY_API_KEY")
        if not has_api_secret:
            missing.append("CLOUDINARY_API_SECRET")
        return {
            "configured": cls.is_configured(),
            "has_api_key": has_api_key,
            "has_cloud_name": has_cloud_name,
            "has_api_secret": has_api_secret,
            "missing_credentials": missing,
        }

    @classmethod
    def verify_connection(cls) -> dict[str, object]:
        """Perform a safe minimal ping to Cloudinary API if credentials are provided."""
        if not cls.is_configured():
            status = cls.get_configuration_status()
            missing = status.get("missing_credentials", [])
            return {
                "connected": False,
                "reason": f"Missing required configuration: {', '.join(missing) if missing else 'credentials'}",
            }
        try:
            import cloudinary
            import cloudinary.api
            if settings.CLOUDINARY_URL:
                cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL, secure=True)
            else:
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                    api_key=settings.CLOUDINARY_API_KEY,
                    api_secret=settings.CLOUDINARY_API_SECRET,
                    secure=True,
                )
            result = cloudinary.api.ping()
            return {"connected": True, "status": result.get("status", "ok")}
        except Exception as exc:
            return {"connected": False, "error": str(exc)}

    @classmethod
    async def upload_images(cls, case_id: str, images: Iterable[PreparedImage]) -> List[ProblemImage]:
        if not cls.is_configured():
            status = cls.get_configuration_status()
            missing = status.get("missing_credentials", [])
            missing_msg = f" Missing required: {', '.join(missing)}." if missing else ""
            raise CloudinaryStorageError(
                f"Image storage is not fully configured.{missing_msg} Add CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in backend/.env."
            )
        return await asyncio.to_thread(cls._upload_images_sync, case_id, list(images))

    @classmethod
    def _upload_images_sync(cls, case_id: str, images: List[PreparedImage]) -> List[ProblemImage]:
        try:
            import cloudinary
            import cloudinary.uploader
            import cloudinary.utils
        except ImportError as exc:  # Clear operational feedback if dependencies were not installed.
            raise CloudinaryStorageError("Cloudinary SDK is unavailable. Install backend requirements first.") from exc

        if settings.CLOUDINARY_URL:
            cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL, secure=True)
        else:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )
        uploaded_public_ids: List[str] = []
        assets: List[ProblemImage] = []
        try:
            for image in images:
                image_id = uuid.uuid4().hex
                public_id = f"{settings.CLOUDINARY_FOLDER_PREFIX}/{case_id}/{image_id}"
                result = cloudinary.uploader.upload(
                    io.BytesIO(image.content),
                    public_id=public_id,
                    resource_type="image",
                    overwrite=False,
                    unique_filename=False,
                    use_filename=False,
                    context={"case_id": case_id, "source": "resolveai"},
                )
                saved_public_id = result["public_id"]
                uploaded_public_ids.append(saved_public_id)
                thumbnail_url, _ = cloudinary.utils.cloudinary_url(
                    saved_public_id,
                    secure=True,
                    transformation=[{"width": 480, "height": 320, "crop": "fill", "quality": "auto", "fetch_format": "auto"}],
                )
                assets.append(
                    ProblemImage(
                        id=image_id,
                        public_id=saved_public_id,
                        secure_url=result["secure_url"],
                        thumbnail_url=thumbnail_url,
                        original_filename=image.original_filename,
                        content_type=image.content_type,
                        byte_size=len(image.content),
                        width=image.width,
                        height=image.height,
                        perceptual_hash=image.perceptual_hash,
                        blur_variance=image.blur_variance,
                        quality_warning=image.quality_warning,
                        uploaded_at=datetime.now(timezone.utc).isoformat(),
                        visual_analysis=image.visual_analysis,
                    )
                )
            return assets
        except Exception as exc:
            # Do not leave a partially-created report with unreachable orphan evidence.
            for public_id in uploaded_public_ids:
                try:
                    cloudinary.uploader.destroy(public_id, resource_type="image", invalidate=True)
                except Exception:
                    pass
            raise CloudinaryStorageError("Cloudinary could not store the uploaded evidence. No partial upload was retained.") from exc

    @classmethod
    async def delete_images(cls, images: Iterable[ProblemImage]) -> None:
        if not cls.is_configured():
            raise CloudinaryStorageError("Image storage is not configured, so evidence cannot be deleted safely.")
        await asyncio.to_thread(cls._delete_images_sync, list(images))

    @staticmethod
    def _delete_images_sync(images: List[ProblemImage]) -> None:
        try:
            import cloudinary.uploader
            for image in images:
                result = cloudinary.uploader.destroy(image.public_id, resource_type="image", invalidate=True)
                if result.get("result") not in {"ok", "not found"}:
                    raise CloudinaryStorageError("Cloudinary did not confirm evidence deletion.")
        except CloudinaryStorageError:
            raise
        except Exception as exc:
            raise CloudinaryStorageError("Cloudinary could not delete the evidence; database records were left unchanged.") from exc
