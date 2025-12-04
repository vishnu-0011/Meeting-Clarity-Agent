import os
import json
import pandas as pd

from google import genai
from google.genai import types

from .models import ClarityReport, JargonTerm

# Try importing ollama (optional backend)
try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


# ---------- LOAD MASTER JARGON LIST (BACKEND-RELATIVE) ----------

# .../backend/src/llm_analyser.py -> BASE_DIR = .../backend
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
JARGON_CSV_PATH = os.path.join(DATA_DIR, "jargon_master_list.csv")

try:
    print(f"🔍 Loading jargon master list from: {JARGON_CSV_PATH}")
    jargon_master_df = pd.read_csv(JARGON_CSV_PATH)

    if jargon_master_df.empty:
        raise ValueError("jargon_master_list.csv is empty")

    if "Jargon_Term" not in jargon_master_df.columns:
        raise ValueError("CSV missing 'Jargon_Term' column")

    JARGON_TERMS_LIST = jargon_master_df["Jargon_Term"].dropna().tolist()
    print(f"✅ Loaded {len(JARGON_TERMS_LIST)} jargon terms from master list")
except Exception as e:
    print(f"⚠️  Could not load jargon master list: {e}")
    jargon_master_df = pd.DataFrame()
    JARGON_TERMS_LIST = []


# ---------- GEMINI BACKEND ----------


def analyze_transcript_for_clarity(utterances_data) -> ClarityReport:
    """
    Analyze the full transcript for jargon using Gemini,
    constrained to the terms in jargon_master_list.csv.
    """
    # 1. Prepare transcript text
    full_transcript = ""
    for u in utterances_data:
        full_transcript += f"Speaker {u['speaker']} [{u['start']:.1f}s]: {u['text']}\n"

    # 2. Gemini client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")

    client = genai.Client(api_key=api_key)

    # 3. Ensure jargon list is loaded
    if not JARGON_TERMS_LIST:
        raise ValueError(
            "No jargon terms loaded from master list. "
            "Check backend/data/jargon_master_list.csv and its columns."
        )

    # Build formatted list with definitions
    jargon_with_defs = "\n".join(
        [
            f"- {row['Jargon_Term']}: {row['Jargon_Meaning']}"
            for _, row in jargon_master_df.iterrows()
            if pd.notna(row.get("Jargon_Term"))
        ]
    )

    # 4. System prompt
    system_prompt = f"""
You are a Senior Communication Clarity Consultant.

MASTER JARGON LIST (only these terms should be identified):
{jargon_with_defs}

CRITICAL INSTRUCTIONS:
1. Search the transcript for EVERY term in the list above.
2. Count how many times EACH term appears.
3. For each found term, provide:
   - term (exact spelling from list)
   - speaker (who said it)
   - frequency (count, integer)
   - clarity_critique (suggest clearer phrasing)
   - penalty_weight (1.0 for buzzwords, 0.5 for technical, 0.2 for necessary)

4. Return JSON matching ClarityReport schema EXACTLY.
5. Do NOT identify any terms NOT in the list above.
6. If a term appears 0 times, do NOT include it.
7. Be thorough: check for all {len(JARGON_TERMS_LIST)} terms in the list.

Return ONLY valid JSON, no explanation.
"""

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_schema=ClarityReport,
    )

    print(
        f"Sending transcript to Gemini (constrained to {len(JARGON_TERMS_LIST)} terms)..."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[full_transcript],
        config=config,
    )

    report_dict = json.loads(response.text)
    return ClarityReport(**report_dict)


# ---------- OLLAMA BACKEND ----------


def analyze_transcript_with_ollama(utterances_data) -> ClarityReport:
    """
    Analyze the full transcript for jargon using a local Ollama model,
    constrained to the terms in the master CSV list.
    """
    if not OLLAMA_AVAILABLE:
        raise ImportError("ollama package not available.")

    # 1. Prepare transcript text (truncate to avoid huge prompts)
    MAX_CHARS = 8000
    full_transcript = ""
    for u in utterances_data:
        line = f"Speaker {u['speaker']} [{u['start']:.1f}s]: {u['text']}\n"
        if len(full_transcript) + len(line) > MAX_CHARS:
            break
        full_transcript += line

    # 2. JSON schema we expect
    schema = ClarityReport.model_json_schema()

    # 3. Ensure jargon list is loaded
    if not JARGON_TERMS_LIST:
        raise ValueError(
            "No jargon terms loaded from master list. "
            "Check backend/data/jargon_master_list.csv and its columns."
        )

    jargon_with_defs = "\n".join(
        [
            f"- {row['Jargon_Term']}: {row['Jargon_Meaning']}"
            for _, row in jargon_master_df.iterrows()
            if pd.notna(row.get("Jargon_Term"))
        ]
    )

    system_prompt = f"""
You are a Senior Communication Clarity Consultant.

MASTER JARGON LIST (only these terms should be identified):
{jargon_with_defs}

CRITICAL INSTRUCTIONS:
1. Search the transcript for EVERY term in the list above.
2. Count how many times EACH term appears (case-insensitive).
3. For each found term, provide:
   - term (MUST be from the list, exact spelling)
   - speaker (string)
   - frequency (integer count)
   - clarity_critique (string; how to say it more clearly)
   - penalty_weight (float between 0.0 and 1.0)

4. Compute:
   - total_jargon_count (integer)
   - overall_clarity_summary (string, max 50 words)

5. Return a JSON object matching this schema exactly:

{json.dumps(schema, indent=2)}

Rules:
- Do NOT wrap the result in extra keys (no "data", "result", "meeting_transcript").
- The top-level JSON MUST contain only: total_jargon_count, identified_jargon, overall_clarity_summary.
- Respond with JSON only. No explanation text.
- Be thorough: search for all {len(JARGON_TERMS_LIST)} terms in the list above.
"""

    print(
        f"Sending transcript to Ollama (constrained to {len(JARGON_TERMS_LIST)} terms)..."
    )

    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_transcript},
        ],
        format="json",
        options={
            "num_predict": 512,
            "temperature": 0.1,
        },
    )

    raw = response["message"]["content"]

    try:
        report_dict = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ollama returned invalid JSON: {e}\n\nRaw:\n{raw[:500]}")

    try:
        return ClarityReport(**report_dict)
    except Exception as e:
        print("Ollama raw dict:", report_dict)
        raise ValueError(f"Ollama JSON does not match ClarityReport schema: {e}")


# ---------- SCORING FUNCTIONS ----------


def calculate_clarity_index(report: ClarityReport, total_words: int) -> int:
    """Calculates the final Meeting Clarity Index (0-100) using weighted penalties."""
    if total_words == 0:
        return 100

    total_weighted_penalty = 0.0
    for jargon_term in report.identified_jargon:
        total_weighted_penalty += (
            jargon_term.frequency * jargon_term.penalty_weight
        )

    normalized_penalty = (total_weighted_penalty / total_words) * 500
    final_penalty = min(80, normalized_penalty)
    clarity_index = max(20, 100 - round(final_penalty))

    return clarity_index


def calculate_speaker_scores(report: ClarityReport) -> dict:
    """Calculates the weighted penalty score for each speaker."""
    speaker_penalties: dict[str, float] = {}

    for term in report.identified_jargon:
        penalty = term.frequency * term.penalty_weight
        speaker_penalties[term.speaker] = speaker_penalties.get(
            term.speaker, 0.0
        ) + penalty

    return speaker_penalties
