# Inventory & Order Management System

A simplified full-stack inventory and order management app built for the assessment brief.

## Features

- FastAPI backend with product, customer, and order APIs
- React frontend for managing products, customers, and orders
- PostgreSQL database with Docker Compose
- Unique product SKUs and unique customer emails
- Inventory validation before order creation
- Automatic stock reduction after successful order creation
- Environment-variable based configuration
- Dockerfiles for backend and frontend

## Tech Stack

- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- Frontend: React, Vite, lucide-react
- Database: PostgreSQL
- Containers: Docker, Docker Compose

## Quick Start With Docker

1. Copy the environment file:

```bash
cp .env.example .env
```

2. Start the full app:

```bash
docker compose up --build
```

3. Open the app:

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg://inventory:change-me@localhost:5432/inventory_db
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server reads `VITE_API_BASE_URL`. By default it points to `http://localhost:8000`.

## Tests

```bash
cd backend
pip install -r requirements.txt
pytest
```

The included tests use an in-memory SQLite database and cover:

- duplicate product SKU rejection
- duplicate customer email rejection
- successful order creation reducing stock
- failed order creation when stock is insufficient

## Deployment Notes

Use these free hosting-friendly options:

- Backend: Render, Railway, Fly.io, or Koyeb
- Frontend: Vercel, Netlify, or Render Static Site
- Database: Neon, Supabase, Render PostgreSQL, or Railway PostgreSQL
- Docker image: GitHub Container Registry or Docker Hub

Required production environment variables:

- `DATABASE_URL`
- `BACKEND_CORS_ORIGINS`
- `VITE_API_BASE_URL`

Submission should include:

- GitHub repository URL
- Docker image URL
- Live frontend URL
- Live backend API URL

