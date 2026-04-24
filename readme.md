# AI-Powered Procurement Audit System

> An intelligent, enterprise-grade auditing system built on the **SAP Cloud Application Programming Model (CAP)**. This project bridges the gap between manual document review and automated business processes by utilizing a **RAG-based AI Sidecar** for real time contract compliance and risk assessment, designed for deployment on the **SAP Business Technology Platform (BTP)**.

---

## The Problem

Manual procurement auditing in large enterprises is error-prone, slow, and suffers from **"Alert Fatigue."** When every minor discrepancy is flagged with the same urgency as a critical policy violation, auditors lose trust in the system and operational efficiency suffers.

---

## The Solution

This application implements a **RAG (Retrieval-Augmented Generation)** pipeline that analyzes purchase orders, whether manually entered or extracted from PDFs against specific contract terms retrieved from a Vector Database. It dynamically assigns a **Heuristic Severity Score (1.0 – 9.0)** to every PO, allowing procurement officers to focus their time on high-impact financial risks while auto-validating compliant records.

---

## 🏗️ Architecture Overview

The system follows a modular microservices architecture, decoupling resource-heavy AI analysis logic from the core SAP backend.

```
┌──────────────────────────┐        ┌──────────────────────────────┐
│   CAP Backend (Node.js)  │──────▶│   AI Sidecar (FastAPI)       │
│   SAP HANA Cloud / SQLite│◀──────│   LangChain + Groq (Llama-3) │
│   AuditLogs / PO Store   │        │   ChromaDB Vector Engine      │
└──────────────────────────┘        └──────────────────────────────┘
         ▲                                        ▲
         │                                        │
   Manual UI / PDF Upload ───────────────────────┘
```

### Flow

1. **Ingestion** — Data enters via the web UI (manual entry) or the Python sidecar (PDF upload)
2. **Semantic Retrieval** — ChromaDB is queried to pull the relevant contract clauses for the PO
3. **Risk Assessment** — The LLM evaluates PO data against retrieved clauses and assigns a Risk Score
4. **Logging & Approval** — Validated data is persisted in the SAP database, triggering an automated entry in `AuditLogs` for full traceability

---

## 🚀 Key Features

### 1. Dual-Mode Purchase Order Ingestion
- **Manual Entry** — A clean, structured UI for submitting POs directly into the SAP system
- **Automated PDF Upload** — An AI-driven ingestion pipeline that parses invoice PDFs, extracts key data fields, and submits them for instant validation

### 2. Context-Aware Auditing (RAG)
ChromaDB performs semantic search to retrieve the exact contract clauses relevant to a specific PO *before* the audit analysis. This grounds the AI in real, retrieved contract data — significantly reducing hallucinations compared to standard LLM prompts.

### 3. Heuristic Severity Scoring

| Score | Severity | Trigger |
|---|---|---|
| **9.0** | 🔴 Critical | Contractual breaches (e.g., exceeding credit limits, prohibited vendor usage) |
| **5.0** | 🟡 Moderate | Data quality discrepancies (e.g., vendor mismatches, missing discount terms) |
| **1.0** | 🟢 Compliant | Verified clean records — ready for Fast-Track processing |

### 4. Human-in-the-Loop (HITL) Workflow
A dedicated dashboard interface allows procurement officers to review AI-generated insights, perform manual overrides, and maintain a **permanent, immutable audit trail**.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend | Node.js, SAP CAP (Cloud Application Programming Model) |
| AI Sidecar | Python, FastAPI, LangChain |
| LLM Engine | Groq API — `Llama-3.3-70b-versatile` |
| Vector Engine | ChromaDB (semantic retrieval of contract clauses) |
| Document Intelligence | PyPDF (automated parsing of unstructured PDF invoices) |
| Database | SQLite (Development) → SAP HANA Cloud (Production) |
| Orchestration | Docker, MTA (Multi-Target Application) |

---

## ⚙️ Installation & Setup

### Prerequisites

- Docker Desktop (with WSL 2 enabled)
- Node.js & NPM
- Python 3.11+

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/procure-audit-system.git
cd procure-audit-system
```

---

### 2. AI Sidecar (FastAPI)

```bash
cd ai-engine

# Create a .env file and add your GROQ_API_KEY
# GROQ_API_KEY=your_key_here

pip install -r requirements.txt
python main.py
```

---

### 3. CAP Backend

```bash
cd ..
npm install
cds watch
```

---

### 4. Launch the UI

Open [http://localhost:4004](http://localhost:4004) in your browser.

---

## ☁️ Deployment Strategy (SAP BTP)

This project uses the **SAP MTA (Multi-Target Application)** model to ensure atomic deployments across development, staging, and production environments.

To package the project for production:

```bash
mbt build
```

This generates an `.mtar` artifact that bundles:
- The Node.js CAP service
- The AI Docker container
- Database module descriptors

The artifact is ready for deployment to the **SAP BTP Cloud Foundry** environment.

---

## Security

| Concern | Approach |
|---|---|
| **Credential Management** | Sensitive API keys injected at runtime via environment variables; `.env` excluded via `.gitignore` |
| **CORS** | Cross-Origin Resource Sharing restricted and configured for SAP BTP integration |

---

## Roadmap

- [ ] **Vector Store Migration** — Move from `ChromaDB` to SAP HANA Cloud's native vector storage for improved enterprise scalability
- [ ] **Authentication** — Integration with **SAP XSUAA** for role-based access control (RBAC)
