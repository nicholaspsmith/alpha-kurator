#include "PluginEditor.h"

namespace
{
    // Stage 1: token + URL are compiled in. Stage 4 reads them from a settings file.
    const juce::String kBackendUrl  = "http://localhost:8000";
    const juce::String kBearerToken = "dev-token";
    constexpr int kPollIntervalMs   = 500;
    constexpr int kPollMaxAttempts  = 30;
}

LyricAssistantEditor::LyricAssistantEditor (LyricAssistantProcessor& p)
    : AudioProcessorEditor (&p),
      processor (p),
      client (kBackendUrl, kBearerToken)
{
    setSize (640, 480);

    titleLabel.setFont (juce::Font (juce::FontOptions (22.0f, juce::Font::bold)));
    addAndMakeVisible (titleLabel);

    editor.setMultiLine (true);
    editor.setReturnKeyStartsNewLine (true);
    editor.setTextToShowWhenEmpty ("What just hit you?", juce::Colours::grey);
    editor.setWantsKeyboardFocus (true);
    addAndMakeVisible (editor);

    submitButton.onClick = [this] { onSubmitClicked(); };
    addAndMakeVisible (submitButton);

    statusLabel.setColour (juce::Label::textColourId, juce::Colours::grey);
    addAndMakeVisible (statusLabel);

    responseView.setMultiLine (true);
    responseView.setReadOnly (true);
    responseView.setCaretVisible (false);
    addAndMakeVisible (responseView);
}

void LyricAssistantEditor::paint (juce::Graphics& g)
{
    g.fillAll (juce::Colours::white);
}

void LyricAssistantEditor::resized()
{
    auto area = getLocalBounds().reduced (16);
    titleLabel.setBounds (area.removeFromTop (32));
    area.removeFromTop (8);

    auto editorArea = area.removeFromTop (160);
    editor.setBounds (editorArea);
    area.removeFromTop (8);

    auto buttonArea = area.removeFromTop (32);
    submitButton.setBounds (buttonArea.removeFromRight (120));
    statusLabel.setBounds (buttonArea);
    area.removeFromTop (12);

    responseView.setBounds (area);
}

void LyricAssistantEditor::onSubmitClicked()
{
    const auto rawInput = editor.getText().trim();
    if (rawInput.isEmpty())
        return;

    submitButton.setEnabled (false);
    statusLabel.setText ("Submitting...", juce::dontSendNotification);
    responseView.setText ({}, false);

    pendingSubmissionId = client.createSubmission (rawInput);
    if (pendingSubmissionId.isEmpty())
    {
        renderResponse ("Submission failed.");
        submitButton.setEnabled (true);
        return;
    }

    pollAttempts = 0;
    statusLabel.setText ("Analyzing...", juce::dontSendNotification);
    startTimer (kPollIntervalMs);
}

void LyricAssistantEditor::timerCallback()
{
    pollAttempts++;
    if (pollAttempts > kPollMaxAttempts)
    {
        stopTimer();
        renderResponse ("Timed out waiting for analysis.");
        submitButton.setEnabled (true);
        return;
    }

    juce::String status;
    juce::String suggestionsJson;
    if (! client.fetchSubmissionStatus (pendingSubmissionId, status, suggestionsJson))
        return;

    if (status == "complete")
    {
        stopTimer();
        renderResponse (suggestionsJson);
        submitButton.setEnabled (true);
    }
    else if (status == "failed")
    {
        stopTimer();
        renderResponse ("Backend reported analysis failed.");
        submitButton.setEnabled (true);
    }
}

void LyricAssistantEditor::renderResponse (const juce::String& message)
{
    statusLabel.setText ("Done.", juce::dontSendNotification);
    responseView.setText (message, false);
}
