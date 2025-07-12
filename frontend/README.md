# OLAIR Frontend

This is the **frontend React application** for the **Multi-Agent Lease Analyzer** project built using **React + TypeScript**. It serves as the minimal UI layer for interacting with the backend API powered by a conversational AI agent, RAG search, and CRM system.

---

## 🚀 Features Implemented

- 🔹 File upload interface for lease analysis
- 🔹 Real-time chat component (integrates with backend `/chat`)
- 🔹 CRM page to manage users (create, edit, delete)
- 🔹 Organized folder structure for clean codebase
- 🔹 Modular React + TypeScript setup

---

## 🧾 Folder Structure

```bash
src/
├── api/              # Axios client and endpoint constants
│   ├── client.ts
│   └── endpoints.ts
├── components/       # Reusable UI components
│   ├── ChatBox.tsx
│   ├── FileUploader.tsx
│   └── ClauseViewer.tsx
├── pages/            # Route-level pages
│   ├── Home.tsx
│   └── CRM.tsx
├── hooks/            # Custom React hooks
│   └── useChat.ts
├── types/            # TypeScript types/interfaces
│   ├── lease.d.ts
│   └── user.d.ts
├── utils/            # Utility/helper functions
│   └── formatText.ts
├── App.tsx           # App router
└── main.tsx          # Entry point

