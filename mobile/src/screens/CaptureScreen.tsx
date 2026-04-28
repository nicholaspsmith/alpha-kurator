import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import {
  createSubmission,
  getSubmissionSuggestions,
  Submission,
  Suggestion,
} from "@/api/client";
import { getToken, setToken } from "@/storage/token";

interface HistoryItem {
  submission: Submission;
  suggestions: Suggestion[];
}

export function CaptureScreen() {
  const [draft, setDraft] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [needsToken, setNeedsToken] = useState(false);
  const [tokenInput, setTokenInput] = useState("");

  useEffect(() => {
    void (async () => {
      const t = await getToken();
      if (!t) setNeedsToken(true);
    })();
  }, []);

  async function handleSubmit() {
    if (!draft.trim()) return;
    setSubmitting(true);
    try {
      const submission = await createSubmission({ raw_input: draft });
      const suggestions = await getSubmissionSuggestions(submission.id);
      setHistory((prev) => [{ submission, suggestions }, ...prev]);
      setDraft("");
    } catch (e) {
      Alert.alert("Submission failed", e instanceof Error ? e.message : String(e));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSaveToken() {
    if (!tokenInput.trim()) return;
    await setToken(tokenInput.trim());
    setNeedsToken(false);
    setTokenInput("");
  }

  if (needsToken) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Set backend token</Text>
        <TextInput
          style={styles.input}
          value={tokenInput}
          onChangeText={setTokenInput}
          placeholder="LYRIC_ASSISTANT_TOKEN"
          autoCapitalize="none"
          autoCorrect={false}
          secureTextEntry
        />
        <Pressable style={styles.button} onPress={handleSaveToken}>
          <Text style={styles.buttonText}>Save</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <Text style={styles.title}>Capture</Text>
      <TextInput
        style={[styles.input, styles.draft]}
        value={draft}
        onChangeText={setDraft}
        placeholder="What just hit you?"
        multiline
        autoFocus
      />
      <Pressable
        style={[styles.button, (!draft.trim() || submitting) && styles.buttonDisabled]}
        onPress={handleSubmit}
        disabled={!draft.trim() || submitting}
      >
        {submitting ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Submit</Text>
        )}
      </Pressable>

      <FlatList
        style={styles.history}
        data={history}
        keyExtractor={(item) => item.submission.id}
        renderItem={({ item }) => (
          <View style={styles.historyItem}>
            <Text style={styles.historyInput}>{item.submission.raw_input}</Text>
            <Text style={styles.historyStatus}>{item.submission.status}</Text>
            {item.suggestions.map((s) => (
              <Text key={s.id} style={styles.historySuggestion}>
                {s.suggestion_type}: {JSON.stringify(s.content)}
              </Text>
            ))}
          </View>
        )}
      />
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#fff",
  },
  title: {
    fontSize: 28,
    fontWeight: "600",
    marginTop: 32,
    marginBottom: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 12,
  },
  draft: {
    minHeight: 120,
    textAlignVertical: "top",
  },
  button: {
    backgroundColor: "#222",
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonDisabled: {
    backgroundColor: "#999",
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  history: {
    marginTop: 24,
  },
  historyItem: {
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "#ccc",
  },
  historyInput: {
    fontSize: 16,
  },
  historyStatus: {
    fontSize: 12,
    color: "#666",
    marginTop: 4,
  },
  historySuggestion: {
    fontSize: 13,
    color: "#444",
    marginTop: 4,
  },
});
