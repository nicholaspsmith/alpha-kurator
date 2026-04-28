#include "PluginProcessor.h"
#include "PluginEditor.h"

LyricAssistantProcessor::LyricAssistantProcessor()
    : AudioProcessor (BusesProperties()
                          .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                          .withOutput ("Output", juce::AudioChannelSet::stereo(), true))
{
}

juce::AudioProcessorEditor* LyricAssistantProcessor::createEditor()
{
    return new LyricAssistantEditor (*this);
}

// Required entry point for plugin formats.
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new LyricAssistantProcessor();
}
