# 🧱 MultiAgent-Olair: Real-Time AI Agents for Lease & CRM Intelligence

MultiAgent-Olair is a full-stack platform that combines a real-time lease analysis engine with internal CRM capabilities. It empowers commercial real estate professionals to upload, query, and analyze lease clauses and internal knowledge using AI agents backed by vector stores and OpenAI.

---

## 🚀 Tech Stack

### ✨ Frontend (React - Create React App)

* React 18
* Axios (API requests)
* Tailwind CSS + Custom CSS modules
* React State Hooks & Conditional Rendering

### 🪡 Backend (FastAPI)

* FastAPI
* SQLAlchemy ORM + SQLite (or PostgreSQL)
* Pydantic (data validation)
* OpenAI API (GPT-3.5 for LLM inference)
* FAISS-like vector store for embedding search
* File handling for CSV/PDF ingestion

---

## 🌐 Features Overview

### 📄 Upload Engine

* Upload CSVs (`qa`, `property`, `master_clauses`) or PDF leases (WIP)
* Real-time feedback on success/failure
* Store in `/data/` directory

### 🤖 AI Agents

* **Internal KB Agent**: Searches across:

  * Q\&A pairs
  * Property data
  * Contract clauses
* **Lease Clause Agent**: Performs risk & redline analysis on lease text
* All agents use OpenAI embeddings + GPT-3.5 for synthesis

### 📉 Lease Preview

* View uploaded lease data (Q\&A or Property)
* Table with pagination, search
* Switching between data types

### 📢 Chat Assistant

* Conversational assistant
* Mode toggles:

  * General (auto vector search)
  * Internal KB only
* Uses source: `auto`, `internal`, `qa`, `property`, `master_clauses`, `lease`

### 👥 CRM Dashboard

* Manage Users (add/edit/delete)
* View conversations per user
* View/delete assistant replies

---

## 🚧 Setup Guide

### 1. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run FastAPI backend
uvicorn main:app --reload --port 8000
```

* Base URL: `http://localhost:8000`

> Create `.env` file with your OpenAI key:

```env
OPENAI_API_KEY=sk-xxxxx
```

---

### 2. Frontend Setup (React - CRA)

```bash
cd frontend
npm install
npm start
```

* App runs on: [http://localhost:3000](http://localhost:3000)

#### Axios Config (`src/api/axiosconfig.ts`)

```ts
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000"
});

export default api;
```

---

## 📚 API Endpoints

### Chat Routes (`/api/routes/chat`)

* `POST /` - General or internal chat
* `POST /internal` - Internal KB enhanced chat
* `POST /lease` - Lease analysis questions
* `POST /analyze-clause` - Risk analysis for one clause
* `GET /health` - System health check
* `GET /sources` - Available source types
* `GET /kb-stats` - Stats of internal KBs

### CRM Routes (`/api/routes/crm`)

* `GET /users` - List users
* `POST /users` - Add user
* `PUT /users/{id}` - Update user
* `DELETE /users/{id}` - Delete user
* `GET /users/{id}/conversations` - User history
* `GET /conversations` - All conversations
* `POST /conversations` - Add conversation

### Upload Routes (`/api/routes/upload`)

* `POST /docs` - Upload CSVs (qa, property, clauses)
* `GET /internal-knowledge?type=qa|property` - View uploaded samples

---

## 💡 Use Cases

* Real estate teams asking natural questions like:

  > "What is the annual rent for 123 Main St?"

* Legal/compliance asking:

  > "Show exclusivity or termination clauses"

* Internal teams asking:

  > "How do I submit a tenant repair request?"

---

## 🚫 Limitations

* PDF ingestion not yet populating vector stores
* No user authentication
* Single user\_id (for now)
* SQLite for demo; replace with PostgreSQL in production

---

## 🚀 Future Plans

* ✅ PDF parsing + populate\_vector\_store
* ✅ Conversation logging for all agents
* ✅ Admin dashboard for clause risk management
* ✅ Tenant engagement bot with chat history

---

## 📊 Sample Questions to Try

* "What are the termination clauses?"
* "What's the broker email for 456 Pine Ave?"
* "How do I submit maintenance requests?"

---

## 📅 Developed for

**Olair** x AI Agents Hackathon
