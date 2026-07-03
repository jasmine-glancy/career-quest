# Career Quest 🗺️

Career Quest is a career intelligence system that helps users track job applications, manage resume versions, and analyze job-fit using structured data and optional AI-assisted insights.

## 📚 Table of Contents

- [Career Quest 🗺️](#career-quest-️)
  - [📚 Table of Contents](#-table-of-contents)
  - [📌 Overview](#-overview)
  - [🧭 Philosophy](#-philosophy)
  - [🧱 Architecture](#-architecture)
    - [Backend](#backend)
    - [Frontend](#frontend)
  - [🗂️ Core Features](#️-core-features)
    - [1. Job Application Tracker](#1-job-application-tracker)
    - [2. Resume Versioning System](#2-resume-versioning-system)
    - [3. Job-Fit AI Analyzer](#3-job-fit-ai-analyzer)
    - [4. Career Insights Dashboard (Phase 2)](#4-career-insights-dashboard-phase-2)
  - [🧠 AI \& Enrichment Layer](#-ai--enrichment-layer)
    - [Job Fit Analysis Service](#job-fit-analysis-service)
    - [Future Enhancements](#future-enhancements)
  - [🗄️ Data Model (High-Level)](#️-data-model-high-level)
    - [Users](#users)
    - [Resumes](#resumes)
    - [ResumeVersions](#resumeversions)
    - [Jobs](#jobs)
    - [Applications](#applications)
    - [AIAnalysis](#aianalysis)
  - [🔌 API Structure (FastAPI)](#-api-structure-fastapi)
    - [Auth APIs (Phase 2)](#auth-apis-phase-2)
    - [Resume APIs](#resume-apis)
    - [Jobs APIs](#jobs-apis)
    - [Application APIs](#application-apis)
    - [AI Services APIs](#ai-services-apis)
  - [🎨 Frontend Structure (Next.js)](#-frontend-structure-nextjs)
    - [Pages](#pages)
    - [UI Components](#ui-components)
  - [⚙️ System Design Notes](#️-system-design-notes)
    - [Backend Design Principles](#backend-design-principles)
    - [Performance Considerations](#performance-considerations)
  - [🧪 Future Enhancements](#-future-enhancements)
    - [Phase 2](#phase-2)
    - [Phase 3](#phase-3)
    - [Phase 4](#phase-4)
  - [🚀 Getting Started (Dev Setup)](#-getting-started-dev-setup)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)

## 📌 Overview

CareerFlow is a full-stack application designed to act as a personal career CRM. It combines job application tracking, resume version control, and AI-driven job-fit analysis into a unified system.

The goal is to help users:

- Track job applications through a structured pipeline
- Maintain and version resumes tailored to specific roles
- Analyze job fit using structured AI outputs
- Gain insights into career progression and skill gaps

## 🧭 Philosophy

This project is designed as a:

- Career intelligence system
- Not just a CRUD app
- Not just an AI wrapper

The goal is to combine:

- Data engineering principles
- Product design thinking
- Practical AI integration
- Real-world career utility

## 🧱 Architecture

### Backend

- FastAPI (REST API layer)
- PostgreSQL (primary database)
- SQLAlchemy (ORM)
- Alembic (database migrations)
- Redis (optional: caching, background jobs, queues)

### Frontend

- Next.js (App Router)
- TypeScript
- Tailwind CSS

## 🗂️ Core Features

### 1. Job Application Tracker

- Create and manage job applications
- Track status:
  - Saved
  - Applied
  - Interviewing
  - Offer
  - Rejected
- Store notes, deadlines, and company details

---

### 2. Resume Versioning System

- Create multiple resume versions per user
- Link resumes to specific job applications
- Track changes over time
- Support structured storage of:
  - Experience
  - Skills
  - Projects
  - Education

### 3. Job-Fit AI Analyzer

- Compare resume vs job description
- Generate:
  - Match score
  - Strengths
  - Skill gaps
  - Suggested resume improvements
- Return structured JSON outputs for UI rendering

### 4. Career Insights Dashboard (Phase 2)

- Application success rate
- Interview conversion rate
- Skill gap trends
- Resume performance analytics

## 🧠 AI & Enrichment Layer

### Job Fit Analysis Service

- Input:
  - Resume data
  - Job description
- Output:
  - Structured evaluation (JSON schema)
  - Match scoring
  - Recommendations for improvement

### Future Enhancements

- Resume auto-optimization per job
- Skill extraction from resumes
- Job clustering by similarity
- Application success prediction

## 🗄️ Data Model (High-Level)

### Users

- user_id
- name
- email
- created_at

### Resumes

- resume_id
- user_id
- title
- created_at

### ResumeVersions

- resume_version_id
- resume_id
- snapshot_json
- created_at

### Jobs

- job_id
- title
- company
- description
- url
- location

### Applications

- application_id
- user_id
- job_id
- resume_version_id
- status
- applied_at

### AIAnalysis

- analysis_id
- application_id
- match_score
- strengths_json
- gaps_json
- recommendations_json
- created_at

## 🔌 API Structure (FastAPI)

### Auth APIs (Phase 2)

- POST /auth/register
- POST /auth/login

### Resume APIs

- GET /resumes
- POST /resumes
- GET /resumes/{id}
- POST /resumes/{id}/version

### Jobs APIs

- GET /jobs
- POST /jobs
- GET /jobs/{id}

### Application APIs

- GET /applications
- POST /applications
- PATCH /applications/{id}/status

### AI Services APIs

- POST /ai/analyze-fit
- POST /ai/optimize-resume

## 🎨 Frontend Structure (Next.js)

### Pages

- /dashboard (overview metrics)
- /applications (job pipeline board)
- /resumes (resume manager)
- /jobs/[id] (job detail + AI analysis)
- /resume/[id] (resume editor/versioning view)

### UI Components

- Application Kanban board
- Resume editor (structured sections)
- Job detail panel
- AI insights card
- Analytics charts

## ⚙️ System Design Notes

### Backend Design Principles

- API-first architecture
- Separation of AI layer from core CRUD logic
- Structured JSON responses for all AI outputs
- Strict schema validation via Pydantic

### Performance Considerations

- Redis caching for AI results (future)
- Async FastAPI endpoints for heavy operations
- Database indexing on:
  - user_id
  - job_id
  - application status

## 🧪 Future Enhancements

### Phase 2

- AI resume tailoring per job
- Skill graph generation
- Job recommendation engine

### Phase 3

- Chrome extension for job saving
- LinkedIn integration
- Auto-apply assistant (careful with ethics/limits)

### Phase 4

- Public portfolio mode
- Shareable career dashboard
- Team/job referral tracking

## 🚀 Getting Started (Dev Setup)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
