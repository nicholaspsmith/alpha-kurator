import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    ForeignKey,
    Integer,
    Real,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

EMBEDDING_DIM = 300


class ReferenceSong(Base):
    __tablename__ = "reference_songs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    artist: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    lyrics: Mapped[str] = mapped_column(Text, nullable=False)
    genre: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    mood_tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    analysis_date: Mapped[datetime | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(Text)


class SongAnalysis(Base):
    __tablename__ = "song_analysis"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reference_song_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reference_songs.id", ondelete="CASCADE"),
        index=True,
    )
    rhyme_schemes: Mapped[dict | None] = mapped_column(JSONB)
    syllable_patterns: Mapped[dict | None] = mapped_column(JSONB)
    meter: Mapped[dict | None] = mapped_column(JSONB)
    emotional_markers: Mapped[dict | None] = mapped_column(JSONB)
    vocabulary_frequency: Mapped[dict | None] = mapped_column(JSONB)
    thematic_elements: Mapped[dict | None] = mapped_column(JSONB)


class WordEmbedding(Base):
    __tablename__ = "word_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    word_or_phrase: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    source_song_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reference_songs.id", ondelete="CASCADE")
    )
    frequency_count: Mapped[int | None] = mapped_column(Integer)


class ArtistVocabulary(Base):
    __tablename__ = "artist_vocabularies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    artist_name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    word: Mapped[str] = mapped_column(Text, nullable=False)
    frequency_weight: Mapped[float] = mapped_column(Real, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM))


class UserSubmission(Base):
    __tablename__ = "user_submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    submission_date: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), index=True
    )
    mood_tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    reference_artist: Mapped[str | None] = mapped_column(Text)
    analysis_requested: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="api")

    suggestions: Mapped[list["SubmissionSuggestion"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )


class SubmissionSuggestion(Base):
    __tablename__ = "submission_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_submissions.id", ondelete="CASCADE"),
        index=True,
    )
    suggestion_type: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Real, nullable=False)
    created_date: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    submission: Mapped[UserSubmission] = relationship(back_populates="suggestions")
