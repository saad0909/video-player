from moviepy.editor import VideoFileClip
import os

def extract_aduio(video_path):
	if video_path == "" or not os.path.exists(video_path):
		return "no video file found"

	output_audio_file = "output.wav"
	video_clip = VideoFileClip(video_path)
	audio_clip = video_clip.audio
	audio_clip.write_audiofile(output_audio_file)
	video_clip.close()
	return output_audio_file
