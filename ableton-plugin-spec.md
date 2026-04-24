# Ableton Plugin Specification

## Overview

A Juce-built plugin that integrates into Ableton Live, providing direct in-DAW access to the lyric assistant. Smart autocomplete and live suggestions powered by the backend analysis engine, designed to support the writing workflow without breaking creative flow.

Built in **Juce** (rather than Max for Live) to allow full custom UI, networking, and the depth of functionality this tool requires.

## Core Features

### Lyric Editor Window

- Clean, focused text editor for writing and refining lyrics
- Loads previous mobile submissions or starts fresh
- Real-time character, word, syllable, and line counting
- Visual indicators for rhyme patterns, line lengths, syllable counts as you type

### Smart Autocomplete

- Suggests next words as you type, based on:
  - Vector embeddings — semantically related words from reference library
  - Frequency-weighted vocabularies — words common to selected reference artist
  - Local context — what fits grammatically and tonally with what you've written
- Multiple ranked options shown inline
- Tab / arrow key to accept, Escape to dismiss

### Suggestion Panel

- Side panel showing deeper analysis from backend:
  - Rhyme scheme patterns that fit the current line
  - Semantic alternatives for better articulation
  - Emotional tone matching
  - Thematic suggestions
  - Optional artist-style hints (e.g. "Eminem-style rhyme for this line")
- Refreshes on demand or as you type (debounced)

### Reference Artist Selector

- Dropdown to pick artist whose vocabulary biases autocomplete
- Authentic-to-you mode (no artist bias, just your own input + general suggestions) is the default
- Artist mode is opt-in and intended as intentional reference / shout-out — never imitation

### Backend Integration

- REST API calls to Python backend on homelab
- Local cache of recent suggestions to minimize latency
- Graceful degradation if backend unreachable (local autocomplete from cached vocabularies)

### Export Functionality

- Export finished lyrics to clipboard
- Save to file
- Send back to mobile submission history for later reference

## Tech Stack

| Layer | Choice |
|-------|--------|
| Language | C++ |
| Framework | Juce (latest stable) |
| Build system | CMake |
| UI | Juce native components |
| Networking | Juce `URL` / `WebInputStream` for REST calls |
| JSON | Juce built-in JSON support |
| Plugin format | VST3 + AU (for Ableton on macOS) |

## User Workflow

1. Open Ableton, add plugin to a track
2. Optionally load previous mobile submission, or start fresh
3. Begin typing — autocomplete suggests words in real time
4. Hit "Analyze" for full suggestion panel update
5. Optionally pick reference artist for stylistic flavor
6. Refine lyrics with structural and semantic suggestions
7. Export when satisfied — to clipboard, file, or back to mobile history

## Design Principles

- **Don't break flow.** Suggestions appear when invited; the editor stays the center of attention.
- **Authentic-by-default.** Artist style is opt-in and clearly marked when active.
- **Fast feedback.** Local cache + debounced backend calls keep autocomplete snappy.
- **Tight Ableton integration.** Behaves like a first-class Live plugin, not a bolted-on web app.
