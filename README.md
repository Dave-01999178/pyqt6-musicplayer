# PyQt6 Music Player

> ⚠️ Work in progress

A desktop music player built with **Python** and **PyQt6**. Supports common audio formats with metadata display and real-time PCM playback.

Built as a hands-on Python learning project — improving Python proficiency, learning new concepts, exploring GUI development, audio processing, and application architecture through practical implementation.

---

## Requirements

### System
- Python 3.12+
- [FFmpeg](https://ffmpeg.org/download.html) — must be installed and available on `PATH`
- [Poetry](https://python-poetry.org/docs/#installation) — dependency manager

### Dependencies

Install via Poetry:
```bash
poetry install
```

| Package | Purpose |
|---|---|
| `PyQt6` | GUI framework |
| `pydub` | Audio decoding (requires FFmpeg) |
| `mutagen` | Metadata extraction |
| `numpy` | PCM audio processing |
| `PyAudio` | Audio playback |

---

## Getting Started
```bash
poetry install
poetry run python main.py
```

---

## Supported Formats

MP3, WAV, FLAC, OGG *(via FFmpeg/pydub)*

---