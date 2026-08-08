# InvestOps AI — Deployment & Infrastructure Guide

Comprehensive deployment guide for **InvestOps AI**, covering multi-stage Docker containerization, local `docker-compose` stack orchestration, Railway backend deployment, Vercel frontend deployment, and environment variable configurations.

---

## 🐋 Container Architecture

InvestOps AI utilizes production multi-stage Docker images to minimize container footprint and enhance runtime security.

### 1. FastAPI Backend Container (`Dockerfile.api`)
- **Base Image**: `python:3.11-slim`
- **User**: Non-root user `investops` (UID/GID 1001)
- **Healthcheck**: Polling `http://localhost:8000/health` every 30s
- **Process Manager**: Uvicorn with 4 worker processes

```dockerfile
# Build command
docker build -t investops-api:latest -f Dockerfile.api .
```

### 2. Next.js Frontend Container (`Dockerfile.web`)
- **Base Image**: `node:20-alpine`
- **User**: Non-root user `nextjs` (UID/GID 1001)
- **Output**: Standalone Next.js server trace (`node server.js`)
- **Port**: 3000

```dockerfile
# Build command
docker build -t investops-web:latest -f Dockerfile.web .
```

---

## 🎛️ Docker Compose Local Stack Setup

Run the full local multi-service stack (PostgreSQL 16, FastAPI Backend, Next.js Web Frontend) with one command:

```bash
docker compose up --build -d
```

### Services Included

| Service | Image / Build | Internal Port | Host Port | Description |
| :--- | :--- | :--- | :--- | :--- |
| `db` | `postgres:16-alpine` | `5432` | `5432` | Durable relational database |
| `api` | `Dockerfile.api` | `8000` | `8000` | FastAPI Control Plane Service |
| `web` | `Dockerfile.web` | `3000` | `3000` | Next.js Institutional Web UI |

---

## 🚂 Railway Backend Deployment

The FastAPI control plane and PostgreSQL database deploy to **Railway** using `railway.json`.

### Railway Configuration (`railway.json`)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.api"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 5
  }
}
```

### Railway Deployment Steps
1. Install Railway CLI: `npm i -g @railway/cli`
2. Link project: `railway link`
3. Provision PostgreSQL database on Railway platform.
4. Set Environment Variables in Railway Dashboard (see schema below).
5. Deploy API service: `railway up --service investops-api`

---

## 🔺 Vercel Frontend Deployment

The Next.js 14 web application deploys to **Vercel** using `vercel.json` with automated API rewrites pointing to the Railway production API URL.

### Vercel Configuration (`vercel.json`)
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs",
  "buildCommand": "cd apps/web && npm run build",
  "outputDirectory": "apps/web/.next",
  "rewrites": [
    {
      "source": "/api/v1/:path*",
      "destination": "https://${RAILWAY_BACKEND_URL}/api/v1/:path*"
    }
  ]
}
```

### Vercel Deployment Steps
1. Install Vercel CLI: `npm i -g vercel@latest`
2. Link project: `vercel link`
3. Deploy to production: `vercel --prod`

---

## 🔑 Environment Variables Schema Reference

| Variable Name | Description | Default / Example | Required |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | Target environment mode | `production` / `development` | Yes |
| `LOG_LEVEL` | Application logging verbosity | `INFO` / `DEBUG` | Yes |
| `POSTGRES_USER` | PostgreSQL user account | `postgres` | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL user password | `postgres` | Yes |
| `POSTGRES_DB` | PostgreSQL database name | `investops` | Yes |
| `DATABASE_URL` | SQLAlchemy connection string | `postgresql+psycopg://postgres:postgres@db:5432/investops` | Yes |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | `super-secret-investops-institutional-jwt-key` | Yes |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token validity window in mins | `480` | Yes |
| `LLM_PROVIDER` | Primary AI LLM provider | `anthropic` / `openai` | Yes |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key | `sk-ant-api03-...` | Optional |
| `OPENAI_API_KEY` | OpenAI GPT-4o API Key | `sk-proj-...` | Optional |
| `MOCK_LLM_RESPONSES` | Toggle deterministic fallback LLM | `true` | Yes |
| `MOCK_BROKER_EXECUTION` | Toggle sandbox FIX broker execution | `true` | Yes |
| `NEXT_PUBLIC_API_URL` | Public frontend API base URL | `http://localhost:8000/api/v1` | Yes |
