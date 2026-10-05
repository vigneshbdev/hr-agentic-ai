from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.state import HRAgentState
from app.agent.graph import hr_agent
from app.auth.service import authenticate_employee
from app.auth.dependencies import get_current_employee

from langchain_core.messages import HumanMessage

from fastapi import HTTPException
from pydantic import BaseModel

from fastapi import Depends
from uuid import uuid4

from app.agent.memory import get_conversation, save_conversation

app = FastAPI(
    title="HR Copilot",
    description="Enterprise HR Agent",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We'll restrict this to your Vercel URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/agent")
def run_agent(
    message: str,
    conversation_id: str | None = None,
    employee_id: int = Depends(get_current_employee)
    ):
    if not conversation_id:
        conversation_id = str(uuid4())

    existing_state = get_conversation(conversation_id)

    if existing_state:
        state = existing_state
        state["messages"].append(
            HumanMessage(content=message)
        )
    else:
        state: HRAgentState = {
            "messages": [HumanMessage(content=message)],
            "employee_id": employee_id,
            "intent": None,
            "tool_results": [],
            "final_response": None,
        }

    result = hr_agent.invoke(state)

    save_conversation(conversation_id, result)

    final_message = result["messages"][-1]

    return {
        "response": final_message.content,
        "employee_id": employee_id,
        "conversation_id": conversation_id,
    }

class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
def login(request: LoginRequest):

    token = authenticate_employee(
        request.email,
        request.password,
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }