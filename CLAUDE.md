# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

This repository currently contains only specification/architecture documents — **no code has been written yet**. There are no build, test, or lint commands to run. Before writing code, consult the relevant spec and confirm tech-stack choices with the user, since these are still on paper.

## What this project is

Personal lyric-writing assistant ("Lyric Assistant") with three components communicating over REST:

```
Mobile App (React Native)  ──REST──>  Python Backend (FastAPI)  <──REST──  Ableton Plugin (Juce/C++)
                                              │
                                              └── PostgreSQL + pgvector
```

- **Mobile app** — friction-free capture of raw thoughts/lyrics, offline-first, push notifications when analysis completes. See [`mobile-app-spec.md`](./mobile-app-spec.md).
- **Python backend** — NLP pipeline (NLTK structural + spaCy semantic), vector embeddings, suggestion generation, runs on the user's HPE DL380 Gen9 homelab. See [`backend-architecture.md`](./backend-architecture.md).
- **Ableton plugin** — in-DAW lyric editor with smart autocomplete and live suggestions. Juce is chosen over Max for Live for full UI/networking depth. See [`ableton-plugin-spec.md`](./ableton-plugin-spec.md).
- **Database** — single PostgreSQL instance with `pgvector` for embeddings; no separate vector DB. Schema in [`database-schema.md`](./database-schema.md).

## Two working modes

The product exposes two complementary modes that the backend must support:

1. **Structural** — syllable counts, rhyme schemes, meter, line length (NLTK).
2. **Semantic** — emotional tone, themes, articulating feelings obliquely (spaCy + embeddings).

These feed into each other (start from a feeling, get structural patterns; start from a skeleton, get semantically appropriate fills). When designing endpoints or features, preserve the ability to enter from either side.

## Non-negotiable product principles

These come from the README and recur across specs — treat them as design constraints, not aspirations:

- **Authenticity over imitation.** Artist-style suggestions are *intentional reference*, never replacement of the user's voice. Authentic-mode (no artist bias) is the default; artist bias is opt-in and must be clearly marked when active.
- **Friction-free capture.** Every additional tap on mobile is a chance to lose an idea. Design for one-screen, one-tap flow.
- **Offline-first on mobile.** Submissions queue locally and sync when connectivity returns.
- **Don't break flow in Ableton.** Suggestions appear when invited; the editor is the focus. Local cache + debounced backend calls keep autocomplete snappy; the plugin must degrade gracefully when the homelab is unreachable.

## Architectural decisions worth knowing before making changes

- **Single Postgres instance with pgvector** instead of a dedicated vector DB. Rationale: keeps homelab ops simple, lets submissions/analyses/embeddings live in one transaction, and pgvector is fine for the expected scale (well under 5M vectors). Migration path to Qdrant/Chroma/Milvus is left open but not pre-built.
- **Embedding dimension is `vector(300)`** in the schema, sized for word2vec/FastText. If switching to sentence-transformers (often 384 or 768), the schema needs updating — don't silently change models without adjusting the column type.
- **Suggestion payloads are `jsonb`** keyed by `suggestion_type` (`rhyme_pattern` / `semantic_alternative` / `next_word` / `artist_style` / `thematic`). Adding a new suggestion type means adding a new value here, not a new table.
- **Juce, not Max for Live**, for the Ableton plugin — because the plugin needs custom UI, REST networking, and depth Max for Live can't easily deliver. Plugin formats are VST3 + AU (macOS Ableton).

## When adding code

- The backend lives alongside an existing `~/Music/music-workspace` Python setup that uses `.venv` + `direnv`. New Python work in this repo should follow the same pattern unless the user says otherwise.
- The user has 12+ years of JS/TS experience and active Python use. Mobile (React Native + TypeScript) and backend (Python 3.11+) play to existing strengths; the Juce/C++ plugin is the area most likely to need extra care.
- Note: `backend-architecture.md` has a typo — "word2fec" should be "word2vec". Worth fixing if touching that file.
