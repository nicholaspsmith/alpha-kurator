#pragma once

#include <juce_core/juce_core.h>

class BackendClient
{
public:
    BackendClient (juce::String baseUrl, juce::String bearerToken);

    /** Returns the new submission's id, or an empty string on failure. */
    juce::String createSubmission (const juce::String& rawInput);

    /** Fills outStatus with "pending"/"analyzing"/"complete"/"failed".
        On status=="complete", outSuggestionsJson is populated with the suggestion list as JSON.
        Returns false if the request fails entirely (network error, non-2xx). */
    bool fetchSubmissionStatus (const juce::String& submissionId,
                                juce::String& outStatus,
                                juce::String& outSuggestionsJson);

private:
    juce::String baseUrl;
    juce::String bearerToken;

    juce::String performRequest (const juce::URL& url,
                                 bool isPost,
                                 const juce::String& jsonBody = {});
};
