from google.cloud import speech_v1p1beta1 as speech

def transcribe_audio(audio_path):
    client = speech.SpeechClient()

    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, single_utterance=False
    )
    requests = [speech.StreamingRecognizeRequest(audio_content=content)]

    # Perform streaming recognition
    responses = client.streaming_recognize(
        requests=requests, config=streaming_config
    )

    for response in responses:
        for result in response.results:
            print("Transcript: {}".format(result.alternatives[0].transcript))

    return response.results


