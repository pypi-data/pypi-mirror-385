from svc_helper.sfeatures.models import RVCHubertModel, SVC5WhisperModel, \
    SVC5HubertModel, SVC5TextEncoderFullModel
import numpy as np
import torch
import librosa
import soundfile as sf

def test_sfeatures():
    rvc_model = RVCHubertModel()

    data, rate = librosa.load('tests/test_speech.wav',
       sr=RVCHubertModel.expected_sample_rate)
    feat = rvc_model.extract_features(torch.from_numpy(data))

    data, rate = librosa.load('tests/ood5_male.wav',
        sr=RVCHubertModel.expected_sample_rate)
    #print(len(data))
    padded_data = rvc_model.pad_audio(data)
    sf.write('tests/test_padded.wav', padded_data, samplerate=16000)
    feat = rvc_model.extract_features(torch.from_numpy(data))
    print(feat.shape)

    del rvc_model
    svc5_whisper_model = SVC5WhisperModel()
    feat = svc5_whisper_model.extract_features(torch.from_numpy(data))
    print(feat.shape)

    del svc5_whisper_model
    svc5_hubert_model = SVC5HubertModel()
    feat = svc5_hubert_model.extract_features(torch.from_numpy(data))
    print(feat.shape)

    del svc5_hubert_model
    svc5_text_encoder_model = SVC5TextEncoderFullModel()
    feat = svc5_text_encoder_model.extract_features(torch.from_numpy(data))
    print(feat.shape)
    
test_sfeatures()