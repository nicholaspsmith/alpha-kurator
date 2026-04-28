import Constants from "expo-constants";

import { getToken } from "@/storage/token";

const backendUrl: string =
  (Constants.expoConfig?.extra?.backendUrl as string | undefined) ??
  "http://localhost:8000";

export type SubmissionStatus = "pending" | "analyzing" | "complete" | "failed";

export interface Submission {
  id: string;
  raw_input: string;
  status: SubmissionStatus;
  submission_date: string;
  mood_tags: string[];
  reference_artist: string | null;
  source: "mobile" | "ableton-export" | "api";
}

export interface Suggestion {
  id: string;
  submission_id: string;
  suggestion_type:
    | "rhyme_pattern"
    | "semantic_alternative"
    | "next_word"
    | "artist_style"
    | "thematic";
  content: Record<string, unknown>;
  confidence_score: number;
  created_date: string;
}

async function authedFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const token = await getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(`${backendUrl}${path}`, { ...init, headers });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`HTTP ${res.status}: ${detail}`);
  }
  return res;
}

export async function createSubmission(input: {
  raw_input: string;
  mood_tags?: string[];
  reference_artist?: string | null;
}): Promise<Submission> {
  const res = await authedFetch("/submissions", {
    method: "POST",
    body: JSON.stringify({ ...input, source: "mobile" }),
  });
  return res.json();
}

export async function getSubmissionSuggestions(id: string): Promise<Suggestion[]> {
  const res = await authedFetch(`/submissions/${id}/suggestions`);
  return res.json();
}
