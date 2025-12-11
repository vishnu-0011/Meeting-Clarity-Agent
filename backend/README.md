# 🔧 Backend — Meeting Clarity Agent

> **AI Pipeline for Speech Analysis & Communication Clarity Scoring**

This directory contains the FastAPI backend that powers the Meeting Clarity Agent. It orchestrates video processing, speech recognition, semantic analysis, and generates clarity metrics.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Core Modules](#core-modules)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Environment Variables](#environment-variables)

## 🏗️ Architecture

The backend follows a modular pipeline architecture:

```
Video Upload
    ↓
[main.py] — FastAPI Router
    ↓
┌─────────────────────────────────────────────────────┐
│ Processing Pipeline                                 │
├─────────────────────────────────────────────────────┤
│ 1. Media Extraction (utils.py)                      │
│    └→ MoviePy + FFmpeg                             │
│                                                     │
│ 2. ASR & Diarization (asr_processor.py)            │
│    └→ AssemblyAI API                               │
│                                                     │
│ 3. LLM Analysis (llm_analyser.py)                  │
│    └→ Gemini / Ollama / Mistral                    │
│                                                     │
│ 4. Clarity Scoring (models.py)                     │
│    └→ Pydantic validation + metrics                │
└─────────────────────────────────────────────────────┘
    ↓
JSON Response with Clarity Index & Metrics
```

## 📁 Core Modules

### `main.py` — FastAPI Application

**Responsibilities:**
- HTTP endpoint routing
- File upload handling
- Request/response validation
- CORS middleware configuration
- MongoDB integration (optional)

**Key Dependencies:**
- `FastAPI` — Web framework
- `python-multipart` — File upload parsing
- `pymongo` — Database client

### `src/asr_processor.py` — Speech Recognition

**Function:** `get_transcript_with_diarization(audio_path: str)`

**What it does:**
- Uploads audio to AssemblyAI
- Requests speaker diarization
- Extracts speaker labels and timestamps
- Returns structured transcript

**Output Format:**
```json
{
  "speaker_labels": ["Speaker 1", "Speaker 2"],
  "words": [
    {"word": "hello", "start": 0, "end": 500, "speaker": "Speaker 1"},
    {"word": "world", "start": 600, "end": 1000, "speaker": "Speaker 2"}
  ]
}
```

### `src/llm_analyser.py` — Semantic Jargon Analysis

**Functions:**

1. **`analyze_transcript_for_clarity(transcript: str, llm_provider: str)`**
   - Identifies jargon terms and ambiguous language
   - Assigns severity weights (0.0–1.0)
   - Generates improvement suggestions
   - Supports Gemini, Ollama, and Mistral

2. **`calculate_clarity_index(jargon_list: list, weights: list)`**
   - Computes 0–100 clarity score
   - Formula: `100 - (sum(weights) / len(jargon) * 100)`
   - Lower jargon usage = higher clarity

3. **`calculate_speaker_scores(transcript: dict, jargon_analysis: dict)`**
   - Aggregates jargon usage per speaker
   - Returns speaker-level metrics and rankings

### `src/vision_processor.py` — Video Processing

**Function:** `extract_frames(video_path: str, sample_rate: int)`

**Purpose:**
- Optional: Extract key frames for visual context
- Could support text detection (OCR) or gesture analysis
- Currently used for video validation

### `src/utils.py` — Helper Functions

**Key Functions:**

```python
extract_media(video_path: str, ffmpeg_path: str) -> str
  # Extracts WAV audio from video
  # Returns: path to audio file

validate_video_duration(video_path: str, max_duration: int = 3600) -> bool
  # Ensures video doesn't exceed max duration
  # Returns: True if valid

get_ffmpeg_path() -> str
  # Retrieves FFmpeg executable path from environment
```

### `src/models.py` — Data Models

**Pydantic Models:**

```python
class JargonTerm(BaseModel):
    word: str
    severity: float  # 0.0–1.0
    context: str
    suggestion: str

class ClarityReport(BaseModel):
    meeting_id: str
    clarity_index: float  # 0–100
    speaker_scores: List[SpeakerScore]
    jargon_terms: List[JargonTerm]
    transcript: str
    generated_at: datetime
```

## 📦 Installation

### 1. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Packages:**
- `fastapi` — Web framework
- `moviepy` — Video processing
- `assemblyai` — Speech recognition API
- `google-genai` — Gemini LLM
- `ollama` — Local LLM support
- `pydantic` — Data validation
- `pymongo[srv]` — Database
- `python-dotenv` — Environment config

## ⚙️ Configuration

### `.env` File

Create `.env` in the backend root directory:

```env
# Speech Recognition
ASSEMBLYAI_API_KEY=<your_key>

# LLM Configuration
# Option 1: Cloud (Gemini)
GEMINI_API_KEY=<your_gemini_key>
LLM_PROVIDER=gemini

# Option 2: Local (Ollama)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=mistral
# LLM_PROVIDER=ollama

# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net
MONGODB_DB=meeting-ai-agent

# Media Processing
FFMPEG_PATH=C:\\ffmpeg\\bin\\ffmpeg.exe  # Windows example
# FFmpeg on macOS/Linux is typically auto-detected

# Server
FAST_API_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=True
```

## 🚀 Running the Server

### Development Mode

```bash
python main.py
# Server starts on http://localhost:8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Swagger Docs

Once running, visit: **http://localhost:8000/docs**

## 💡 API Endpoints

### Upload & Analyze

```http
POST /upload
Content-Type: multipart/form-data

Parameters:
  - video: File
  - user_id: string (form data)
```

**Response (200 OK):**
```json
{
  "meeting_id": "507f1f77bcf86cd799439011",
  "clarity_index": 72.5,
  "speaker_scores": [
    {
      "speaker": "Speaker 1",
      "jargon_count": 5,
      "total_words": 1200,
      "jargon_density": 0.0042,
      "avg_severity": 0.65
    }
  ],
  "jargon_terms": [
    {
      "word": "synergy",
      "severity": 0.8,
      "context": "Let's create synergy between teams",
      "suggestion": "Use: 'collaboration' or 'teamwork'"
    }
  ],
  "transcript": "...",
  "processing_time_seconds": 45.2
}
```

### Get Meeting History

```http
GET /history?user_id=<user_id>&limit=10
```

### Get Meeting Details

```http
GET /meeting/<meeting_id>
```

### Health Check

```http
GET /health
```

## 📊 Data Models

All responses are validated using Pydantic models defined in `src/models.py`.

Key schema inheritance:

```
ClarityReport
├── meeting_id
├── clarity_index (0–100)
├── speaker_scores (List[SpeakerScore])
│   ├── speaker
│   ├── jargon_count
│   ├── avg_severity
│   └── jargon_density
├── jargon_terms (List[JargonTerm])
│   ├── word
│   ├── severity (0.0–1.0)
│   ├── context
│   └── suggestion
├── transcript
└── generated_at
```

## 🔑 Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `ASSEMBLYAI_API_KEY` | ✅ Yes | — | Get from [AssemblyAI](https://www.assemblyai.com/) |
| `GEMINI_API_KEY` | ❌ No* | — | For cloud LLM; get from [Google AI](https://ai.google.dev/) |
| `OLLAMA_BASE_URL` | ❌ No* | `http://localhost:11434` | For local LLM |
| `OLLAMA_MODEL` | ❌ No* | `mistral` | Local model name |
| `LLM_PROVIDER` | ❌ No | `gemini` | `gemini` or `ollama` |
| `MONGODB_URI` | ❌ No | — | For database (optional) |
| `FFMPEG_PATH` | ❌ No | Auto-detected | FFmpeg binary path |
| `DEBUG` | ❌ No | `False` | Debug logging |

*At least one LLM provider is required

## 📚 Additional Resources

- [AssemblyAI Documentation](https://www.assemblyai.com/docs)
- [Google Gemini API](https://ai.google.dev/)
- [Ollama Documentation](https://ollama.ai/)
- [FastAPI Official Guide](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🐛 Troubleshooting

### "AssemblyAI key is invalid"
- Verify the API key in `.env`
- Check that your account has active credits
- Visit [AssemblyAI Dashboard](https://www.assemblyai.com/dashboard)

### "FFmpeg not found"
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html), add to PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

### "Ollama connection failed"
- Ensure Ollama is running: `ollama serve`
- Verify `OLLAMA_BASE_URL` in `.env`
- Pull a model: `ollama pull mistral`

### "CORS errors from frontend"
- Backend includes CORS middleware
- Ensure frontend runs on `localhost:3000`
- Check backend logs for validation errors

---

**Backend Module Last Updated:** December 2025
