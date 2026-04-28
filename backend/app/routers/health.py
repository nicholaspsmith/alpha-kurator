from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.schemas import Health

router = APIRouter(tags=["system"])


@router.get("/healthz", response_model=Health)
async def get_health(
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> Health:
    settings = get_settings()
    db_state: str = "up"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_state = "down"

    overall = "ok" if db_state == "up" else "degraded"
    if overall != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return Health(
        status=overall,
        db=db_state,
        embedding_model="unavailable",  # Stage 1: no model loaded yet
        version=settings.version,
    )
