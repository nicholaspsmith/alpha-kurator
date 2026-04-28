#include "BackendClient.h"

BackendClient::BackendClient (juce::String url, juce::String token)
    : baseUrl (std::move (url)),
      bearerToken (std::move (token))
{
}

juce::String BackendClient::performRequest (const juce::URL& url,
                                            bool isPost,
                                            const juce::String& jsonBody)
{
    const juce::String authHeader = "Authorization: Bearer " + bearerToken;
    const juce::String contentTypeHeader = "Content-Type: application/json";
    const juce::String headers = authHeader + "\r\n" + contentTypeHeader;

    juce::URL requestUrl = url;
    if (isPost && jsonBody.isNotEmpty())
        requestUrl = requestUrl.withPOSTData (jsonBody);

    auto options = juce::URL::InputStreamOptions (juce::URL::ParameterHandling::inAddress)
                       .withConnectionTimeoutMs (10000)
                       .withExtraHeaders (headers)
                       .withHttpRequestCmd (isPost ? "POST" : "GET");

    if (auto stream = requestUrl.createInputStream (options))
        return stream->readEntireStreamAsString();

    return {};
}

juce::String BackendClient::createSubmission (const juce::String& rawInput)
{
    juce::DynamicObject::Ptr payload (new juce::DynamicObject());
    payload->setProperty ("raw_input", rawInput);
    payload->setProperty ("source", "ableton-export");
    const auto body = juce::JSON::toString (juce::var (payload.get()));

    const juce::URL url (baseUrl + "/submissions");
    const auto response = performRequest (url, /*isPost*/ true, body);
    if (response.isEmpty())
        return {};

    const auto parsed = juce::JSON::parse (response);
    if (auto* obj = parsed.getDynamicObject())
        return obj->getProperty ("id").toString();

    return {};
}

bool BackendClient::fetchSubmissionStatus (const juce::String& submissionId,
                                           juce::String& outStatus,
                                           juce::String& outSuggestionsJson)
{
    const juce::URL submissionUrl (baseUrl + "/submissions/" + submissionId);
    const auto submissionBody = performRequest (submissionUrl, /*isPost*/ false);
    if (submissionBody.isEmpty())
        return false;

    const auto parsed = juce::JSON::parse (submissionBody);
    auto* obj = parsed.getDynamicObject();
    if (obj == nullptr)
        return false;

    outStatus = obj->getProperty ("status").toString();

    if (outStatus == "complete")
    {
        const juce::URL suggestionsUrl (baseUrl + "/submissions/" + submissionId + "/suggestions");
        outSuggestionsJson = performRequest (suggestionsUrl, /*isPost*/ false);
    }

    return true;
}
