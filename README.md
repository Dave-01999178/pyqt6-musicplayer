# PyQt6 Music Player

A desktop music player built with **Python** and **PyQt6**. Supports common audio formats with metadata display and real-time PCM playback.

Built as a hands-on Python learning project — improving Python proficiency, learning new concepts, exploring GUI development, audio processing, and application architecture through practical implementation.

---

<details>
<summary><strong>🎓 What I Learned</strong></summary>

This project deepened my understanding of Python fundamentals, design conventions, and architecture through hands-on practice and focused learning:

- Defining clear **layer and domain boundaries** with focused responsibilities, preventing logic from leaking across them
- Structuring code using a **service layer** to separate business logic from UI and infrastructure concerns
- Applying **time complexity (Big-O)** awareness when choosing an appropriate data structures and algorithms for the problem
- Using **threads** to keep the UI responsive during audio playback and processing
- Designing **cross-layer/boundary communication** using a **Pub-Sub** pattern and **protocol interfaces** to decouple components
- Using a **Tagged Union** to represent multiple possible outcomes, rather than relying on exceptions or overloaded return values
- Centralizing dependency wiring using an **application context** as a **composition root**, keeping object construction separate from business logic
- Applying **error propagation and handling** best practices:
  - Writing explicit `except` clauses for known failure cases
  - Preserving context when re-raising exceptions
  - Avoiding broad `except Exception` catches in favor of targeted handling
  - Using structured **logging** to support debugging and traceability
- Applying **code hygiene** throughout the entire codebase:
  - Using linters to enforce consistent code style and language conventions
  - Naming variables and functions to express intent, not expose implementation details
  - Keeping functions and methods focused on a single responsibility
  - Writing self-documenting code that doesn't require comments to explain what it does
  - Reserving inline comments for complex or non-obvious logic and design decisions

</details>

---

## 🚀 Installation & Usage

### Prerequisites

- Python **3.12** or higher
- [FFmpeg](https://ffmpeg.org/download.html) — must be installed and available on your system `PATH`
- [Poetry](https://python-poetry.org/docs/#installation) — dependency manager

> Ensure Python 3.12+ and FFmpeg are installed and added to your system PATH before installing dependencies.

### 🔧 Installation

Clone the repository and install dependencies using Poetry:

```bash
git clone https://github.com/yourusername/pyqt6_music_player.git
cd pyqt6_music_player
poetry install
```

### 📦 Dependencies

| Package | Purpose |
|---|---|
| `PyQt6` | GUI framework |
| `pydub` | Audio decoding (requires FFmpeg) |
| `mutagen` | Metadata extraction |
| `numpy` | PCM audio processing |
| `PyAudio` | Audio playback |

### ▶️ Running the App

```bash
poetry run python main.py
```

---

## 🎵 Supported Formats

MP3, WAV, FLAC, OGG *(via FFmpeg/pydub)*

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).