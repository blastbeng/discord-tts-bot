import os
from bark.generation import SAMPLE_RATE, preload_models, codec_decode, generate_coarse, generate_fine, load_codec_model, generate_text_semantic
from encodec.utils import convert_audio
from bark_hubert_quantizer.hubert_manager import HuBERTManager
from bark_hubert_quantizer.pre_kmeans_hubert import CustomHubert
from bark_hubert_quantizer.customtokenizer import CustomTokenizer

from bark.api import generate_audio
from transformers import AutoProcessor, BarkModel


import torchaudio
import torch
from io import BytesIO


# download and load all models
preload_models(
    text_use_gpu=True,
    text_use_small=False,
    coarse_use_gpu=True,
    coarse_use_small=False,
    fine_use_gpu=True,
    fine_use_small=False,
    codec_use_gpu=True,
    force_reload=False,
)

def voice_clone(output):
    device = 'cuda' # or 'cpu'
    model = load_codec_model(use_gpu=True if device == 'cuda' else False)
    hubert_manager = HuBERTManager()
    hubert_manager.make_sure_hubert_installed()
    hubert_manager.make_sure_tokenizer_installed()

    hubert_model = CustomHubert(checkpoint_path='./data/models/hubert/hubert.pt').to(device)
    tokenizer = CustomTokenizer.load_from_checkpoint('./data/models/hubert/tokenizer.pth').to(device)


    audio_filepath = 'config/to_clone.wav' # the audio you want to clone (under 13 seconds)
    wav, sr = torchaudio.load(audio_filepath)
    wav = convert_audio(wav, sr, model.sample_rate, model.channels)
    wav = wav.to(device)

    semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
    semantic_tokens = tokenizer.get_token(semantic_vectors)
    
    with torch.no_grad():
        encoded_frames = model.encode(wav.unsqueeze(0))
    codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze() 
    
    
    codes = codes.cpu().numpy()
    
    semantic_tokens = semantic_tokens.cpu().numpy()
    import numpy as np
    if not os.path.exists("./config/bark_voices/"): 
        os.makedirs("./config/bark_voices/") 
    output_path = './config/bark_voices/' + output + '.npz'
    np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)

def talk(voice_name, text_prompt):
    processor = AutoProcessor.from_pretrained("suno/bark-small")
    model = BarkModel.from_pretrained("suno/bark-small")

    voice_preset = "./config/bark_voices/" + voice_name + ".npz"

    inputs = processor(text_prompt, voice_preset=voice_preset)

    audio_array = model.generate(**inputs, semantic_max_new_tokens=100)
    audio_array = audio_array.cpu().numpy().squeeze()

    return BytesIO(bytes(audio_array))