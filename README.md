# HR Agentic AI

An enterprise-oriented **HR Assistant powered by Agentic AI** that enables employees to interact with HR services through a conversational interface.

The application combines **LangGraph, Gemini, Retrieval-Augmented Generation (RAG), PostgreSQL/pgvector, and HR data tools** to answer policy questions, retrieve employee-specific information, calculate leave requirements, validate leave requests, and submit leave applications.

## 🚀 Live Demo

**HR Copilot:**  
https://pixel-perfect-render-8298.lovable.app/

The application provides an authenticated conversational interface for interacting with the HR Agent.

---

## Overview

The HR Agentic AI application provides employees with a single conversational interface for common HR activities.

Instead of relying only on a static chatbot, the system dynamically determines when it needs to:

- Retrieve information from HR policy documents
- Query employee-specific HR data
- Calculate leave durations
- Validate leave availability
- Check employee eligibility
- Retrieve previous leave requests
- Submit a leave request

The agent uses **LangGraph** to orchestrate the interaction between the language model and application tools.

---

## Key Features

### 🔐 Employee Authentication

Employees authenticate using their registered email address and password.

The backend issues a JWT access token which is used to authorize subsequent API requests.

Employee identity is passed into the agent execution context so that employee-specific tools operate against the authenticated employee.

---

### 💬 Conversational HR Assistant

Employees can ask HR-related questions using natural language.

Examples:

```text
What is my joining date?

How many earned leave days do I have?

Can I take 5 days of earned leave?

What is the sick leave policy?

How many days of casual leave can I carry forward?

What are the rules for taking leave?
```

The agent determines which tools or knowledge sources are required to answer the question.

---

### 📚 HR Policy RAG

HR policy documents are processed and stored as vectorized document chunks.

The RAG pipeline:

```text
HR Policy PDF
      ↓
Text Extraction
      ↓
Document Chunking
      ↓
Gemini Embeddings
      ↓
PostgreSQL + pgvector
      ↓
Semantic Search
      ↓
Relevant Policy Context
      ↓
LLM Response
```

The application uses **Gemini Embeddings** to generate vector representations and PostgreSQL with **pgvector** for semantic similarity search.

This allows the assistant to answer questions based on the organization's HR policy documents rather than relying only on the language model's general knowledge.

---

### 👤 Employee Information

The agent can retrieve information belonging to the authenticated employee, including:

- Employee name
- Employee code
- Email
- Department
- Joining date

---

### 🏖️ Leave Balance

Employees can retrieve their current leave balances.

Supported leave information includes:

- Earned Leave
- Casual Leave
- Sick Leave
- Other configured leave types

---

### 📅 Leave Calculation

The application provides a dedicated calculation tool for determining leave duration.

The calculation is performed deterministically by the application rather than relying on the language model to perform date arithmetic.

---

### ✅ Leave Eligibility

The agent can check whether an employee satisfies the configured leave eligibility criteria.

Eligibility is evaluated using employee information stored in the database.

---

### 🔎 Leave Validation

Before submitting a leave request, the application can validate whether the employee has sufficient leave balance.

The validation is performed through a backend tool against the employee's actual leave balance.

---

### 📝 Leave Request Submission

Employees can explicitly request the agent to submit a leave request.

The submission tool validates:

- Leave type
- Date format
- Date range
- Available leave balance
- Authenticated employee identity

The request is stored in the `leave_requests` table with a `Pending` status.

---

### 📋 Leave Request History

Employees can retrieve their submitted leave requests.

The assistant can provide information such as:

- Request ID
- Leave type
- Start date
- End date
- Status
- Request creation time

---

### 🧠 Conversation Context

The application maintains conversation context using a conversation ID.

This allows follow-up questions to reference information from previous messages.

Example:

```text
User:
How many earned leave days do I have?

Agent:
You have 12 earned leave days.

User:
Can I use 5 of them?

Agent:
Yes. You have sufficient earned leave balance for 5 days.
```

---

# Agent Architecture

```text
┌──────────────────────────────┐
│        Employee UI           │
│     Web / Chat Interface     │
└──────────────┬───────────────┘
               │
               │ HTTP / REST
               ▼
┌──────────────────────────────┐
│        FastAPI Backend       │
│                              │
│  Authentication              │
│  API Layer                   │
│  Agent Execution             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        LangGraph Agent       │
│                              │
│  ┌────────────────────────┐  │
│  │      LLM / Gemini      │  │
│  └───────────┬────────────┘  │
│              │               │
│       Tool Selection         │
│              │               │
│  ┌───────────┴────────────┐  │
│  │        Tools           │  │
│  │                        │  │
│  │ Employee Profile       │  │
│  │ Leave Balance          │  │
│  │ Policy Search          │  │
│  │ Leave Eligibility      │  │
│  │ Leave Calculation      │  │
│  │ Leave Validation       │  │
│  │ Leave Submission       │  │
│  │ Leave History          │  │
│  └────────────────────────┘  │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌─────────────────┐
│ PostgreSQL   │  │ HR Policy RAG   │
│              │  │                 │
│ Employees    │  │ Gemini          │
│ Leave        │  │ Embeddings      │
│ Requests     │  │       ↓         │
│ Balances     │  │ pgvector        │
└──────────────┘  └─────────────────┘
```

---

# Agent Workflow

The application uses a tool-calling workflow implemented with LangGraph.

```text
User Message
     │
     ▼
┌─────────────┐
│ Agent Node  │
└──────┬──────┘
       │
       ▼
 Does the agent
 need a tool?
    /       \
  Yes        No
   │          │
   ▼          ▼
Tools Node   Final Response
   │
   ▼
Tool Result
   │
   ▼
Agent Node
   │
   ▼
Final Response
```

This allows the agent to perform multi-step operations when required.

---

# Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React / TypeScript |
| Frontend Platform | Lovable |
| Backend | Python |
| API Framework | FastAPI |
| Agent Framework | LangGraph |
| LLM | Google Gemini |
| Embeddings | Gemini Embedding |
| Database | PostgreSQL |
| Vector Database | PostgreSQL + pgvector |
| Database Platform | Supabase |
| Authentication | JWT + bcrypt |
| Document Processing | PyPDF |
| Deployment | Render / Vercel |
| API Communication | REST |

---

# Project Structure

```text
hr-agentic-ai/
│
├── app/
│   ├── agent/
│   │   ├── graph.py
│   │   ├── memory.py
│   │   └── state.py
│   │
│   ├── auth/
│   │   ├── security.py
│   │   ├── service.py
│   │   └── dependencies.py
│   │
│   ├── db/
│   │   └── supabase.py
│   │
│   ├── llm/
│   │   └── client.py
│   │
│   ├── rag/
│   │   ├── chunker.py
│   │   ├── document_loader.py
│   │   ├── embeddings.py
│   │   ├── ingest.py
│   │   └── repository.py
│   │
│   ├── tools/
│   │   ├── calculation.py
│   │   ├── eligibility.py
│   │   ├── employee.py
│   │   ├── leave.py
│   │   ├── leave_request.py
│   │   ├── leave_requests.py
│   │   ├── leave_validation.py
│   │   └── policy.py
│   │
│   └── main.py
│
├── requirements.txt
└── .gitignore
```

---

# Database Model

The application uses PostgreSQL with the following primary entities:

```text
employees
    │
    ├───────────────┐
    │               │
    ▼               ▼
leave_balances   leave_requests
```

### Employees

Stores employee identity and profile information.

### Leave Balances

Stores leave balances by:

- Employee
- Leave type
- Year

### Leave Requests

Stores employee leave applications and their current status.

### Policy Documents

Stores processed HR policy chunks and their vector embeddings.

---

# Configuration

The backend requires environment variables for external services and authentication.

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

GEMINI_API_KEY=your_gemini_api_key

JWT_SECRET=your_strong_jwt_secret
```

Secrets must be configured through the deployment platform's environment-variable settings and should never be committed to Git.

---

# Running Locally

## 1. Clone the repository

```bash
git clone https://github.com/vigneshbdev/hr-agentic-ai.git
cd hr-agentic-ai
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file with the required configuration.

## 5. Start the backend

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

# Example API Flow

### Login

```http
POST /auth/login
```

### Ask the HR Agent

```http
POST /agent
Authorization: Bearer <JWT_TOKEN>
```

### Health Check

```http
GET /health
```

---

# Security Model

The application separates authentication, employee identity, and agent tool execution.

```text
Employee
   ↓
JWT Authentication
   ↓
Authenticated Employee ID
   ↓
LangGraph State
   ↓
Injected into Employee-Specific Tools
   ↓
Database Query
```

Employee-specific tools use the authenticated employee identity rather than accepting an employee ID directly from the language model.

The Supabase service-role key is used only by the backend and must never be exposed to the frontend.

---

# Design Principles

### Tool-Based Actions

Business operations such as retrieving balances, calculating dates, validating leave, and submitting requests are implemented as deterministic backend tools.

### Grounded Policy Responses

HR policy questions are answered using retrieved policy documents rather than relying solely on the LLM's internal knowledge.

### Employee-Scoped Data Access

Employee-specific operations use the authenticated employee identity.

### Deterministic Calculations

Date calculations and leave validation are handled by backend functions rather than asking the LLM to perform business calculations.

### Agentic Orchestration

LangGraph coordinates the interaction between the LLM and application tools, allowing the agent to dynamically select the capabilities required for a request.

---

# Current Scope

The application currently supports:

- Employee authentication
- Employee profile retrieval
- Conversational HR assistance
- HR policy RAG
- Leave balance retrieval
- Leave eligibility checks
- Leave duration calculation
- Leave balance validation
- Leave request submission
- Leave request history
- Multi-turn conversation context

The HR policy content included with the application is **sample/fictional policy content** intended for demonstration purposes.

---

# Future Enhancements

Potential production enhancements include:

- Persistent conversation memory using Redis or PostgreSQL
- Role-based access control for HR administrators
- HR document management and versioning
- Policy document upload through the application
- Approval workflow for managers
- Email/notification integration
- Holiday calendar integration
- Working-day leave calculations
- Duplicate leave-request detection
- API rate limiting
- Comprehensive audit logging
- Observability and agent tracing
- Human approval checkpoints for sensitive actions
- Additional HR workflows such as payroll, benefits, onboarding, and employee support

---

## License

This project is intended for demonstration and evaluation purposes.
