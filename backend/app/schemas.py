import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SubmissionStatus = Literal["pending", "analyzing", "complete", "failed"]
SubmissionSource = Literal["mobile", "ableton-export", "api"]
SuggestionType = Literal[
    "rhyme_pattern", "semantic_alternative", "next_word", "artist_style", "thematic"
]


class Health(BaseModel):
    status: Literal["ok", "degraded"]
    db: Literal["up", "down"]
    embedding_model: Literal["loaded", "loading", "unavailable"]
    version: str


class SubmissionCreate(BaseModel):
    raw_input: str = Field(min_length=1, max_length=10000)
    mood_tags: list[str] = Field(default_factory=list)
    reference_artist: str | None = None
    source: SubmissionSource = "api"


class Submission(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    raw_input: str
    status: SubmissionStatus
    submission_date: datetime
    mood_tags: list[str] = Field(default_factory=list)
    reference_artist: str | None = None
    source: SubmissionSource


class Suggestion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    submission_id: uuid.UUID
    suggestion_type: SuggestionType
    content: dict[str, Any]
    confidence_score: float
    created_date: datetime
