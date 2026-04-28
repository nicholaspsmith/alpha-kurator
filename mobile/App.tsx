import { StatusBar } from "expo-status-bar";
import { SafeAreaView, StyleSheet } from "react-native";

import { CaptureScreen } from "@/screens/CaptureScreen";

export default function App() {
  return (
    <SafeAreaView style={styles.root}>
      <StatusBar style="auto" />
      <CaptureScreen />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: "#fff",
  },
});
