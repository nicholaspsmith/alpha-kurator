# Mobile App Specification

## Overview

A lightweight cross-platform mobile capture app that lets you dump raw thoughts, emotions, and lyric ideas whenever inspiration strikes. The core value: zero friction. Inspiration rarely waits, so the app should make capturing it effortless and automatically pipe it into the analysis engine on the homelab server.

## Core Features

### Quick Capture Interface

- Single-screen text input — open app, start typing
- Optional mood / context tags (e.g. `frustrated`, `political`, `love-song`, `verse`, `hook`)
- Optional reference artist selector (for artist-style suggestions on this submission)
- One-tap submit

### Offline Support

- Submissions queue locally if offline
- Auto-sync to backend when connection returns
- No lost ideas, ever

### Notification System

- Push notification when backend finishes analyzing a submission
- Quick preview of top suggestions in notification
- Tap to open full analysis in app

### Submission History

- Browse previous captures
- See analysis status (pending / complete)
- View suggestions inline
- Mark favorites or pull into Ableton when ready to write

## Tech Stack

| Layer | Choice |
|-------|--------|
| Framework | React Native |
| Language | TypeScript |
| Local storage | SQLite (offline queue + cached suggestions) |
| Network | REST calls to homelab backend |
| Notifications | Push (APNS for iOS, FCM for Android) |
| Auth | Simple token-based auth to homelab |

React Native is a good fit given existing JavaScript/TypeScript expertise — minimal new ground to cover, ship to both iOS and Android from one codebase.

## User Flow

1. Inspiration hits — open app
2. Type raw thought, partial lyric, or feeling
3. Optionally tag mood / context, optionally pick reference artist
4. Submit
5. App queues locally if offline; sends immediately if online
6. Backend analyzes, sends push notification when done
7. Review suggestions in app or wait until at the computer in Ableton

## Design Principles

- **Friction-free capture is the north star.** Every additional tap is a chance to lose an idea.
- **Offline-first.** Inspiration doesn't care about cell service.
- **Readable suggestions.** When viewing analysis output, prioritize clarity over density.
- **Authentic to your voice.** The app captures *your* words. Suggestions are aids, not replacements.
