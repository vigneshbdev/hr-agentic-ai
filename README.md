## Why HR Copilot?

HR teams handle a large number of repetitive employee requests every day, including:

- Leave balance enquiries
- Leave policy questions
- Leave eligibility checks
- Leave calculations
- Leave request submissions
- Leave request status enquiries
- Employee information requests

Traditional approaches typically require employees to navigate multiple HR systems, search policy documents, or contact HR directly.

**HR Copilot brings these interactions into a single conversational interface.**

The application combines organizational knowledge, employee-specific data, deterministic business operations, and AI-driven orchestration to provide contextual HR assistance.

---

# What Makes HR Copilot Agentic?

HR Copilot is not implemented as a simple question-and-answer chatbot.

The application uses an **agentic tool-calling architecture** where the language model determines which capabilities are required for a user's request.

For example:

```text
User:
"Can I take 5 days of earned leave from October 10 to October 14?"

                         │
                         ▼
                  LangGraph Agent
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
        Calculate     Check Leave   Search
        Duration       Balance      Policy
             │           │           │
             └───────────┼───────────┘
                         ▼
                 Validate Request
                         │
                         ▼
                  Agent Response
```

The agent does not need to follow one fixed workflow for every question.

Different requests can result in different tool selections.

For example:

```text
"What is my joining date?"
        ↓
get_employee_profile
```

```text
"How many earned leave days do I have?"
        ↓
get_leave_balance
```

```text
"What is the earned leave carry-forward policy?"
        ↓
search_hr_policy
```

```text
"Can I take 5 days of earned leave?"
        ↓
get_leave_balance
        +
validate_leave_request
```

```text
"Submit my leave from October 10 to October 14."
        ↓
calculate_leave_days
        +
validate_leave_request
        +
submit_leave_request
```

This combination of **reasoning, tool selection, retrieval, deterministic processing, and action execution** forms the core agentic behavior of the application.

---

# Agent Tool Catalog

The agent exposes focused tools rather than allowing the language model to directly access the database.

| Tool | Category | Description |
|---|---|---|
| `get_employee_profile` | Employee Data | Retrieves the authenticated employee's profile |
| `get_leave_balance` | Employee Data | Retrieves available leave balances |
| `search_hr_policy` | RAG | Searches HR policy documents using vector similarity |
| `check_leave_eligibility` | Business Logic | Checks whether an employee is eligible for leave |
| `calculate_leave_days` | Calculation | Calculates the duration of a leave period |
| `validate_leave_request` | Validation | Checks requested leave against available balance |
| `submit_leave_request` | Action | Creates a leave request |
| `get_leave_requests` | Employee Data | Retrieves leave request history and status |

### Tool Design Principle

Each tool has a specific responsibility.

```text
LLM
 │
 │ decides which capability is required
 ▼
LangGraph
 │
 ▼
Application Tool
 │
 ├── validates input
 ├── applies business logic
 ├── enforces employee scope
 └── accesses required data
 │
 ▼
Tool Result
 │
 ▼
LLM
 │
 ▼
Final Response
```

This keeps business-critical operations outside the language model.

---

# End-to-End Leave Request Example

A typical leave interaction demonstrates multiple capabilities of the application.

### Step 1 — Employee asks a question

```text
Can I take 5 days of earned leave from October 10 to October 14?
```

### Step 2 — Agent determines required capabilities

The agent can determine that it needs information about:

- Leave duration
- Employee eligibility
- Available leave balance
- Relevant HR policy

### Step 3 — Tools execute

```text
calculate_leave_days()
        ↓
5 days

check_leave_eligibility()
        ↓
Eligible

get_leave_balance()
        ↓
Earned Leave: 12 days

search_hr_policy()
        ↓
Relevant earned-leave policy
```

### Step 4 — Agent synthesizes the results

The language model combines the tool results and policy context into a natural-language response.

### Step 5 — Employee explicitly requests submission

```text
Submit it.
```

The agent can then invoke:

```text
submit_leave_request()
```

### Step 6 — Database transaction

The request is stored in PostgreSQL:

```text
employee_id
leave_type
start_date
end_date
status
created_at
```

with the initial status:

```text
Pending
```

### Step 7 — Result returned to employee

```text
Leave request submitted successfully.

Request ID: 123
Status: Pending
```

This demonstrates the complete flow:

```text
Natural Language
      ↓
Agent Reasoning
      ↓
Tool Selection
      ↓
Data Retrieval
      ↓
Business Validation
      ↓
Action Execution
      ↓
Database Update
      ↓
Natural Language Response
```

---

# RAG Architecture

The policy knowledge layer is implemented using Retrieval-Augmented Generation.

## Ingestion

```text
HR Policy Document
       ↓
PDF Extraction
       ↓
Text Cleaning
       ↓
Chunking
       ↓
Gemini Embedding
       ↓
768-dimensional Vector
       ↓
Supabase PostgreSQL
       ↓
pgvector
```

## Retrieval

```text
Employee Question
       ↓
Query Embedding
       ↓
pgvector Similarity Search
       ↓
Top Relevant Policy Chunks
       ↓
Agent
       ↓
Grounded Response
```

The agent can therefore combine:

```text
Policy Knowledge
       +
Employee Data
       +
Business Logic
       +
Conversation Context
```

rather than relying solely on the LLM's pretrained knowledge.

---

# Authentication and Authorization Flow

Authentication is handled by the FastAPI backend.

```text
┌───────────────┐
│   Employee    │
└───────┬───────┘
        │
        │ Email + Password
        ▼
┌───────────────────┐
│   FastAPI Login   │
└─────────┬─────────┘
          │
          ▼
    Password Check
          │
          ▼
       JWT Token
          │
          ▼
┌───────────────────┐
│ Authenticated API │
└─────────┬─────────┘
          │
          ▼
    Employee ID
          │
          ▼
  LangGraph State
          │
          ▼
 Employee-scoped Tools
```

Employee-specific tools use the authenticated employee identity from application state.

For example:

```python
employee_id: Annotated[int, InjectedState("employee_id")]
```

The employee ID is therefore controlled by the application rather than supplied by the user or generated by the LLM.

---

# Reliability Approach

The application intentionally separates responsibilities between the LLM and deterministic application code.

### Language Model Responsibilities

The LLM is responsible for:

- Understanding natural-language requests
- Determining user intent
- Selecting appropriate tools
- Interpreting tool results
- Maintaining conversational context
- Generating the final response

### Application Responsibilities

The application is responsible for:

- Authentication
- Authorization
- Database access
- Employee identity
- Date calculations
- Leave validation
- Policy retrieval
- Leave request creation
- Data integrity

This separation reduces the risk of allowing the LLM to make critical business decisions directly.

```text
                LLM
                 │
        Reasoning / Selection
                 │
                 ▼
        ┌────────────────┐
        │ Application    │
        │ Tools          │
        └───────┬────────┘
                │
       Deterministic Logic
                │
                ▼
          Database / RAG
```

---

# Data Flow

A typical employee request follows this path:

```text
┌──────────────┐
│   Employee   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Web Client   │
└──────┬───────┘
       │ HTTPS
       ▼
┌──────────────┐
│   FastAPI    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ LangGraph    │
│    Agent     │
└──────┬───────┘
       │
       ├───────────────┐
       │               │
       ▼               ▼
   HR Tools        Policy RAG
       │               │
       ▼               ▼
 PostgreSQL       pgvector
       │               │
       └───────┬───────┘
               ▼
          Tool Results
               │
               ▼
          Gemini LLM
               │
               ▼
       Final HR Response
               │
               ▼
           Employee
```

---

# Application Boundaries

The application follows a clear separation of concerns:

| Component | Responsibility |
|---|---|
| Frontend | User interaction and presentation |
| FastAPI | API layer and authentication |
| LangGraph | Agent orchestration |
| Gemini | Language understanding and response generation |
| Tools | Business capabilities |
| PostgreSQL | Structured HR data |
| pgvector | Semantic policy retrieval |
| Supabase | Managed PostgreSQL platform |

This architecture allows individual components to evolve independently without coupling business logic to the language model.

---

# Example Questions

HR Copilot can handle questions across multiple categories.

### Employee Information

```text
What is my employee code?
What department am I in?
When did I join the company?
What is my registered email?
```

### Leave Balance

```text
How much earned leave do I have?
How much casual leave is remaining?
Show my current leave balance.
```

### HR Policy

```text
What is the earned leave policy?
How many days of earned leave can be carried forward?
What is the sick leave policy?
How much notice is required for earned leave?
```

### Leave Planning

```text
Can I take leave from October 10 to October 14?
How many days is this leave?
Do I have enough earned leave?
Am I eligible for leave?
```

### Leave Actions

```text
Submit this leave request.
Show my leave requests.
What is the status of my leave request?
```

---

# Production Considerations

The current application provides the core architecture required for an agentic HR assistant.

For a larger production deployment, the following capabilities can be added:

- Persistent conversation storage
- Role-based access control
- HR administrator workflows
- Manager approval workflows
- Policy versioning
- Document lifecycle management
- Audit trails
- Rate limiting
- Distributed caching
- Agent observability
- Human approval checkpoints
- Enterprise identity providers
- Notifications and integrations with existing HR systems

The current architecture is designed so these capabilities can be introduced without fundamentally changing the agent/tool model.
