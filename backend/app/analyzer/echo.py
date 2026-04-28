from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SubmissionSuggestion, UserSubmission


async def run_echo_analyzer(submission: UserSubmission, session: AsyncSession) -> None:
    """Stage 1 stub: echo raw input back as a single thematic suggestion.

    Replaced in Stage 2 by the real NLTK + spaCy + embeddings pipeline.
    """
    submission.status = "complete"
    suggestion = SubmissionSuggestion(
        submission_id=submission.id,
        suggestion_type="thematic",
        content={"echo": submission.raw_input},
        confidence_score=1.0,
    )
    session.add(suggestion)
