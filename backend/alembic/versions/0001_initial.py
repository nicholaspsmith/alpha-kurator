"""initial schema with pgvector

Revision ID: 0001
Revises:
Create Date: 2026-04-25
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBEDDING_DIM = 300


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "reference_songs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("artist", sa.Text(), nullable=False),
        sa.Column("lyrics", sa.Text(), nullable=False),
        sa.Column("genre", postgresql.ARRAY(sa.Text())),
        sa.Column("mood_tags", postgresql.ARRAY(sa.Text())),
        sa.Column("analysis_date", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text()),
    )
    op.create_index("ix_reference_songs_artist", "reference_songs", ["artist"])

    op.create_table(
        "song_analysis",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "reference_song_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reference_songs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rhyme_schemes", postgresql.JSONB()),
        sa.Column("syllable_patterns", postgresql.JSONB()),
        sa.Column("meter", postgresql.JSONB()),
        sa.Column("emotional_markers", postgresql.JSONB()),
        sa.Column("vocabulary_frequency", postgresql.JSONB()),
        sa.Column("thematic_elements", postgresql.JSONB()),
    )
    op.create_index(
        "ix_song_analysis_reference_song_id", "song_analysis", ["reference_song_id"]
    )

    op.create_table(
        "word_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("word_or_phrase", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM)),
        sa.Column(
            "source_song_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reference_songs.id", ondelete="CASCADE"),
        ),
        sa.Column("frequency_count", sa.Integer()),
    )
    # IVFFlat is enough for the corpus size at v0; HNSW is a small migration later.
    op.execute(
        "CREATE INDEX ix_word_embeddings_embedding "
        "ON word_embeddings USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )

    op.create_table(
        "artist_vocabularies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("artist_name", sa.Text(), nullable=False),
        sa.Column("word", sa.Text(), nullable=False),
        sa.Column("frequency_weight", sa.Float()),
        sa.Column("embedding", Vector(EMBEDDING_DIM)),
    )
    op.create_index(
        "ix_artist_vocabularies_artist_name", "artist_vocabularies", ["artist_name"]
    )
    op.execute(
        "CREATE INDEX ix_artist_vocabularies_embedding "
        "ON artist_vocabularies USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )

    op.create_table(
        "user_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("raw_input", sa.Text(), nullable=False),
        sa.Column(
            "submission_date",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("mood_tags", postgresql.ARRAY(sa.Text())),
        sa.Column("reference_artist", sa.Text()),
        sa.Column("analysis_requested", sa.Boolean(), server_default=sa.true()),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="api"),
    )
    op.create_index(
        "ix_user_submissions_submission_date",
        "user_submissions",
        [sa.text("submission_date DESC")],
    )

    op.create_table(
        "submission_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "submission_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("user_submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("suggestion_type", sa.String(length=64), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column(
            "created_date",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_submission_suggestions_submission_id",
        "submission_suggestions",
        ["submission_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_submission_suggestions_submission_id", table_name="submission_suggestions")
    op.drop_table("submission_suggestions")
    op.drop_index("ix_user_submissions_submission_date", table_name="user_submissions")
    op.drop_table("user_submissions")
    op.execute("DROP INDEX IF EXISTS ix_artist_vocabularies_embedding")
    op.drop_index("ix_artist_vocabularies_artist_name", table_name="artist_vocabularies")
    op.drop_table("artist_vocabularies")
    op.execute("DROP INDEX IF EXISTS ix_word_embeddings_embedding")
    op.drop_table("word_embeddings")
    op.drop_index("ix_song_analysis_reference_song_id", table_name="song_analysis")
    op.drop_table("song_analysis")
    op.drop_index("ix_reference_songs_artist", table_name="reference_songs")
    op.drop_table("reference_songs")
    op.execute("DROP EXTENSION IF EXISTS vector")
