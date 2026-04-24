# Backend Architecture

## Overview

The Python backend runs on the existing HPE DL380 Gen9 homelab server and handles all heavy lifting: analyzing reference songs, processing user input, generating suggestions, and serving data to the mobile app and Ableton plugin via a REST API.

## Core Components

### Lyric Analysis Engine

**NLTK — structural analysis:**
- Rhyme scheme detection
- Syllable counting
- Line length and meter patterns
- Phonetic similarity (CMU Pronouncing Dictionary)

**spaCy — semantic analysis:**
- Emotional tone and sentiment
- Thematic content extraction
- Vocabulary complexity and diversity
- Named entity and context recognition
- Part-of-speech tagging for grammar-aware suggestions

Returns structured data describing *what* makes reference songs work both technically and emotionally.

### Reference Song Indexing System

- Builds a database of analyzed reference songs you provide
- Extracts patterns: rhyme schemes, vocabulary frequency, emotional markers, thematic elements
- Creates frequency-weighted artist vocabularies for autocomplete and style inspiration
- Indexes everything for fast retrieval and comparison

### Vector Embedding System

- Uses **word2vec** or **FastText** to tokenize and embed all lyrical words and phrases from reference songs
- Stores embeddings in PostgreSQL via the **pgvector** extension
- Creates a semantic graph where similar words and concepts cluster together
- Enables intelligent suggestions based on meaning, not just frequency
- Powers context-aware next-word predictions in the Ableton autocomplete

### REST API Layer

- **FastAPI** handles requests from mobile and Ableton clients
- Async-friendly, auto-generated OpenAPI docs, type-safe via Pydantic
- Endpoints for:
  - Submitting raw input
  - Requesting analysis
  - Fetching suggestions
  - Managing reference songs and artist vocabularies
- Returns structured JSON: suggestions, patterns, semantic alternatives, artist-style hints

### Database

- **PostgreSQL with pgvector extension**
- Single database for everything: analyzed songs, user submissions, suggestions, vector embeddings, artist vocabularies
- Keeps infrastructure simple — no separate vector database to operate
- pgvector handles similarity search efficiently for the volumes expected here (well under 5M vectors)

## Data Flow

1. User submits raw thought or lyric fragment from mobile app
2. Backend stores submission, queues analysis
3. Analysis pipeline runs:
   - NLTK extracts structural patterns from input
   - spaCy extracts semantic and emotional content
   - Vector embeddings find semantically related words/phrases from reference library
   - Optional artist-style filter ranks suggestions by selected artist's vocabulary
4. Returns structured suggestions: rhyme patterns, semantic alternatives, next-word predictions, artist-style hints
5. Ableton plugin fetches and displays suggestions; mobile app shows preview via push notification
6. All results stored for future reference and learning

## Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ |
| API framework | FastAPI |
| NLP — structural | NLTK |
| NLP — semantic | spaCy |
| Embeddings | word2fec / FastText (or sentence-transformers if richer embeddings needed) |
| Database | PostgreSQL with pgvector extension |
| Process management | systemd or Docker Compose on DL380 |
| Hosting | HPE DL380 Gen9 homelab server |

## Why Python

- Strongest NLP ecosystem of any language — NLTK, spaCy, gensim, HuggingFace, sentence-transformers all live here
- Existing developer expertise (12+ years JS/TS, plus active Python use in `~/Music/music-workspace` for stem separation and audio analysis)
- Fits cleanly alongside the existing music-workspace `.venv` + `direnv` setup
- Easy to integrate with future ML/embedding model upgrades

## Why pgvector (not a dedicated vector DB)

- Single database keeps homelab ops simple — no extra service to monitor
- Submissions, analyses, and embeddings live in the same transaction
- pgvector is performant for the expected scale (well under millions of vectors)
- Easy migration path to Qdrant, Chroma, or Milvus later if scale demands it
