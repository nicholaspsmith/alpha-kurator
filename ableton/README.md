# Lyric Assistant — Ableton Plugin

Juce/C++ plugin (VST3 + AU) for in-DAW writing. Stage 1 slice: a single panel with a `TextEditor`, Submit button, and a response view. Posts to the backend, polls for completion, renders the echo response.

JUCE is fetched via CMake `FetchContent` — no submodule, no manual install.

## Build (macOS)

```sh
cmake -S . -B build -G Xcode
cmake --build build --config Release
```

VST3 output:  `build/LyricAssistant_artefacts/Release/VST3/Lyric Assistant.vst3`
AU output:    `build/LyricAssistant_artefacts/Release/AU/Lyric Assistant.component`

For Ableton on macOS, install AU into `~/Library/Audio/Plug-Ins/Components/` and VST3 into `~/Library/Audio/Plug-Ins/VST3/` (or symlink from the build output for iterative dev).

## Configuration

Stage 1: backend URL and bearer token are compiled in via constants at the top of `Source/PluginEditor.cpp`. Stage 4 promotes these to a settings file.

## What's not here yet

This slice only has a "Submit" button and a response view. Smart autocomplete, the suggestion side panel, artist selector, and offline cache all land in Stage 4.
