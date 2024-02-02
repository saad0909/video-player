import torch
import torchaudio
import zipfile
from glob import glob
import os


device = torch.device('cpu')  # gpu also works, but our models are fast enough for CPU

model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en', # also available 'de', 'es'
                                       device=device)
(read_batch, split_into_batches,
 read_audio, prepare_model_input) = utils  # see function signature for details

if not os.path.exists("speech_orig.wav"):
# download a single file, any format compatible with TorchAudio (soundfile backend)
     torch.hub.download_url_to_file('https://opus-codec.org/static/examples/samples/speech_orig.wav', dst ='speech_orig.wav', progress=True)

def speech_to_text(audio_file):
 if not os.path.exists(audio_file):
    return "Audio file not found"
 test_files = glob(audio_file)
 batches = split_into_batches(test_files, batch_size=10)
 input = prepare_model_input(read_batch(batches[0]),
                            device=device)

 output = model(input)
 str = ""
 for example in output:
     str += decoder(example.cpu())
     str += " "
 return str