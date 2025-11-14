# Linguana: African Dialects & Languages Learning Platform

<div align="center">
  <img src="frontend/public/LinguanaHomePage.jpg" alt="Linguana Home Page" width="800"/>
</div>

## Overview

Linguana is a comprehensive platform for learning and preserving African dialects and languages through an engaging, gamified experience. The platform combines modern web technologies with blockchain to create a community-driven language learning ecosystem that celebrates Africa's rich linguistic diversity.

[![License: SSPL](https://img.shields.io/badge/License-SSPL-ff69b4.svg)](https://www.mongodb.com/licensing/server-side-public-license)
[![Next.js](https://img.shields.io/badge/Next.js-14.0.3-000000?logo=next.js)](https://nextjs.org/)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django)](https://www.djangoproject.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Base](https://img.shields.io/badge/Base_L2-0052FF?logo=ethereum)](https://base.org/)

## Features

- **Multi-language Support**: Record and validate audio clips in various African dialects and languages
- **Gamification**: Earn badges, points, and climb leaderboards
- **Web3 Integration**: USDC rewards distributed on Base L2
- **Real-time ASR**: Powered by Whisper for accurate speech recognition
- **PWA Support**: Installable and works offline
- **Community Driven**: Crowdsourced content with consensus validation

## Project Structure

```
linguana/
├── backend/              # Django + DRF + Channels backend
│   ├── linguana/         # Main Django project
│   ├── users/            # User authentication & profiles
│   ├── audio/            # Audio clip management
│   ├── annotations/      # Annotation & consensus system
│   ├── rewards/          # USDC reward distribution
│   └── manage.py
├── asr_service/          # FastAPI + Whisper ASR microservice
│   ├── main.py           # ASR service entry point
│   └── requirements.txt  # Python dependencies
└── frontend/             # Next.js PWA frontend
    ├── src/
    │   ├── app/         # App router pages
    │   └── components/  # Reusable components
    └── package.json     # Frontend dependencies
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- FFmpeg
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- FFmpeg

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/linguana.git
cd linguana/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations and create superuser
python manage.py migrate
python manage.py createsuperuser
python manage.py create_badges

# Start the development server
python manage.py runserver
```

### 2. ASR Service Setup

```bash
cd ../asr_service

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start ASR service
python main.py
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Start Celery Worker (in a new terminal)

```bash
cd backend
source venv/bin/activate  # If not already activated
celery -A linguana worker -l info
```

### 5. Start Redis (in a new terminal)

```bash
# On macOS (using Homebrew)
brew services start redis

# On Linux
sudo systemctl start redis
```

## Configuration

### Backend (`.env`)

```env
# Database
DATABASE_URL=postgres://user:password@localhost:5432/linguana_db

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=linguana-audio

# Firebase Auth
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json

# Base L2 Blockchain
BASE_RPC_URL=https://mainnet.base.org
REWARD_CONTRACT_ADDRESS=0x...

# ASR Service
ASR_SERVICE_URL=http://localhost:8001

# Security
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Frontend (`.env.local`)

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_ASR_URL=http://localhost:8001
NEXT_PUBLIC_BASE_CHAIN_ID=84532

# Firebase (for auth)
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-app.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
```

## Key Features

### Dashboard Overview

<div align="center">
  <img src="frontend/public/LinguanaContributorDashboard.jpg" alt="Linguana Contributor Dashboard" width="800"/>
</div>

### Authentication
- Multiple login methods (Email/Password, Google, Wallet Connect, Magic Link)
- JWT-based authentication with refresh tokens
- Role-based access control

### Audio Processing
- In-browser audio recording with Web Audio API
- Real-time speech-to-text with Whisper ASR
- Audio waveform visualization
- Offline recording support (PWA)

### Gamification
- Achievement badges and levels
- Daily streaks and challenges
- Leaderboards and user rankings
- Progress tracking and statistics

### Web3 Integration
- USDC rewards on Base L2
- Smart contract integration for transparent payouts
- Wallet connection (MetaMask, WalletConnect)
- Transaction history and rewards dashboard

### Community Features
- Crowdsourced content creation
- Consensus-based validation system
- Quality rating and feedback
- Public dataset exports for research

## API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new user |
| `/api/auth/login/` | POST | User login |
| `/api/auth/wallet/connect/` | POST | Connect Web3 wallet |
| `/api/auth/firebase/` | POST | Firebase authentication |
| `/api/auth/magic-link/request/` | POST | Request magic link |

### Audio

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/audio/clips/` | GET | List audio clips |
| `/api/audio/clips/` | POST | Upload new audio clip |
| `/api/audio/clips/{id}/` | GET | Get audio clip details |
| `/api/audio/clips/{id}/feedback/` | GET | Get pronunciation feedback |
| `/api/audio/dashboard/` | GET | User audio dashboard |

### Annotations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/annotations/` | GET | List annotations |
| `/api/annotations/` | POST | Create annotation |
| `/api/annotations/tasks/next_task/` | GET | Get next annotation task |
| `/api/annotations/tasks/{id}/complete/` | POST | Complete annotation task |

### Rewards

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/rewards/rewards/` | GET | List user rewards |
| `/api/rewards/rewards/summary/` | GET | Rewards summary |
| `/api/rewards/withdrawals/` | POST | Request withdrawal |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://{host}/ws/asr/stream/{dialect}/` | Real-time ASR streaming |

## Testing

### Backend Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users audio annotations

# Generate coverage report
coverage run --source='.' manage.py test
coverage report
```

### Frontend Tests

```bash
# Run unit tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run end-to-end tests
npm run test:e2e
```

## Deployment

### Backend (Production)

1. **Database Setup**
   ```bash
   # Create production database
   sudo -u postgres createdb linguana_prod
   sudo -u postgres createuser linguana_prod_user
   ```

2. **Gunicorn + Nginx**
   ```bash
   # Install Gunicorn
   pip install gunicorn
   
   # Run Gunicorn
   gunicorn --workers 3 --bind 0.0.0.0:8000 linguana.asgi:application -k uvicorn.workers.UvicornWorker
   ```

3. **ASR Service**
   ```bash
   # Run with GPU support (recommended)
   python main.py --device cuda
   ```

### Frontend (Production)

```bash
# Build for production
npm run build

# Start production server
npm start

# Or deploy to Vercel/Netlify
vercel --prod
```

## Security

- **Authentication**: JWT with refresh tokens
- **Data Protection**: Encryption at rest and in transit
- **CORS**: Strict origin policy
- **Rate Limiting**: Implemented on sensitive endpoints
- **Audit Logging**: All critical actions are logged
- **Security Headers**: CSP, HSTS, XSS Protection
- **Dependencies**: Regular security updates

## License

This project is licensed under the [Server Side Public License (SSPL)](https://www.mongodb.com/licensing/server-side-public-license).

### Key Points of SSPL:
- **Source Available**: The complete source code is available for viewing and modification.
- **Copyleft**: Any derivative work must be released under the same license.
- **Service Provider Requirement**: If you offer this software as a service, you must release any modifications and the source code of your service under SSPL.

For commercial use beyond the scope of SSPL, please contact us at licensing@linguana.app to discuss alternative licensing options.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Documentation

- [API Documentation](https://docs.linguana.app/api)
- [Frontend Guide](https://docs.linguana.app/frontend)
- [Deployment Guide](https://docs.linguana.app/deployment)

## Contact

For support or questions, please email support@linguana.app

## Acknowledgments

- Whisper ASR by OpenAI
- Django REST Framework
- Next.js and the React ecosystem
- Base L2 for blockchain infrastructure
* Max clip duration: 20 seconds
* Chunk size: 5-8 seconds for ASR

---

## Support

For issues or questions, refer to the SRS document or contact the development team.

---

## License

Proprietary - Linguana Platform

```

---

