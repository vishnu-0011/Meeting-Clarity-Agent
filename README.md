# 🗣️ Meeting Clarity Agent

> **Intelligent Communication Analysis for Professional Meetings**

A comprehensive AI-powered solution that analyzes video meetings to measure and improve communication clarity. The system combines **Automatic Speech Recognition (ASR)**, **speaker diarization**, and **Large Language Models** to identify ambiguous language and jargon, producing a quantifiable Clarity Index with actionable insights.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Environment Setup](#environment-setup)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **Weighted Clarity Index** — 0–100 score with LLM-assigned penalty weights for each jargon term
- **Speaker Contribution Analysis** — Identifies which speakers use the most ambiguous language
- **Real-time Transcription** — High-fidelity ASR with speaker diarization via AssemblyAI
- **Structured LLM Analysis** — Semantic jargon detection using Gemini, Mistral, or Ollama with Pydantic schemas
- **Interactive Dashboard** — React-based frontend with visualizations and transcript highlighting
- **Downloadable Reports** — JSON reports with detailed jargon analysis and recommendations
- **Multi-Model Support** — Switch between cloud (Gemini) and local (Ollama) LLM backends

## 📁 Project Structure

```
meeting-ai-agent/
├── frontend/                 # React dashboard (localhost:3000)
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── App.js          # Main app component
│   │   ├── api.js          # Backend API client
│   │   └── index.js        # React entry point
│   └── package.json
├── backend/                  # FastAPI server + AI pipeline
│   ├── main.py             # FastAPI application entry point
│   ├── src/
│   │   ├── asr_processor.py       # Speech-to-text processing
│   │   ├── llm_analyser.py        # Jargon analysis & clarity scoring
│   │   ├── vision_processor.py    # Video/image processing
│   │   ├── models.py              # Pydantic data models
│   │   └── utils.py               # Helper functions
│   ├── data/
│   │   └── jargon_master_list.csv # Jargon reference database
│   └── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Backend Setup (Python)

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Frontend Setup (Node.js)

```bash
cd frontend
npm install
```

### Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
# ASR API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_key_here

# LLM Configuration (choose one)
GEMINI_API_KEY=your_gemini_key_here
# OR for local LLM:
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# MongoDB (if using backend database)
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net
MONGODB_DB=meeting-ai-agent

# FFmpeg Path (Windows example)
FFMPEG_PATH=C:\\ffmpeg\\bin\\ffmpeg.exe
```

## ⚙️ Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 18+** (for frontend)
- **FFmpeg** installed and configured (for video processing)
- **API Keys:**
  - [AssemblyAI](https://www.assemblyai.com/) — for speech recognition
  - [Google Gemini](https://ai.google.dev/) — for LLM analysis (or local Ollama)
- **MongoDB** (optional, for data persistence)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vishnu-0011/meeting-ai-agent.git
cd meeting-ai-agent
```

### 2. Backend Installation

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 3. Frontend Installation

```bash
cd ../frontend
npm install
```

## 🏃 Running the Application

### Start the Backend (FastAPI)

```bash
cd backend
python main.py
# Backend runs on http://localhost:8000
```

### Start the Frontend (React)

In a new terminal:

```bash
cd frontend
npm start
# Frontend runs on http://localhost:3000
```

### Access the Application

Open your browser and navigate to: **http://localhost:3000**

## 🏗️ Architecture

### Pipeline Flow

1. **Video Upload** → React Dashboard uploads video to FastAPI backend
2. **Media Processing** → MoviePy extracts audio and validates duration
3. **ASR & Diarization** → AssemblyAI transcribes audio with speaker labels
4. **Semantic Analysis** → Gemini/Ollama identifies jargon and assigns penalty weights
5. **Scoring** → Backend calculates Clarity Index (0–100) and speaker metrics
6. **Dashboard Display** → React frontend visualizes results with charts and highlights

### Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **Video Processing** | MoviePy + FFmpeg | Extract and process media |
| **Speech Recognition** | AssemblyAI API | Transcription & speaker diarization |
| **LLM Analysis** | Gemini / Ollama | Semantic jargon detection |
| **Backend Framework** | FastAPI | REST API server |
| **Data Validation** | Pydantic | Type-safe data schemas |
| **Frontend** | React 19 + Recharts | Interactive dashboard |
| **Database** | MongoDB | Optional data persistence |

## 💡 API Documentation

### Main Endpoints

#### Upload & Analyze Meeting

```http
POST /upload
Content-Type: multipart/form-data

Body:
  - video: <video_file>
  - user_id: string
```

**Response:**
```json
{
  "meeting_id": "507f1f77bcf86cd799439011",
  "clarity_index": 72.5,
  "speaker_scores": [
    {"speaker": "Speaker 1", "jargon_count": 5, "severity": 0.6},
    {"speaker": "Speaker 2", "jargon_count": 2, "severity": 0.3}
  ],
  "jargon_terms": ["synergy", "leverage", "bandwidth"],
  "transcript": "..."
}
```

#### Get Meeting History

```http
GET /history?user_id=<user_id>
```

#### Get Meeting Details

```http
GET /meeting/<meeting_id>
```

For full API documentation, see `backend/README.md`.

## 🔧 Troubleshooting

### "FFmpeg not found"

**Solution:** Ensure FFmpeg is installed and update `FFMPEG_PATH` in `.env`.

```bash
# Windows: Download from https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

### "AssemblyAI API Key Invalid"

**Solution:** Verify your API key in the `.env` file and ensure it has active credits.

### "MongoDB connection failed"

**Solution:** If using MongoDB, verify `MONGODB_URI` in `.env` or run locally:

```bash
docker run -d -p 27017:27017 --name mongodb mongo
```

### CORS Errors

**Solution:** The backend already includes CORS middleware. If issues persist, check that both servers are running on the correct ports (frontend: 3000, backend: 8000).

## 📚 Additional Resources

- [Backend README](./backend/README.md) — Detailed backend architecture and components
- [Frontend README](./frontend/README.md) — Frontend component documentation
- [AssemblyAI Docs](https://www.assemblyai.com/docs) — Speech recognition API reference
- [FastAPI Docs](https://fastapi.tiangolo.com/) — Backend framework documentation
- [React Docs](https://react.dev/) — Frontend framework documentation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

## 👤 Author

**Vishnu** — [GitHub Profile](https://github.com/vishnu-0011)

---

**Last Updated:** December 2025
