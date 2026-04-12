"""
HomeGuardian AI — Clip Routes
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from auth import get_current_user
from services.clip_service import clip_extractor

router = APIRouter()


@router.get("/{anomaly_id}")
async def get_clip_metadata(anomaly_id: int, user: dict = Depends(get_current_user)):
    """Get clip metadata for an anomaly event."""
    metadata = clip_extractor.get_clip_metadata(anomaly_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Clip not found for this anomaly")
    return metadata


@router.get("/{anomaly_id}/download")
async def download_clip(anomaly_id: int, user: dict = Depends(get_current_user)):
    """Download the clip MP4 file."""
    metadata = clip_extractor.get_clip_metadata(anomaly_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Clip not found")

    clip_path = Path(metadata["clip_path"])
    if not clip_path.exists():
        raise HTTPException(status_code=404, detail="Clip file not found on disk")

    return FileResponse(
        path=str(clip_path),
        media_type="video/mp4",
        filename=clip_path.name
    )
