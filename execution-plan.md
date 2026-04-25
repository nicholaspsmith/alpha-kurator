# Execution Plan

## Context

This repo currently contains five spec/architecture documents and **no code**:
- `README.md` — vision, problem statement, three-component architecture
- `backend-architecture.md` — Python/FastAPI + NLTK/spaCy + Postgres/pgvector
- `mobile-app-spec.md` — React Native + TypeScript capture app
- `ableton-plugin-spec.md` — Juce/C++ VST3+AU plugin
- `database-schema.md` — Postgres schema with `vector(300)` embeddings

The product is a personal lyric-writing assistant: mobile capture → Python backend (analysis + embeddings) → Ableton plugin for in-DAW writing. Guiding principle is **authenticity over imitation** — artist-style features are intentional reference, not replacement.

**Decisions confirmed:**
- **Build order:** thinnest end-to-end vertical slice first, then iterate depth into each layer
- **MVP target:** full three-component MVP (all three layers shipping at minimum usefulness)
- **Embeddings:** word2vec/FastText with `vector(300)` — matches the schema as written
- **Auth:** single static bearer token in env (homelab is personal-use, assumed reachable via VPN/Tailscale)

The plan below sequences work so that the integration spine works end-to-end as early as possible, then each component grows depth without breaking the contract.

---

## Progress

Status legend: ⬜ not started · 🟡 in progress · ✅ done · ⏸️ blocked

| Stage | Status | Notes |
|-------|--------|-------|
| 0 — Repo bootstrap & API contract | ✅ | Done 2026-04-25 |
| 1 — Thinnest vertical slice (echo) | ⬜ | Backend ⬜ · Mobile ⬜ · Ableton ⬜ |
| 2 — Backend depth (NLTK + spaCy + embeddings) | ⬜ | |
| 3 — Mobile depth (offline + push + history) | ⬜ | Blocked on APNS/FCM credentials |
| 4 — Ableton plugin depth (autocomplete + panel) | ⬜ | |
| 5 — Homelab deploy + ops | ⬜ | |

**Current focus:** Stage 1 backend slice — Docker Compose, Postgres+pgvector, Alembic migration 0001, FastAPI echo analyzer

**Implementation log** (newest first):
- 2026-04-25 — Stage 0 complete: monorepo dirs created (`backend/`, `mobile/`, `ableton/`, `api-contract/`), root `.gitignore` added, `api-contract/openapi.yaml` written and validated by `@redocly/cli` (3 stylistic warnings accepted: missing license field, localhost server entry for dev, no 4xx on `/healthz` since the endpoint has no validation/auth path). Fixed `word2fec` → `word2vec` typo in `backend-architecture.md` line 80.
- 2026-04-25 — Stage 0 kicked off

This section is updated as work progresses — each completed stage gets ticked off and noteworthy decisions/deviations are appended to the implementation log.

---

## Stage 0 — Repo bootstrap & shared API contract

**Goal:** establish project structure and freeze the v0 API shape so all three components can build against it.

- Top-level layout (monorepo, since the three components share a single API contract):
  ```
  /backend       Python/FastAPI
  /mobile        React Native
  /ableton       Juce/C++ plugin
  /api-contract  OpenAPI spec, shared types reference
  ```
- Write `/api-contract/openapi.yaml` with v0 endpoints:
  - `POST /submissions` — create raw submission (`raw_input`, `mood_tags[]`, `reference_artist?`)
  - `GET /submissions/{id}` — fetch submission + status
  - `GET /submissions/{id}/suggestions` — fetch generated suggestions
  - `GET /reference-songs` / `POST /reference-songs` — manage the reference corpus
  - `GET /artists/{name}/vocabulary` — frequency-weighted vocab for a given artist
  - `POST /autocomplete` — short-context next-word/phrase suggestions for the Ableton plugin
- Auth: `Authorization: Bearer <token>` on every request; token from server env, no DB-side auth table for v0.
- Fix the `word2fec` → `word2vec` typo in `backend-architecture.md` while we're here.

**Done when:** OpenAPI spec lints cleanly and is checked in. No runtime code yet.

---

## Stage 1 — Thinnest vertical slice (capture → echo → display)

**Goal:** prove the integration spine end-to-end with the dumbest possible analysis. No NLP, no embeddings, no DB queries beyond store/fetch.

### Backend (slice)
- `pyproject.toml` with FastAPI, Uvicorn, Pydantic, SQLAlchemy + asyncpg, Alembic. Use `.venv` + `direnv` to match the existing `~/Music/music-workspace` pattern.
- Postgres + `pgvector` running locally via Docker Compose (one service: `db`, one: `api`). Same Compose file will deploy to the DL380 later.
- Alembic migration 0001: `reference_songs`, `song_analysis`, `word_embeddings`, `artist_vocabularies`, `user_submissions`, `submission_suggestions` exactly as in `database-schema.md`. `CREATE EXTENSION vector` in the first migration.
- Implement `POST /submissions`, `GET /submissions/{id}`, `GET /submissions/{id}/suggestions`. The "analyzer" is a stub that synchronously echoes the input back as a single `submission_suggestions` row of type `thematic` with content `{"echo": "<raw_input>"}`.
- Bearer-token auth via FastAPI dependency reading `LYRIC_ASSISTANT_TOKEN` from env.

### Mobile (slice)
- React Native + TypeScript via Expo (faster than bare RN for v0; can eject later if needed).
- Single screen: text input + submit button + a list of past submissions with their echo response.
- Token stored in Expo SecureStore; backend URL configurable in dev.
- No offline queue, no push, no auth UI yet. Just confirm round-trip works against the homelab IP.

### Ableton (slice)
- Juce skeleton via CMake (better long-term than Projucer and matches the spec). Build VST3 + AU on macOS.
- Single panel with a `TextEditor`, a "Submit" button, and a `Label` for the response. Hit `POST /submissions`, poll `GET /submissions/{id}` until `status=complete`, render the echo.
- Networking via Juce `URL`/`WebInputStream`; bearer token compiled in for now.

**Done when:** typing on phone, on the plugin, or via curl all hit the same backend, store a row, and return an identifiable echo. The contract works.

---

## Stage 2 — Backend depth (real analysis + embeddings)

**Goal:** replace the echo stub with the real analysis pipeline against a small seeded reference corpus.

- **Reference song ingestion:** simple `POST /reference-songs` accepting `{title, artist, lyrics, genre[], mood_tags[], notes}`. Seed 5–10 songs manually from the artists in the README (Eminem, Brandon Boyd, Bob Marley, Bradley Nowell). A small CLI script `backend/scripts/seed_reference.py` reads from a local `reference_seed/` folder of `.txt` files with simple frontmatter — easier than building UI for it now.
- **NLTK structural analysis:** rhyme scheme detection (CMU Pronouncing Dictionary), syllable counts, line-length / meter — written into `song_analysis.rhyme_schemes` / `syllable_patterns` / `meter` as jsonb.
- **spaCy semantic analysis:** sentiment, theme keywords, vocabulary frequency, POS tags — written into `song_analysis.emotional_markers` / `vocabulary_frequency` / `thematic_elements`.
- **Embeddings:** load FastText (pretrained `cc.en.300.bin`) at startup. For each token in each reference song, write a `word_embeddings` row with `vector(300)`. Build per-artist `artist_vocabularies` via simple frequency normalization.
- **Index:** create the IVFFlat or HNSW index on `word_embeddings.embedding` and `artist_vocabularies.embedding`. HNSW is faster for queries; spec calls it out as the preferred choice. Use cosine distance (`<=>`).
- **Analyzer pipeline for submissions:** when a submission lands, run NLTK + spaCy on the raw input, then for each significant token:
  - Find K nearest reference tokens via pgvector cosine similarity → `semantic_alternative` suggestions
  - If `reference_artist` is set, weight matches by that artist's `frequency_weight`
  - Detect candidate rhyme groups using CMU dict over the input's last words → `rhyme_pattern` suggestions
- **Async background work:** keep it simple — FastAPI `BackgroundTasks` for v0 (no Celery/RQ yet). Submission status moves `pending → analyzing → complete`. Document the upgrade path in a code comment if/when concurrency demands it.
- **`/autocomplete` endpoint:** takes `{context_text, max_suggestions, reference_artist?}`, embeds the trailing N tokens, returns nearest neighbors filtered to grammatically plausible POS tags. This is what the Ableton plugin will call frequently.

**Done when:** submitting a fragment from curl returns real rhyme suggestions, semantic alternatives, and (if an artist is selected) artist-style hints — all backed by the seeded corpus.

---

## Stage 3 — Mobile depth (offline queue + push + history)

**Goal:** make the mobile app match its spec. Friction-free capture is the north star; offline-first is non-negotiable.

- **Local SQLite** via `expo-sqlite` (or `op-sqlite` if perf demands). Tables: `pending_submissions`, `cached_submissions`, `cached_suggestions`.
- **Offline queue:** every submit writes to `pending_submissions` first; a background sync (on app foreground + network change) flushes to backend and moves rows to `cached_submissions`. No idea is ever lost.
- **Submission history screen:** chronological list, status badge (pending/analyzing/complete), tap to view suggestions inline. Mark favorite via local-only flag for v0 (no backend column needed yet).
- **Mood tag chips + reference-artist picker** on the capture screen. Both optional, both one-tap.
- **Push notifications:** Expo Notifications wired to APNS (iOS) and FCM (Android). Backend gains a `POST /devices` endpoint that stores `(device_id, push_token, platform)` in a new `devices` table; emit a notification when a submission's status flips to `complete`. *Note:* APNS cert / FCM project setup is a manual prerequisite — block this stage until those credentials exist.
- **UI keeps to spec principles:** one-screen capture, one-tap submit, readable suggestion view.

**Done when:** capture works offline on a phone in airplane mode, syncs on reconnect, and a push notification fires when analysis completes.

---

## Stage 4 — Ableton plugin depth (autocomplete + suggestion panel)

**Goal:** match the plugin spec — flow-preserving autocomplete and a side panel of deeper suggestions.

- **Lyric editor view:** full-window `TextEditor` with live syllable / word / line counters. Visual indicators for rhyme groupings as you type (color-coding via `AttributedString`).
- **Smart autocomplete:**
  - On every typing pause (debounced ~150–250ms), POST `/autocomplete` with the last N tokens + selected artist.
  - Render top-K suggestions inline in a dropdown anchored at the caret.
  - Tab/arrow to accept, Esc to dismiss.
  - Maintain a small in-memory LRU of recent (`context_hash → suggestions`) pairs to keep typing snappy and reduce backend chatter.
- **Suggestion panel (side):** triggered by an "Analyze" button or auto-debounced. Shows full suggestion set (rhyme schemes for current line, semantic alternatives, thematic suggestions, artist-style hints if enabled). This calls `POST /submissions` with the current editor content and renders the result.
- **Reference artist selector:** dropdown populated from `GET /artists` (a new tiny endpoint listing distinct artists from the corpus). Default is "Authentic (no bias)" — match the spec's authentic-by-default rule, with an obvious indicator when an artist bias is active.
- **Graceful offline behavior:** if backend unreachable, fall back to a locally-cached vocabulary file (downloaded from `/artists/{name}/vocabulary` on connect) for autocomplete. Suggestion panel disables with a clear "backend unreachable" state.
- **Export:** clipboard, save-to-file, and `POST /submissions` with a `source: "ableton-export"` flag for round-trip into mobile history.
- **Build outputs:** VST3 + AU, signed for local install on macOS Ableton. CMake build target documented in `ableton/README.md`.

**Done when:** writing in Ableton with the plugin loaded gives live autocomplete, an analyze panel, and artist-bias toggling — all driving against the real backend.

---

## Stage 5 — Homelab deployment & operational polish

**Goal:** move from local dev to running on the DL380 Gen9.

- Single `docker-compose.prod.yml` with `db` (postgres + pgvector image) and `api` services. Volumes for Postgres data and the FastText model file (don't bake the multi-GB model into the image).
- systemd unit that runs `docker compose up -d` on boot — chosen over bare systemd-managed processes because Compose already gives clean lifecycle management for the two services together.
- `.env.production` with `LYRIC_ASSISTANT_TOKEN`, `DATABASE_URL`, `FASTTEXT_MODEL_PATH`. Never committed.
- Mobile and Ableton clients point at the homelab via Tailscale hostname (recommended) or LAN IP if used at home only.
- Light operational tooling: a `backend/scripts/backup_db.sh` cron that pg_dumps to a known path; a `/healthz` endpoint returning DB + model load status.

**Done when:** rebooting the DL380 brings the API back automatically, mobile and plugin reconnect, and a fresh submission round-trips successfully.

---

## Critical files (to be created)

- `api-contract/openapi.yaml`
- `backend/pyproject.toml`, `backend/app/main.py`, `backend/app/db.py`, `backend/app/models.py`, `backend/app/analyzer/{nltk_pipeline.py,spacy_pipeline.py,embeddings.py}`, `backend/alembic/versions/0001_initial.py`, `backend/scripts/seed_reference.py`
- `mobile/app.json`, `mobile/src/screens/{CaptureScreen.tsx,HistoryScreen.tsx}`, `mobile/src/db/queue.ts`, `mobile/src/api/client.ts`, `mobile/src/notifications/index.ts`
- `ableton/CMakeLists.txt`, `ableton/Source/PluginProcessor.cpp`, `ableton/Source/PluginEditor.cpp`, `ableton/Source/Net/BackendClient.cpp`, `ableton/Source/UI/{Editor,SuggestionPanel,AutocompleteOverlay}.cpp`
- `docker-compose.yml` (dev), `docker-compose.prod.yml`, `.env.example`

## Reuse / external dependencies

No existing internal code to reuse — greenfield. External libraries to lean on rather than reimplement:
- **NLTK** for rhyme/syllable/meter (CMU dict)
- **spaCy** `en_core_web_md` for semantic analysis (avoid `_lg` for now to keep RAM modest on the DL380)
- **gensim** to load FastText `cc.en.300.bin`
- **pgvector** Python client (`pgvector-asyncpg`) — don't hand-roll vector queries
- **Expo** + `expo-sqlite` + `expo-notifications` on mobile
- **Juce** modules: `juce_gui_basics`, `juce_audio_plugin_client`, `juce_core` (for `URL`/`WebInputStream`)

---

## Verification

End-to-end test (run after Stage 4 completes; partial versions runnable after each stage):

1. **Backend up:** `docker compose up -d`, then `curl -H "Authorization: Bearer $TOKEN" http://homelab:8000/healthz` returns 200.
2. **Reference corpus seeded:** `python backend/scripts/seed_reference.py reference_seed/` ingests 5–10 songs; `curl /reference-songs` lists them.
3. **Submission round-trip from curl:**
   ```
   curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d '{"raw_input":"frustrated nobody listens about the planet", "reference_artist":"Bob Marley"}' \
     http://homelab:8000/submissions
   ```
   then poll `/submissions/{id}` until `status=complete`, then `/submissions/{id}/suggestions` returns rhyme + semantic + artist-style entries.
4. **Mobile offline test:** put phone in airplane mode, submit three captures, return to wifi, confirm all three appear in history with `complete` status and a push notification fires.
5. **Ableton autocomplete test:** open a Live project with the plugin loaded, type a line — autocomplete dropdown appears within ~250ms, Tab accepts, "Analyze" populates the side panel with rhyme/semantic/artist suggestions.
6. **Auth test:** repeat (3) without the bearer header — confirm 401.
7. **Resilience test:** stop the `api` container; confirm the plugin falls back to cached-vocabulary autocomplete and the panel shows a clear offline state.

Each stage should be runnable and demoable on its own — that's the point of the thin-slice-first sequencing.
