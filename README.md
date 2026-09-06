# SentinelAI – Enterprise LLM Security & Monitoring Platform

SentinelAI is a security gateway platform designed to sit between users and LLM providers, monitor interactions, and provide a modern enterprise-grade administration experience. Phase 1 focuses on the complete foundation: authentication, RBAC, user management, audit logs, settings, health monitoring, responsive UI, and deployment assets.

## Features

- Modern dark dashboard and enterprise UI
- JWT access and refresh authentication
- Password hashing with bcrypt
- Role-based access control for Admin, Security Analyst, and User
- User management, profile, settings, and audit log pages
- Health check endpoint for backend, database, and Redis
- Docker and Docker Compose deployment setup

## Tech Stack

### Frontend
- React 19
- Vite
- TypeScript
- Tailwind CSS
- React Router
- Axios
- TanStack Query
- React Hook Form
- Zod
- Framer Motion

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT
- Passlib
- bcrypt

### Database & Infrastructure
- PostgreSQL
- Redis
- Docker
- Docker Compose

## Folder Structure

- frontend/ – Vite React front end
- backend/ – FastAPI application
- database/ – schema and migration assets
- docker/ – container build files
- docs/ – documentation and design notes
- scripts/ – automation scripts

## Installation

### Docker Setup

```bash
docker compose up --build
```

The frontend will be available at http://localhost:5174 and the backend at http://localhost:8000.

### Manual Setup

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Files

- backend/.env.example
- frontend/.env.example

## Screenshots

Placeholder: Add screenshots of the login, dashboard, and settings screens in the docs/assets folder.

## Notes

This phase does not include AI security detection yet. It establishes the full foundation for future LLM threat and anomaly monitoring features.
