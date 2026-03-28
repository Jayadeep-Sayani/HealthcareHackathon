# MedRelay 🏥

An agentic patient intake and referral network that reduces friction in healthcare handoffs, connects siloed providers, and routes patients to the right level of care faster.

## Team Members

- Nolan Bryson
- Jayadeep Sayani

## Challenge Track

Track 1 - Clinical 

## Problem Statement

Emergency rooms are overcrowded with non-emergency cases. Specialists have no standardized intake. Referrals are manual, paper-heavy, and relationship-dependent — if a doctor doesn't personally know a specialist, the patient may never get in. The healthcare system is described by practitioners as "a bunch of small islands of innovation with no connection to one another."

Key pressures addressed:
- **Centralized intake and referral systems** (government priority)
- **Routing patients to right level of care** (reducing ER misuse)
- **Workforce constraints** — doctors are stretched thin, every saved minute matters
- **Shift toward community-based and virtual care models**
- **Care continuity** — next doctor needs context the current doctor has

## Solution Summary

MedRelay is a two-sided web application that adds zero cognitive load to physician workflows while creating a connected healthcare network. The platform features:

### 🔄 **Doctor Session View (Referring Physician)**
- Live appointment session UI with patient roster selection
- Ambient AI transcription agent that builds structured clinical notes in real-time
- One-click referral creation with AI-generated clinical summaries
- Zero forms, zero paperwork — just speak and send

### 📋 **Specialist Intake Feed (Receiving Physician)**
- Real-time priority queue of incoming referrals by specialty
- Network effect: shared feed across all doctors of same specialty
- Urgency-based sorting with overdue flagging (red pins for urgent cases >14 days)
- One-click patient onboarding with automated email notifications

### 📚 **Care Thread / Patient History**
- Single longitudinal patient record keyed to health card ID
- Chronological timeline of all referrals, acceptances, and clinical notes
- Full context sharing across the entire care network
- Reduces repeat diagnostics and medical errors

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** SQLite with SQLAlchemy ORM
- **AI:** Anthropic Claude API (claude-sonnet-4-20250514)
- **Email:** SMTP via Resend.com
- **Auth:** Role-based login with localStorage

### Frontend
- **Framework:** React + TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **API Client:** Typed fetch wrappers

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Deployment:** Ready for cloud platforms (Render, etc.)

## How to Run/View the Demo

### Prerequisites
- Node.js >= 18
- Python >= 3.11
- Docker (optional, for containerized deployment)

### Local Development Setup

1. **Clone and navigate to the project:**
   ```bash
   cd healthcare-hackathon
   ```

2. **Backend Setup:**
   ```bash
   cd backend

   # Create virtual environment
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux

   # Install dependencies
   pip install -r requirements.txt

   # Copy environment file and configure
   cp .env.example .env
   # Edit .env with your API keys (Anthropic, Resend)

   # Load demo data
   python seed.py

   # Start dev server
   python -m uvicorn main:app --reload
   ```
   Backend runs at: http://localhost:8000
   API docs: http://localhost:8000/docs

3. **Frontend Setup:**
   ```bash
   cd frontend

   # Install dependencies
   npm install

   # Start dev server
   npm run dev
   ```
   Frontend runs at: http://localhost:5173

### Demo Script (3 minutes)

1. **Login as Referring Doctor** (Dr. Sarah Chen)
   - Select patient from roster
   - Start appointment session

2. **AI-Powered Intake**
   - Speak or type patient symptoms
   - Watch AI extract clinical notes in real-time
   - AI suggests specialist type and urgency score

3. **One-Click Referral**
   - Review/edit AI-generated referral packet
   - Click "Send Referral" — zero forms required

4. **Specialist Perspective** (Login as Dr. Marcus Webb - Psychiatrist)
   - View urgency-sorted referral queue
   - Accept referral with one click
   - Patient receives automated booking email

5. **Care Continuity**
   - View patient's complete care thread
   - See full clinical history across all providers

### Docker Deployment (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build
```

Frontend: http://localhost:3000
Backend: http://localhost:8000

### Production Deployment

The application is configured for deployment on platforms like Render, Railway, or Vercel. Configure these environment variables:

- `ANTHROPIC_API_KEY` - Your Claude API key
- `EMAIL_HOST=smtp.resend.com`
- `EMAIL_USER=resend`
- `EMAIL_PASS` - Your Resend API key
- `DATABASE_URL` - Database connection string
- `BOOKING_PUBLIC_BASE_URL` - Your deployed frontend URL

## Key Features

✅ **Zero Cognitive Load** - Adds no steps to physician workflow
✅ **Real-time AI Transcription** - Ambient clinical note generation
✅ **Network Effects** - Shared specialist feeds scale automatically
✅ **Urgency-Based Routing** - Prevents care delays
✅ **Care Continuity** - Complete patient history sharing
✅ **Automated Notifications** - Email booking links to patients
✅ **Responsive Design** - Works on all devices
✅ **Type-Safe** - Full TypeScript coverage, zero errors

## API Endpoints

- `POST /login` - Doctor authentication
- `GET /patients` - Patient roster
- `GET /patients/{id}/thread` - Care history
- `POST /referrals` - Create referral
- `GET /referrals` - Specialist feed
- `POST /referrals/{id}/accept` - Accept referral
- `POST /ai/transcript` - AI note extraction
- `GET /doctors` - Doctor directory

---

**Built for healthcare innovation.** Reducing friction, connecting providers, improving patient outcomes.</content>
<parameter name="filePath">c:\Users\Jay\healthcare\HealthcareHackathon\readme.md
