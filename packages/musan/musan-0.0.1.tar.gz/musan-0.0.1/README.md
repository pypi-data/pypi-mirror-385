# MUSAN LIBRARY

## What is this?
The module allows you to work with music-sentiment-analisys models for [happy/sad](https://huggingface.co/nikarpoff/music-sentiment-analysis-happy-sad-13M) classification and [relaxing/energetic](https://huggingface.co/nikarpoff/music-sentiment-analysis-relaxing-energetic-8M) classification tasks. Source code of models and how them were trained you can see in [this repository](https://github.com/nikarpoff/music-sentiment-analysis). Library also provides methods to build and transform mel-spectrograms from the source audio file.

## Quick Guide
Example of usage:
```
import musan
import io

with open(filename, 'rb') as f:
    mp3_bytes = f.read()
    mp3_bytes = io.BytesIO(mp3_bytes)

hs_model, re_model = musan.load_pretraned_models()
result = musan.predict(mp3_bytes, hs_model, re_model, verbose=True)
```
    
Output:
```
19.10.2025 18:20:00: spec shape: torch.Size([1, 96, 4096])
19.10.2025 18:20:01: prediction time: 0:00:00.291374; running on cpu
{'predict': 'happy', 'happy': 0.6612311005592346, 'sad': 0.3387688398361206, 'energetic': 0.649221658706665, 'relaxing': 0.35077834129333496}
```

You also can load and use only one model:
```
model_re = musan.load_pretraned_re_model()
result = musan.predict(mp3_bytes, model_re=re_model)
```

or

```
model_hs = musan.load_pretraned_hs_model()
result = musan.predict(mp3_bytes, model_hs=hs_model)
```
