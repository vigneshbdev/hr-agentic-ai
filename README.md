# HR Agentic AI — HR Copilot

An agentic AI-powered HR Copilot that provides a conversational interface for employees and HR teams.

The system combines **LangGraph, Google Gemini, RAG, Supabase PostgreSQL/pgvector, and role-based tools** to answer HR policy questions, retrieve employee information, manage leave requests, and perform HR actions through natural language.

## Live Demo

**Application:**  
https://pixel-perfect-render-8298.lovable.app/

**GitHub:**  
https://github.com/vigneshbdev/hr-agentic-ai

---

## Key Capabilities

### Employee

- Ask HR policy questions using RAG
- View personal employee information
- Check leave balances
- Check leave eligibility
- Calculate leave duration
- Submit leave requests
- View leave request history
- Continue conversations with contextual follow-up questions

### HR

The same Copilot interface provides HR-specific capabilities based on the authenticated user's role:

- View pending leave requests
- Approve leave requests
- Reject leave requests with a reason
- Access employee leave information
- Query HR policies

HR actions are protected by **server-side role-based authorization**.

---

## Architecture

```text
                    ┌─────────────────────┐
                    │   React / TypeScript│
                    │     HR Copilot UI   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    │ Authentication/Auth │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    LangGraph Agent  │
                    │ Tool Orchestration  │
                    └──────┬───────┬──────┘
                           │       │
              ┌────────────┘       └─────────────┐
              ▼                                  ▼
       ┌──────────────┐                  ┌──────────────┐
       │ Policy RAG   │                  │ HR Tools     │
       │ Gemini       │                  │ Leave        │
       │ Embeddings   │                  │ Employee     │
       │ pgvector     │                  │ Eligibility  │
       └──────┬───────┘                  │ Approval     │
              │                          └──────┬───────┘
              └──────────────┬──────────────────┘
                             ▼
                    ┌─────────────────────┐
                    │ Supabase PostgreSQL │
                    │      + pgvector     │
                    └─────────────────────┘
```

The LLM acts as the **reasoning and orchestration layer**, while deterministic business operations such as leave calculations, validations, and database updates are handled by dedicated tools.

---

## Agentic Workflow

A typical request flows through:

```text
User Question
     ↓
LangGraph Agent
     ↓
Determine required capability
     ↓
Select appropriate tool
     ↓
Execute tool / retrieve knowledge
     ↓
Return result to Agent
     ↓
Generate final response
```

For policy questions, the agent uses RAG:

```text
Question
   ↓
Gemini Embedding
   ↓
Supabase pgvector
   ↓
Relevant Policy Chunks
   ↓
Gemini
   ↓
Answer + Source Citation
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React / TypeScript |
| Backend | Python / FastAPI |
| Agent Framework | LangGraph |
| LLM | Google Gemini |
| Embeddings | Google Gemini Embeddings |
| RAG / Vector DB | Supabase pgvector |
| Database | Supabase PostgreSQL |
| Authentication | JWT + bcrypt |
| Frontend Hosting | Lovable |
| Backend Hosting | Render |

---

## Security

The application uses authentication and server-side authorization to protect employee and HR operations.

- JWT-based authentication
- Passwords stored using bcrypt hashing
- Employee identity derived from the authenticated session
- Employee-specific tools use the authenticated employee ID
- HR operations require the `hr` role
- HR authorization is enforced inside backend tools
- Supabase service-role credentials remain backend-only
- RAG policy sources are returned with citations for traceability

The frontend does not determine whether an operation is authorized.

---

## Project Structure

```text
hr-agent/
├── app/
│   ├── agent/          # LangGraph agent and state
│   ├── auth/           # Authentication and authorization
│   ├── db/             # Supabase database client
│   ├── llm/            # LLM configuration
│   ├── rag/            # Document ingestion and retrieval
│   └── tools/          # HR business tools
│
├── requirements.txt
└── .gitignore
```

---

## Deployment

The application is deployed using:

- **Lovable** — React frontend
- **Render** — FastAPI backend
- **Supabase** — PostgreSQL database and pgvector

This setup provides a lightweight deployment architecture suitable for demonstrating the complete agentic workflow without requiring dedicated infrastructure.

---

## Example Queries

### Employee

> What is my leave balance?

> Am I eligible for leave?

> How many casual leaves do I get?

> Show my leave requests.

> Apply for casual leave from October 9 to October 10.

### HR

> Show me all pending leave requests.

> Approve leave request 12.

> Reject leave request 13 because the requested leave overlaps with a critical project deadline.

---

## Project Goal

The project demonstrates how an enterprise HR workflow can be transformed into an **agentic conversational system**, where the LLM coordinates specialized tools and knowledge sources while authentication, authorization, business rules, and data access remain under deterministic backend control.
