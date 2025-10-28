Linguana ASR Service
====================

FastAPI-based Automatic Speech Recognition service using OpenAI Whisper for Kenyan dialects.

Setup:
------
1. Create virtual environment:
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

2. Install dependencies:
   pip install -r requirements.txt

3. Run the service:
   python main.py

   Or with uvicorn:
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload

Endpoints:
----------
- GET  /          - Service info
- GET  /health    - Health check
- POST /transcribe - Transcribe audio file
- POST /stream    - Process audio chunk
- WS   /ws/stream/{dialect} - WebSocket streaming
- POST /benchmark - Benchmark model performance

API Documentation:
------------------
Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

Notes:
------
- Default model: Whisper base
- Supports GPU acceleration if CUDA available
- Optimized for Swahili and Kenyan dialects
