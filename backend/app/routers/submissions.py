import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzer.echo import run_echo_analyzer
from app.auth import require_token
from app.db import get_session
from app.models import SubmissionSuggestion, UserSubmission
from app.schemas import Submission, SubmissionCreate, Suggestion

router = APIRouter(tags=["submissions"], dependencies=[Depends(require_token)])


@router.post(
    "/submissions",
    response_model=Submission,
    status_code=status.HTTP_201_CREATED,
)
async def create_submission(
    payload: SubmissionCreate,
    session: AsyncSession = Depends(get_session),
) -> UserSubmission:
    submission = UserSubmission(
        raw_input=payload.raw_input,
        mood_tags=payload.mood_tags or None,
        reference_artist=payload.reference_artist,
        source=payload.source,
        status="pending",
    )
    session.add(submission)
    await session.flush()

    # Stage 1: synchronous echo analyzer. Stage 2 moves this to BackgroundTasks.
    await run_echo_analyzer(submission, session)
    await session.commit()
    await session.refresh(submission)
    return submission


@router.get("/submissions/{submission_id}", response_model=Submission)
async def get_submission(
    submission_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> UserSubmission:
    submission = await session.get(UserSubmission, submission_id)
    if submission is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": "Submission not found"},
        )
    return submission


@router.get(
    "/submissions/{submission_id}/suggestions",
    response_model=list[Suggestion],
)
async def get_submission_suggestions(
    submission_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> list[SubmissionSuggestion]:
    submission = await session.get(UserSubmission, submission_id)
    if submission is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": "Submission not found"},
        )
    result = await session.execute(
        select(SubmissionSuggestion).where(
            SubmissionSuggestion.submission_id == submission_id
        )
    )
    return list(result.scalars().all())
