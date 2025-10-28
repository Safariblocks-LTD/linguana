LINGUANA - Kenyan Dialect Learning & Crowdsourcing Platform
============================================================

A PWA-first platform for learning Kenyan dialects (Sheng, Kiamu, Kibajuni) with gamified crowdsourcing and USDC rewards on Base L2.

PROJECT STRUCTURE
-----------------
linguana/
├── backend/              # Django + DRF + Channels backend
│   ├── linguana/        # Main Django project
│   ├── users/           # User authentication & profiles
│   ├── audio/           # Audio clip management
│   ├── annotations/     # Annotation & consensus system
│   ├── rewards/         # USDC reward distribution
│   └── manage.py
├── asr_service/         # FastAPI + Whisper ASR microservice
│   ├── main.py
│   └── requirements.txt
└── frontend/            # Next.js PWA frontend
    ├── app/
    ├── components/
    └── package.json

QUICK START
-----------

1. Backend Setup:
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   
   cp .env.example .env
   # Edit .env with your configuration
   
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py create_badges
   python manage.py runserver

2. ASR Service Setup:
   cd asr_service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py

3. Frontend Setup:
   cd frontend
   npm install
   npm run dev

4. Celery Worker (separate terminal):
   cd backend
   celery -A linguana worker -l info

5. Redis (required for Celery & Channels):
   redis-server

ENVIRONMENT VARIABLES
---------------------
Backend (.env):
- DATABASE_URL: PostgreSQL connection string
- REDIS_URL: Redis connection string
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY: S3 storage
- FIREBASE_CREDENTIALS_PATH: Firebase auth credentials
- BASE_RPC_URL, REWARD_CONTRACT_ADDRESS: Base L2 blockchain
- ASR_SERVICE_URL: ASR microservice endpoint

Frontend (.env.local):
- NEXT_PUBLIC_API_URL: Backend API URL
- NEXT_PUBLIC_WS_URL: WebSocket URL
- NEXT_PUBLIC_BASE_CHAIN_ID: Base chain ID

KEY FEATURES
------------
✓ Multi-auth: Email/password, Firebase social, Magic Link, Wallet connect
✓ Audio recording/upload with PWA offline support
✓ Real-time ASR via WebSocket (Whisper)
✓ Gamified UI: progress bars, streaks, badges, leaderboards
✓ Consensus-based validation (3 annotations, 85% similarity)
✓ USDC rewards on Base L2 (70% contributor, 30% validators)
✓ Dataset export for ML training
✓ Pronunciation feedback with waveform visualization
✓ Admin dashboard for pool funding & analytics

API ENDPOINTS
-------------
Auth:
- POST /api/auth/register/
- POST /api/auth/login/
- POST /api/auth/wallet/connect/
- POST /api/auth/firebase/
- POST /api/auth/magic-link/request/

Audio:
- GET/POST /api/audio/clips/
- GET /api/audio/clips/{id}/feedback/
- POST /api/audio/clips/{id}/submit_for_annotation/
- GET /api/audio/dashboard/

Annotations:
- GET/POST /api/annotations/annotations/
- GET /api/annotations/tasks/next_task/
- POST /api/annotations/tasks/{id}/complete/

Rewards:
- GET /api/rewards/rewards/my_rewards/
- GET /api/rewards/rewards/summary/
- POST /api/rewards/withdrawals/

WebSocket:
- ws://localhost:8000/ws/asr/stream/{dialect}/

TESTING
-------
Backend:
  python manage.py test

Frontend:
  npm run test

DEPLOYMENT
----------
Backend:
- Use gunicorn + daphne for production
- Configure PostgreSQL database
- Setup Redis for Celery & Channels
- Configure S3 for audio storage
- Deploy ASR service separately (GPU recommended)

Frontend:
- Build: npm run build
- Deploy to Vercel/Netlify with PWA support

SECURITY
--------
- HTTPS required for production
- JWT authentication with refresh tokens
- Wallet signature verification
- CSRF protection enabled
- Rate limiting recommended
- Encrypted audio storage

BUSINESS RULES
--------------
- Consent required for all recordings
- 3 annotations minimum per clip
- 85% consensus threshold for validation
- $0.20 default reward per validated clip
- 70/30 split (contributor/validators)
- Max clip duration: 20 seconds
- Chunk size: 5-8 seconds for ASR

SUPPORT
-------
For issues or questions, refer to the SRS document or contact the development team.

LICENSE
-------
Proprietary - Linguana Platform
