# abstract_hugpy
## Description
**Description:**
A batteries-included bridge between your **abstract\_\*** ecosystem and popular **Hugging Face–style** NLP/Speech models. It packages **local model runners**, **text utilities**, **video→audio→transcribe→summarize** workflows, and optional **Flask blueprints** so you can expose everything over HTTP with almost no glue code.

* Repository: `https://github.com/AbstractEndeavors/abstract_hugpy`
* Author: `putkoff`
* License: MIT
* Status: Alpha

## ✨ Features

* **Video intelligence pipeline**

  * Download YouTube videos (`yt_dlp`)
  * Extract audio (`moviepy`/`ffmpeg`)
  * Transcribe with **OpenAI Whisper** (local)
  * Auto-generate **SRT captions**, **summary**, **keywords**, and **metadata**
  * Persistent, per-video directory management (`VideoDirectoryManager`)
* **Summarization**

  * Local **T5** (from your pre-downloaded dir)
  * **google/flan-t5-xl** helper for quick text2text summaries
  * **Falconsai/text\_summarization** pipeline (optional)
* **Keywords & embeddings**

  * **Sentence-BERT + KeyBERT** for keyphrase extraction
  * spaCy-based noun/NER keywording + density metrics
* **Generation helpers**

  * A lightweight text generator (`distilgpt2`) and helper to build public asset URLs
* **DeepCoder (local LLM) integration**

  * Singleton wrapper around a local **DeepCoder-14B** checkpoint with normal/c hat generation
* **Drop-in HTTP APIs (Flask blueprints)**

  * `/download_video`, `/extract_video_audio`, `/get_video_whisper_*`, `/get_video_*path`, etc.
  * `/deepcoder_generate`
  * Optional **proxy** blueprint for port-forwarding to local services

---

## 📦 Install

> **Python**: 3.6–3.9 (as declared). Newer versions may work but aren’t guaranteed by `setup.py`.

```bash
pip install abstract_hugpy
```

### System prerequisites

* **ffmpeg** (required by `moviepy` & `yt_dlp`)

  ```bash
  sudo apt-get update && sudo apt-get install -y ffmpeg
  ```
* **CUDA** (optional but recommended for speed if you have an NVIDIA GPU)
* **spaCy English model** (for NLP keyword rules)

  ```bash
  python -m spacy download en_core_web_sm
  ```

### Heavy dependencies

This package intentionally relies on:

* `torch`, `transformers`, `whisper`, `sentence_transformers`, `moviepy`, `yt_dlp`, `spacy`, `keybert`
* Your **abstract\_\*** modules: `abstract_ai`, `abstract_apis`, `abstract_flask`, `abstract_security`, `abstract_utilities`, `abstract_videos`, `abstract_webtools`

  > Keep them installed and version-compatible. If you later decide a more standard library is preferable at an integration point, I’ll **recommend replacing** the custom module rather than dropping it from examples (per your preference).

---

## 🗂️ Project Layout

```
abstract_hugpy/
  abstract_hugpy.py               # convenience import
  routes.py                       # re-exports model helpers
  video_utils.py                  # VideoDirectoryManager + video pipeline API
  create/get_video_url_bp.py      # codegen helpers for Flask blueprints
  hugging_face_flasks/
    deep_coder_flask.py
    proxy_video_url_flask.py
    video_url_flask.py
  hugging_face_models/
    config.py                     # DEFAULT_PATHS to local model dirs
    whisper_model.py
    summarizer_model.py
    google_flan.py
    keybert_model.py
    falcon_flan_t5_summarizers.py
    bigbird_module.py
    generation.py
    deepcoder.py
```

---

## ⚙️ Configuration

Local model/checkpoint locations are centralized in `hugging_face_models/config.py`:

```python
DEFAULT_PATHS = {
  "whisper":        "/mnt/24T/hugging_face/modules/whisper_base",
  "keybert":        "/mnt/24T/hugging_face/modules/all_minilm_l6_v2",
  "summarizer_t5":  "/mnt/24T/hugging_face/modules/text_summarization/",
  "flan":           "google/flan-t5-xl",
  "deepcoder":      "/mnt/24T/hugging_face/modules/DeepCoder-14B",
}
```

* You can **override** these at call time where functions accept a `*_path` or `model_directory` parameter.
* Video cache root defaults to `'/mnt/24T/hugging_face/videos'` (`video_utils.VIDEOS_DIRECTORY`). If that path doesn’t exist on your machine, either:

  * create it and grant write permissions, or
  * pass a different directory into `get_abs_videos_directory(...)` before use.

**Environment variables used by the proxy blueprint**

* `DEEPCODER_FLASK_PORT` – local port serving `deepcoder_generate`
* `VIDEO_URL_FLASK_PORT` – local port serving video endpoints

---

## 🚀 Quickstart (Python)

### 1) Summarize text (local T5)

```python
from abstract_hugpy.hugging_face_models.summarizer_model import summarize

text = "Long content ..."
summary = summarize(text, summary_mode="medium")  # short|medium|long|auto
print(summary)
```

### 2) Extract keywords (KeyBERT + spaCy)

```python
from abstract_hugpy.hugging_face_models.keybert_model import refine_keywords

info = refine_keywords(
    full_text="Your document goes here",
    top_n=10, diversity=0.5, use_mmr=True
)
print(info["combined_keywords"], info["keyword_density"])
```

### 3) Transcribe audio/video with Whisper (local)

```python
from abstract_hugpy.hugging_face_models.whisper_model import whisper_transcribe, extract_audio_from_video

audio_path = extract_audio_from_video("/path/to/video.mp4")  # creates audio.wav next to video
result = whisper_transcribe(audio_path, model_size="small", language="english")
print(result["text"])
```

### 4) End-to-end video pipeline (YouTube → metadata)

```python
from abstract_hugpy.video_utils import (
    download_video, extract_video_audio,
    get_video_whisper_text, get_video_metadata, get_video_captions
)

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

download_video(url)                  # cache info + mp4
extract_video_audio(url)             # cache audio.wav
text = get_video_whisper_text(url)   # transcribe (caches whisper_result.json)
meta = get_video_metadata(url)       # summary + keywords (caches video_metadata.json)
srt  = get_video_captions(url)       # captions.srt

print(meta["title"])
```

### 5) DeepCoder: local LLM generation

```python
from abstract_hugpy.hugging_face_models.deepcoder import get_deep_coder

dc = get_deep_coder()  # uses DEFAULT_PATHS["deepcoder"]
out = dc.generate(prompt="Write a Python function that checks if a number is prime.", max_new_tokens=256)
print(out)
```

---

## 🌐 HTTP API (Flask Blueprints)

You can expose the modules via Flask in minutes.

### Register blueprints

```python
from flask import Flask
from abstract_hugpy.hugging_face_flasks.video_url_flask import video_url_bp
from abstract_hugpy.hugging_face_flasks.deep_coder_flask import deep_coder_bp
from abstract_hugpy.hugging_face_flasks.proxy_video_url_flask import proxy_video_url_bp

app = Flask(__name__)
app.register_blueprint(video_url_bp)
app.register_blueprint(deep_coder_bp)
app.register_blueprint(proxy_video_url_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
```

### Video endpoints (JSON in, JSON out)

All accept `POST`/`GET` with body like:

```json
{ "url": "https://www.youtube.com/watch?v=..." }
```

| Endpoint                      | Purpose                          | Returns                 |
| ----------------------------- | -------------------------------- | ----------------------- |
| `/download_video`             | Download/cache the video & info  | video info dict         |
| `/extract_video_audio`        | Ensure `audio.wav` exists        | path or ok              |
| `/get_video_whisper_result`   | Full Whisper JSON                | `{text, segments, ...}` |
| `/get_video_whisper_text`     | Transcribed text only            | `str`                   |
| `/get_video_whisper_segments` | Segment list                     | `list[dict]`            |
| `/get_video_metadata`         | `{title, description, keywords}` | dict                    |
| `/get_video_captions`         | Generate `.srt`                  | content/path            |
| `/get_video_info`             | yt-dlp info                      | dict                    |
| `/get_video_directory`        | cached folder path               | str                     |
| `/get_video_path`             | mp4 path                         | str                     |
| `/get_video_audio_path`       | audio path                       | str                     |
| `/get_video_srt_path`         | captions path                    | str                     |
| `/get_video_metadata_path`    | metadata path                    | str                     |

**Example**

```bash
curl -X POST http://localhost:5005/get_video_whisper_text \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### DeepCoder endpoint

| Endpoint              | Body                                                  | Notes                                              |
| --------------------- | ----------------------------------------------------- | -------------------------------------------------- |
| `/deepcoder_generate` | Arbitrary JSON passed to `DeepCoder.generate(**data)` | Expects keys like `prompt`, `max_new_tokens`, etc. |

**Example**

```bash
curl -X POST http://localhost:5005/deepcoder_generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a Python Fibonacci function.", "max_new_tokens":256}'
```

### Proxy endpoints

If you run the real services on separate local ports, enable the proxy blueprint and set:

* `DEEPCODER_FLASK_PORT`
* `VIDEO_URL_FLASK_PORT`

The proxy exposes the same routes under `/api/*` and forwards requests to the local services.

---

## 🧠 How it works (high level)

```
YouTube URL
   │
   ▼
VideoDirectoryManager (per-ID folder)
   ├── info.json (yt_dlp)
   ├── video.mp4
   ├── audio.wav  (moviepy/ffmpeg)
   ├── whisper_result.json (OpenAI Whisper local)
   ├── captions.srt
   └── video_metadata.json (summary + keywords)
```

* **Whisper** transcribes audio to text & segments.
* **Summarizer** (local T5 or flan-t5-xl) condenses text.
* **KeyBERT + spaCy** extract keywords & densities.
* **Flask blueprints** expose orchestration endpoints.

---

## 📝 Logging

Most modules log via `abstract_utilities.get_logFile(__name__)`. Check your configured log directory for traces (e.g., video extraction progress, errors).

---

## 🔐 Security & Networking

* Downloading videos respects whatever `yt_dlp` supports; mind site TOS.
* The proxy blueprint forwards requests to `http://localhost:{PORT}`—use only within trusted networks and put a reverse proxy (Nginx) in front of it for auth/SSL if exposed publicly.
* Large models on GPU? Make sure to **cap tokens / batch sizes** in production.

---

## 🧩 API Reference (selected)

### `video_utils.VideoDirectoryManager`

* `get_data(video_url=None, video_id=None) -> dict`
* `download_video(video_url) -> dict`
* `extract_audio(video_url) -> str`
* `get_whisper_result(video_url) -> dict`
* `get_metadata(video_url) -> dict`  (summary+keywords)
* `get_captions(video_url) -> str`   (loads/export SRT)

**Convenience functions** mirror the above:
`download_video(...)`, `extract_video_audio(...)`, `get_video_whisper_text(...)`, etc.

### `hugging_face_models.summarizer_model`

* `summarize(text, summary_mode='medium', max_chunk_tokens=450, min_length=None, max_length=None) -> str`

### `hugging_face_models.keybert_model`

* `refine_keywords(full_text, top_n=10, ...) -> dict`
* `extract_keywords(text|list[str], top_n=5, ...) -> list[...]`

### `hugging_face_models.whisper_model`

* `whisper_transcribe(audio_path, model_size='small', language='english', ...) -> dict`
* `extract_audio_from_video(video_path, audio_path=None) -> str|None`

### `hugging_face_models.deepcoder`

* `get_deep_coder(module_path=None, torch_dtype=None, use_quantization=True) -> DeepCoder`
* `DeepCoder.generate(prompt|messages, max_new_tokens=..., use_chat_template=False, ...) -> str`

---

## 🧯 Troubleshooting

* **`ffmpeg` not found**
  Install it (`sudo apt-get install ffmpeg`). MoviePy/yt-dlp rely on it.

* **spaCy model: `OSError: [E050] Can't find model 'en_core_web_sm'`**
  `python -m spacy download en_core_web_sm`

* **CUDA OOM / very slow inference**

  * Use smaller Whisper model (`tiny`/`base`), smaller T5, or run on CPU.
  * For DeepCoder, enable 4-bit quantization (`use_quantization=True`) and reduce `max_new_tokens`.

* **Permission errors under `/mnt/24T/...`**

  * Create the directories and set write perms, or change `DEFAULT_PATHS` and `VIDEOS_DIRECTORY` to locations you own.

* **`moviepy` audio write hangs**
  Ensure the input file has an audio stream; upgrade `moviepy`; verify ffmpeg.

* **`yt_dlp` network errors**
  Update `yt_dlp` and retry, or use cookies/proxy if needed.

---

## 🔄 Versioning

Current package version: **0.0.0.40** (alpha)

---

## 🤝 Contributing

PRs welcome! Please:

1. Open an issue describing the change.
2. Keep new modules consistent with the **abstract\_\*** patterns (logging, `SingletonMeta`, path helpers).
3. Add small, runnable examples for new endpoints or model utilities.

---

## 📜 License

MIT © Abstract Endeavors

---

## 💡 Alternatives & When To Prefer Them

* **Remote inference instead of local heavy models**
  If you don’t need air-gapped/offline ops, delegating summarization/ASR to hosted APIs (e.g., Hugging Face Inference Endpoints, OpenAI Whisper API) can drastically simplify setup and reduce infra friction. You could **wrap those calls** behind the same Flask blueprints used here.

* **Faster keywording at scale**
  For massive batch jobs, a simpler TF-IDF or RAKE pipeline (e.g., `scikit-learn`, `rake-nltk`) may be faster and “good enough.” Keep `abstract_hugpy` for high-value content where semantic quality matters.

* **Video processing queue**
  If you’re ingesting thousands of URLs, a message queue (RabbitMQ/Redis) with worker pods running only `video_utils` calls might be more resilient than synchronous Flask calls. You already use RabbitMQ elsewhere—easy to slot in.

* **Model management**
  For multi-host deployments, consider **HF `safetensors`** checkpoints + `text-generation-inference` or **vLLM** as a backend and adapt `deepcoder.py` to call remote generation instead of local `AutoModelForCausalLM`. This offloads VRAM juggling and gives you token-streaming, parallelism, and metrics “for free.”

