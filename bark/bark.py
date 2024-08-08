from bark.generation import load_codec_model, generate_text_semantic
from encodec.utils import convert_audio
from hubert.hubert_manager import HuBERTManager
from hubert.pre_kmeans_hubert import CustomHubert
from hubert.customtokenizer import CustomTokenizer

import torchaudio
import torch

def voice_clone(output):
    model = load_codec_model(use_gpu=True)
    hubert_manager = HuBERTManager()
    hubert_manager.make_sure_hubert_installed()
    hubert_manager.make_sure_tokenizer_installed()

    
    if not os.path.exists("./data/models/hubert/"): 
        os.makedirs("./data/models/hubert/") 


    if os.path.exists("./data/models/hubert/hubert.pt"):
        os.remove("./data/models/hubert/hubert.pt")
    if os.path.exists("./data/models/hubert/hubert.pth"):
        os.remove("./data/models/hubert/hubert.pth")

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
    voice_name = 'output'
    if not os.path.exists("./config/bark_voices/"): 
        os.makedirs("./config/bark_voices/") 
    output_path = './config/bark_voices/' + voice_name + '.npz'
    np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)