cmake_minimum_required(VERSION 3.22)

project(LyricAssistant VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE STRING "macOS deployment target")

# JUCE is fetched via CMake's FetchContent so this repo doesn't vendor it.
include(FetchContent)
FetchContent_Declare(
    JUCE
    GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
    GIT_TAG 8.0.4
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(JUCE)

juce_add_plugin(LyricAssistant
    COMPANY_NAME "LyricAssistant"
    BUNDLE_ID com.lyricassistant.plugin
    PLUGIN_MANUFACTURER_CODE Lyrk
    PLUGIN_CODE Lyrc
    FORMATS VST3 AU
    PRODUCT_NAME "Lyric Assistant"
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS TRUE
)

target_sources(LyricAssistant PRIVATE
    Source/PluginProcessor.cpp
    Source/PluginProcessor.h
    Source/PluginEditor.cpp
    Source/PluginEditor.h
    Source/Net/BackendClient.cpp
    Source/Net/BackendClient.h
)

target_compile_definitions(LyricAssistant PRIVATE
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
)

target_link_libraries(LyricAssistant PRIVATE
    juce::juce_audio_utils
    juce::juce_gui_basics
    juce::juce_core
    juce::juce_recommended_config_flags
    juce::juce_recommended_lto_flags
    juce::juce_recommended_warning_flags
)
