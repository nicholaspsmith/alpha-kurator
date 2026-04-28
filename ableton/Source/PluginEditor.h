#pragma once

#include <juce_gui_basics/juce_gui_basics.h>

#include "Net/BackendClient.h"
#include "PluginProcessor.h"

class LyricAssistantEditor : public juce::AudioProcessorEditor,
                              private juce::Timer
{
public:
    explicit LyricAssistantEditor (LyricAssistantProcessor&);
    ~LyricAssistantEditor() override = default;

    void paint (juce::Graphics&) override;
    void resized() override;

private:
    void onSubmitClicked();
    void timerCallback() override;
    void renderResponse (const juce::String& message);

    LyricAssistantProcessor& processor;

    juce::Label titleLabel { {}, "Lyric Assistant" };
    juce::TextEditor editor;
    juce::TextButton submitButton { "Submit" };
    juce::Label statusLabel;
    juce::TextEditor responseView;

    BackendClient client;
    juce::String pendingSubmissionId;
    int pollAttempts = 0;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (LyricAssistantEditor)
};
