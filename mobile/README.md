# Lyric Assistant — Mobile

Expo + React Native + TypeScript capture app. Stage 1 slice: a single screen with text input → submit → list of past submissions with the backend's echo response.

## Setup

```sh
npm install
npx expo start
```

Then press `i` for iOS simulator or `a` for Android. Scan the QR with Expo Go to use a real device.

## Configuration

- Backend URL — set `expo.extra.backendUrl` in `app.json`. Default `http://localhost:8000` works for the iOS simulator. On a real device, point at your homelab (Tailscale hostname is recommended).
- Bearer token — set on first launch via the in-app prompt; stored in Expo SecureStore under the key `lyric_assistant_token`.

## What's not here yet

Per the execution plan, Stage 1 is the thinnest slice. Offline queue, push notifications, and full submission history come in Stage 3.
