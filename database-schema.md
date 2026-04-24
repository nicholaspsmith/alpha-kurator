# Database Schema

## Overview

PostgreSQL with the **pgvector** extension stores all analyzed songs, user submissions, suggestions, vector embeddings, and artist vocabularies. Single source of truth for the growing library of learnings.

## Core Tables

### `reference_songs`

Stores reference songs you've added for analysis.

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `title` | `text` | |
| `artist` | `text` | |
| `lyrics` | `text` | Full lyrics |
| `genre` | `text[]` | |
| `mood_tags` | `text[]` | Free-form tags |
| `analysis_date` | `timestamptz` | |
| `notes` | `text` | Personal notes on why this song matters to you |

### `song_analysis`

Extracted patterns from each reference song.

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `reference_song_id` | `uuid` FK → `reference_songs.id` | |
| `rhyme_schemes` | `jsonb` | Per-section rhyme patterns |
| `syllable_patterns` | `jsonb` | Syllable counts per line/section |
| `meter` | `jsonb` | Stress patterns |
| `emotional_markers` | `jsonb` | Sentiment, emotional arc |
| `vocabulary_frequency` | `jsonb` | Word frequency map |
| `thematic_elements` | `jsonb` | Themes, motifs, subjects |

### `word_embeddings`

Vector embeddings for words and phrases drawn from reference songs.

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `word_or_phrase` | `text` | |
| `embedding` | `vector(300)` | pgvector type; dimension matches model |
| `source_song_id` | `uuid` FK → `reference_songs.id` | Nullable for global vocabulary |
| `frequency_count` | `integer` | |

### `artist_vocabularies`

Pre-computed frequency-weighted vocabularies per artist.

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `artist_name` | `text` | |
| `word` | `text` | |
| `frequency_weight` | `real` | Normalized 0–1 |
| `embedding` | `vector(300)` | |

### `user_submissions`

Raw input submitted from mobile app.

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `raw_input` | `text` | |
| `submission_date` | `timestamptz` | |
| `mood_tags` | `text[]` | |
| `reference_artist` | `text` | Nullable; selected at submission time |
| `analysis_requested` | `boolean` | |
| `status` | `text` | `pending` / `analyzing` / `complete` / `failed` |

### `submission_suggestions`

Generated suggestions for each submission.

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `submission_id` | `uuid` FK → `user_submissions.id` | |
| `suggestion_type` | `text` | `rhyme_pattern` / `semantic_alternative` / `next_word` / `artist_style` / `thematic` |
| `content` | `jsonb` | Type-specific payload |
| `confidence_score` | `real` | 0–1 |
| `created_date` | `timestamptz` | |

## Indexes

- `word_embeddings(embedding)` — IVFFlat or HNSW index via pgvector for fast similarity search
- `artist_vocabularies(embedding)` — same approach
- `artist_vocabularies(artist_name)` — B-tree for fast artist lookup
- `song_analysis(reference_song_id)` — B-tree
- `user_submissions(submission_date DESC)` — for chronological browsing
- `submission_suggestions(submission_id)` — for fast suggestion retrieval
- `reference_songs(artist)` — B-tree

## Notes on pgvector

- Use `CREATE EXTENSION IF NOT EXISTS vector;` to enable
- Embedding dimension (`vector(300)`) should match the chosen embedding model — adjust if using sentence-transformers (often 384 or 768)
- HNSW index is generally faster for queries; IVFFlat is simpler and adequate for this scale
- Cosine similarity (`<=>` operator) is the default for normalized embeddings
