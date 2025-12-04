from fastapi import FastAPI, UploadFile, File, HTTPException, Depends,Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
from tempfile import NamedTemporaryFile
import shutil


from src.utils import extract_media
from src.asr_processor import get_transcript_with_diarization
from src.llm_analyser import (
    analyze_transcript_for_clarity,
    calculate_clarity_index,
    calculate_speaker_scores,
)
from src.models import ClarityReport

load_dotenv()

MONGODB_URI = os.environ["MONGODB_URI"]
MONGODB_DB = os.environ.get("MONGODB_DB", "meeting-ai-agent")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]
users_col = db["users"]
meetings_col = db["meetings"]

app = FastAPI()

# CORS for React dev server
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # CRA default
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- MODELS ----------
class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id: str

class HistoryItem(BaseModel):
    id: str
    created_at: str
    meeting_label: str
    clarity_index: int
    total_jargon_count: int
    duration_sec: float

def hash_password(pw: str) -> str:
    import hashlib
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def verify_password(pw: str, hashed: str) -> bool:
    return hash_password(pw) == hashed

# ---------- AUTH ENDPOINTS ----------

@app.post("/api/signup")
def signup(payload: SignupRequest):
    existing = users_col.find_one({"username": payload.username})
    if existing:
        # frontend will show this detail
        raise HTTPException(status_code=400, detail="Username already exists")

    res = users_col.insert_one(
        {
            "username": payload.username,
            "password_hash": hash_password(payload.password),
        }
    )
    return {"user_id": str(res.inserted_id)}


@app.post("/api/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    user = users_col.find_one({"username": payload.username})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return LoginResponse(user_id=str(user["_id"]))

@app.get("/api/history/{user_id}")
def history(user_id: str):
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    docs = list(meetings_col.find({"user_id": oid}).sort("created_at", 1))
    history = []
    for d in docs:
        history.append(
            {
                "id": str(d["_id"]),
                "created_at": d["created_at"].isoformat(),
                "meeting_label": d.get("meeting_label", ""),
                "clarity_index": d["clarity_index"],
                "total_jargon_count": d["total_jargon_count"],
                "duration_sec": d["duration_sec"],
            }
        )
    return {"history": history}


@app.post("/api/analyze")
async def analyze_meeting(user_id: str = Form(...), file: UploadFile = File(...)):
    if not users_col.find_one({"_id": ObjectId(user_id)}):
        raise HTTPException(status_code=401, detail="Invalid user")

    # 1. Save uploaded video to temp file
    with NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_video_path = tmp.name

    try:
        # 2. Your existing pipeline
        audio_file, frame_folder, duration = extract_media(temp_video_path, "data/temp", fps=1)
        utterances = get_transcript_with_diarization(audio_file)
        all_text = " ".join(u["text"] for u in utterances)
        total_words = len(all_text.split())

        clarity_report: ClarityReport = analyze_transcript_for_clarity(utterances)
        clarity_index = calculate_clarity_index(clarity_report, total_words)
        speaker_penalties = calculate_speaker_scores(clarity_report)

        # 3. Save summary to MongoDB
        top_terms = sorted(
            clarity_report.identified_jargon,
            key=lambda j: j.frequency * j.penalty_weight,
            reverse=True,
        )[:5]

        doc = {
            "user_id": ObjectId(user_id),
            "created_at": datetime.utcnow(),
            "meeting_label": file.filename,
            "duration_sec": float(duration),
            "clarity_index": int(clarity_index),
            "total_jargon_count": int(clarity_report.total_jargon_count),
            "top_jargon_terms": [
                {"term": j.term, "freq": int(j.frequency), "weight": float(j.penalty_weight)}
                for j in top_terms
            ],
            "speaker_scores": [
                {"speaker": spk, "score": float(score)}
                for spk, score in speaker_penalties.items()
            ],
        }
        meetings_col.insert_one(doc)

        # 4. Return JSON for React
        return {
            "clarity_index": clarity_index,
            "total_words": total_words,
            "total_jargon_count": clarity_report.total_jargon_count,
            "overall_summary": clarity_report.overall_clarity_summary,
            "speaker_scores": doc["speaker_scores"],
            "top_jargon_terms": doc["top_jargon_terms"],
            "transcript": all_text,
        }
    finally:
        try:
            os.remove(temp_video_path)
        except OSError:
            pass
