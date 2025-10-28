from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import whisper
import torch
import tempfile
import os
import logging
from pathlib import Path
import asyncio
from typing import Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Linguana ASR Service",
    description="Automatic Speech Recognition service for Kenyan dialects",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {device}")

models = {}


def load_model(model_size: str = "base"):
    """Load Whisper model"""
    if model_size not in models:
        logger.info(f"Loading Whisper {model_size} model...")
        models[model_size] = whisper.load_model(model_size, device=device)
        logger.info(f"Whisper {model_size} model loaded successfully")
    return models[model_size]


@app.on_event("startup")
async def startup_event():
    """Load default model on startup"""
    load_model("base")
    logger.info("ASR Service started successfully")


@app.get("/")
async def root():
    return {
        "service": "Linguana ASR Service",
        "version": "1.0.0",
        "status": "running",
        "device": device,
        "loaded_models": list(models.keys())
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "device": device,
        "models_loaded": len(models)
    }


@app.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    dialect: str = Form("sheng"),
    model_size: str = Form("base"),
    language: str = Form("sw")
):
    """Transcribe audio file"""
    try:
        logger.info(f"Received transcription request for dialect: {dialect}")
        
        model = load_model(model_size)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        try:
            result = model.transcribe(
                temp_audio_path,
                language=language,
                task="transcribe",
                fp16=(device == "cuda")
            )
            
            transcription = result["text"].strip()
            
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip()
                })
            
            confidence = 0.0
            if "segments" in result and len(result["segments"]) > 0:
                confidences = [seg.get("avg_logprob", 0) for seg in result["segments"]]
                confidence = sum(confidences) / len(confidences) if confidences else 0.0
                confidence = max(0.0, min(1.0, (confidence + 1.0)))
            
            logger.info(f"Transcription completed: {transcription[:50]}...")
            
            return {
                "transcription": transcription,
                "confidence": round(confidence, 3),
                "language": result.get("language", language),
                "dialect": dialect,
                "segments": segments,
                "model": model_size
            }
        
        finally:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
    
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream")
async def stream_transcribe(
    audio: UploadFile = File(...),
    dialect: str = Form("sheng")
):
    """Process audio chunk for streaming transcription"""
    try:
        model = load_model("base")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        try:
            result = model.transcribe(
                temp_audio_path,
                language="sw",
                task="transcribe",
                fp16=(device == "cuda")
            )
            
            text = result["text"].strip()
            
            confidence = 0.0
            if "segments" in result and len(result["segments"]) > 0:
                confidences = [seg.get("avg_logprob", 0) for seg in result["segments"]]
                confidence = sum(confidences) / len(confidences) if confidences else 0.0
                confidence = max(0.0, min(1.0, (confidence + 1.0)))
            
            return {
                "text": text,
                "confidence": round(confidence, 3),
                "is_final": True,
                "dialect": dialect
            }
        
        finally:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
    
    except Exception as e:
        logger.error(f"Stream transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/stream/{dialect}")
async def websocket_stream(websocket: WebSocket, dialect: str):
    """WebSocket endpoint for real-time streaming"""
    await websocket.accept()
    logger.info(f"WebSocket connection established for dialect: {dialect}")
    
    try:
        model = load_model("base")
        
        while True:
            data = await websocket.receive_bytes()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(data)
                temp_audio_path = temp_audio.name
            
            try:
                result = model.transcribe(
                    temp_audio_path,
                    language="sw",
                    task="transcribe",
                    fp16=(device == "cuda")
                )
                
                text = result["text"].strip()
                
                confidence = 0.0
                if "segments" in result and len(result["segments"]) > 0:
                    confidences = [seg.get("avg_logprob", 0) for seg in result["segments"]]
                    confidence = sum(confidences) / len(confidences) if confidences else 0.0
                    confidence = max(0.0, min(1.0, (confidence + 1.0)))
                
                await websocket.send_json({
                    "type": "partial_transcript",
                    "text": text,
                    "confidence": round(confidence, 3),
                    "is_final": True
                })
            
            finally:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for dialect: {dialect}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()


@app.post("/benchmark")
async def benchmark_model(
    test_audio: UploadFile = File(...),
    reference_text: str = Form(...),
    dialect: str = Form("sheng")
):
    """Benchmark model performance"""
    try:
        from jiwer import wer, cer
        
        model = load_model("base")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await test_audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        try:
            result = model.transcribe(
                temp_audio_path,
                language="sw",
                task="transcribe",
                fp16=(device == "cuda")
            )
            
            hypothesis = result["text"].strip()
            
            word_error_rate = wer(reference_text, hypothesis) * 100
            char_error_rate = cer(reference_text, hypothesis) * 100
            
            return {
                "reference": reference_text,
                "hypothesis": hypothesis,
                "wer": round(word_error_rate, 2),
                "cer": round(char_error_rate, 2),
                "dialect": dialect
            }
        
        finally:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
    
    except Exception as e:
        logger.error(f"Benchmark error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
