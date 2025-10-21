"""File operations endpoints."""

import logging
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class FileContent(BaseModel):
    """Request model for file updates."""

    content: str


@router.get("/roadmap")
async def get_roadmap() -> Dict[str, str]:
    """Get ROADMAP.md content."""
    roadmap_path = Path("/workspace/docs/roadmap/ROADMAP.md")

    if not roadmap_path.exists():
        raise HTTPException(status_code=404, detail="ROADMAP.md not found")

    content = roadmap_path.read_text()
    return {"path": str(roadmap_path), "content": content}


@router.put("/roadmap")
async def update_roadmap(file: FileContent) -> Dict[str, str]:
    """Update ROADMAP.md content."""
    roadmap_path = Path("/workspace/docs/roadmap/ROADMAP.md")

    try:
        roadmap_path.write_text(file.content)
        logger.info("ROADMAP.md updated successfully")
        return {"status": "success", "message": "ROADMAP.md updated"}
    except Exception as e:
        logger.error(f"Failed to update ROADMAP.md: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_path:path}")
async def get_file(file_path: str) -> Dict[str, str]:
    """Get project file content."""
    full_path = Path("/workspace") / file_path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    if not full_path.is_file():
        raise HTTPException(status_code=400, detail=f"Not a file: {file_path}")

    content = full_path.read_text()
    return {"path": str(full_path), "content": content}


@router.put("/{file_path:path}")
async def update_file(file_path: str, file: FileContent) -> Dict[str, str]:
    """Update project file content."""
    full_path = Path("/workspace") / file_path

    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(file.content)
        logger.info(f"File updated: {file_path}")
        return {"status": "success", "message": f"File updated: {file_path}"}
    except Exception as e:
        logger.error(f"Failed to update file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
