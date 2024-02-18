from speech_to_text import transcribe_audio
from beep_clip import censor_video, extract_audio_from_video
from detect import analyze_text


print("hellp")
video_path = "/home/raza/code/censor_tool_fyp/Wolf Of Wallstreet.mp4"

# Step 0: Extract Audio from Video
audio_path = extract_audio_from_video(video_path)

# Step 1: Speech-to-Text
transcription_results = transcribe_audio(audio_path)

# Extract the transcribed text from the results
transcribed_text = " ".join(result.alternatives[0].transcript for result in transcription_results)

print(transcribed_text)

"""
# Step 2: Detect Explicit Content
toxicity_score = analyze_text(transcribed_text)
print("Toxicity Score:", toxicity_score)

# Step 3: Video Processing (Censoring)
if toxicity_score > 0.5:  # Adjust the threshold based on your requirements
    censor_points = [5.0, 10.2, 15.7]  # Replace with the time points where explicit content is detected
    censor_video(video_path, censor_points)
    print("Video censored.")
else:
    print("No explicit content detected.")
"""