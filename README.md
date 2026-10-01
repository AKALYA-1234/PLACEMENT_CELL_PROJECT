# College Placement Management & Analytics Portal (Admin Only)

A production-quality, admin-only web application for managing college placement data, normalizing company-wise multi-sheet Excel workbooks, tracking student round progressions, and generating college placement analytics.

> **IMPORTANT**: This system is exclusively for Admin users. There is no student-facing portal.

---

## Technical Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL / SQLite (SQLAlchemy 2.0 ORM)
- **Migrations**: Alembic
- **Auth**: JWT (JSON Web Tokens) with bcrypt password hashing
- **Data Engine**: Pandas & OpenPyXL (Deterministic Excel parser)

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS (Glassmorphic Dark Theme)
- **Routing**: React Router v6
- **HTTP Client**: Axios with JWT Interceptors
- **Icons**: Lucide React
- **Charts**: Recharts

---

## Directory Structure

```
PLACEMENT_CELL_PROJECT/
├── backend/                  # FastAPI Admin Backend
│   ├── app/
│   │   ├── models/           # SQLAlchemy ORM Models (9 tables)
│   │   ├── routers/          # API Route Handlers (/api/auth, /api/health)
│   │   ├── schemas/          # Pydantic Schemas
│   │   ├── services/         # Business Logic Layer
│   │   ├── utils/            # JWT & Security Utilities
│   │   ├── config.py         # Pydantic Settings
│   │   ├── database.py       # Engine & Session Factory
│   │   └── main.py           # FastAPI App Entrypoint
│   ├── alembic/              # Database Migrations
│   ├── seed_admin.py         # Seed script for initial admin user
│   ├── requirements.txt      # Python Dependencies
│   └── .env.example
├── frontend/                 # React + TS Admin Dashboard
│   ├── src/
│   │   ├── api/              # Axios Client & Interceptors
│   │   ├── components/       # ProtectedRoute & UI Shell
│   │   ├── contexts/         # AuthContext Provider
│   │   ├── pages/            # LoginPage & DashboardPage
│   │   ├── types/            # TypeScript Interfaces
│   │   ├── App.tsx           # Router Configuration
│   │   └── main.tsx          # React Entrypoint
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── sample_data/              # Sample company placement Excel sheets
├── docs/                     # System architecture & normalization docs
├── README.md
├── .gitignore
└── .env.example
```

---

## Quick Start Guide

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate

pip install -r requirements.txt

# Run migrations & seed initial admin user
alembic upgrade head
python seed_admin.py

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend will run at: `http://localhost:8000`  
Interactive API Docs (Swagger): `http://localhost:8000/docs`

Default Credentials created by `seed_admin.py`:
- **Username**: `admin`
- **Password**: `admin123`

### 2. Frontend Setup

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Frontend will run at: `http://localhost:5173`

---

## Core Data Concepts

Placement stages are normalized into 3 standard college categories:
1. **REGISTERED** — Student signed up for the company drive.
2. **PROGRESSION** — Student moved forward into round 2, round 3, technical interview, HR round, etc.
3. **PLACED** — Student received final placement / offer.

Overall student status logic:
- `PLACED`: Placed in at least 1 company.
- `IN PROCESS`: Progressed beyond round 1 in at least 1 active drive, but not yet placed.
- `NOT PLACED`: Completed drives without any offer.

---

## Phase Roadmap

- [x] **Phase 1**: Project Foundation, Database Schema, Admin Auth & Application Shell
- [ ] **Phase 2**: Excel Parsing Engine & Normalization Rules
- [ ] **Phase 3**: Import Validation Preview & Transactional Database Commit
- [ ] **Phase 4**: Analytics Dashboard & Departmental Metrics
- [ ] **Phase 5**: Student Search, Company Profiles & Export Engine
- [ ] **Phase 6**: Production Hardening, Docker Support & Final Audit
