import os
import assemblyai as aai

def get_transcript_with_diarization(audio_path):
    """Transcribes audio and returns utterances with speaker labels."""
    aai.settings.api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    
    if not aai.settings.api_key:
        raise ValueError("ASSEMBLYAI_API_KEY not found in environment.")

    # Configure for Diarization (Speaker Labels)
    config = aai.TranscriptionConfig(speaker_labels=True)
    transcriber = aai.Transcriber()
    
    # Use transcriber.transcribe() for simple audio file processing
    print("Submitting audio for transcription...")
    transcript = transcriber.transcribe(audio_path, config=config)
    
    if transcript.status == aai.TranscriptStatus.error:
        raise Exception(f"Transcription failed: {transcript.error}")
    
    # Extract just the useful utterance data
    utterances_data = [
        {
            "speaker": u.speaker,
            "text": u.text,
            "start": u.start,  # in milliseconds
            "end": u.end       # in milliseconds
        } for u in transcript.utterances
    ]
    
    return utterances_data