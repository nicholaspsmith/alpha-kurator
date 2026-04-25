# Lyric Assistant

A personal lyric-writing tool designed to help transform raw emotions, thoughts, and ideas into artful, authentic music. This system combines linguistic analysis, semantic understanding, and creative inspiration drawn from artists you admire to amplify your unique voice — never to replace it.

## Vision

You have genuine feelings and perspectives you want to express through music, but articulating them lyrically in a way that feels natural, clever, and not too on-the-nose is hard. This tool helps you study how artists you love craft their messages, then applies those learnings to help refine your own voice into something more compelling, layered, and uniquely yours.

The guiding principle: **everything output by this tool stays authentic to your voice.** Artist references, semantic analysis, and structural patterns are scaffolding — never replacements for genuine human expression.

## Problem Statement

Going from raw emotion to polished lyric is genuinely hard. You know what you want to say, but finding the right words, structure, and artistry takes time and iteration. Inspiration also rarely strikes when you're conveniently in front of your DAW — it hits in bed, in the car, on a walk. You want a tool that:

- Captures raw thoughts the moment they happen, anywhere
- Analyzes lyrics from artists you admire to understand *why* they work
- Helps you articulate your own ideas more artfully without losing your voice
- Integrates directly into your music-making workflow when you're ready to write

## Core Features

### MVP

- **Mobile capture app** — Quick thought dumps whenever inspiration strikes, with offline support
- **Python backend on homelab** — Linguistic analysis (NLTK), semantic understanding (spaCy), and vector embeddings for intelligent suggestions
- **Ableton plugin (Juce)** — In-DAW editor with smart autocomplete and suggestions integrated into the writing workflow

### Stretch Goals

- **Frequency-weighted artist vocabularies** — Suggest words in the style of artists like Eminem, Brandon Boyd, Bob Marley, Bradley Nowell, etc., as intentional reference rather than imitation
- **Vector embedding graph** — Semantic-aware word and phrase suggestions using word2vec / FastText
- **Style transfer models** — More advanced ML-driven artist-style suggestions
- **Advanced thematic analysis** — Emotional arcs, narrative structure, undertones, layered meaning

## High-Level Architecture

Three layers, communicating via REST API:

```
┌─────────────────┐         ┌──────────────────────┐         ┌─────────────────────┐
│  Mobile App     │ ──────> │  Python Backend      │ <────── │  Ableton Plugin     │
│  (React Native) │  REST   │  (FastAPI on DL380)  │  REST   │  (Juce / C++)       │
│                 │         │                      │         │                     │
│  Quick capture  │         │  - NLTK / spaCy      │         │  Lyric editor       │
│  Offline queue  │         │  - Vector embeddings │         │  Smart autocomplete │
│  Notifications  │         │  - PostgreSQL +      │         │  Suggestion panel   │
│                 │         │    pgvector          │         │                     │
└─────────────────┘         └──────────────────────┘         └─────────────────────┘
```

- **Mobile App** — Lightweight capture interface for raw input from anywhere
- **Python Backend** — Heavy lifting: analysis, embeddings, suggestion generation, persistent storage. Runs on the existing HPE DL380 Gen9 homelab server.
- **Ableton Plugin** — Creative interface for in-DAW writing with smart autocomplete and live suggestions

## Two Working Modes

The tool supports two complementary modes for working with lyrics:

1. **Structural Mode** — Focused on craft: syllable counts, rhyme schemes, meter, line length. Powered primarily by NLTK.
2. **Semantic Mode** — Focused on meaning: emotional tone, themes, undertones, articulating specific feelings or topics in artful, oblique ways. Powered by spaCy and vector embeddings.

These modes feed into each other. You can start with a feeling ("frustration about people not listening on environmental issues") and the tool helps find structural patterns and metaphors that fit. Or start with a structure (a verse skeleton) and the tool helps fill it with semantically appropriate language drawn from your own raw input.

## Documentation

- [`execution-plan.md`](./execution-plan.md) — Staged build plan and live progress tracker
- [`backend-architecture.md`](./backend-architecture.md) — Python backend design, NLP stack, vector embeddings, API
- [`mobile-app-spec.md`](./mobile-app-spec.md) — React Native capture app
- [`ableton-plugin-spec.md`](./ableton-plugin-spec.md) — Juce plugin for Ableton Live
- [`database-schema.md`](./database-schema.md) — PostgreSQL + pgvector schema
