from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

from langchain_core.messages import HumanMessage

from app.agent.state import HRAgentState
from app.agent.graph import hr_agent
from app.agent.memory import get_conversation, save_conversation
from app.auth.service import authenticate_employee
from app.auth.dependencies import get_current_user


app = FastAPI(
    title="HR Copilot",
    description="Enterprise HR Agent",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to frontend URL before production
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
    employee_id: int = Depends(get_current_user),
    current_user: dict = Depends(get_current_user),
):
    employee_id = current_user["employee_id"]
    role = current_user["role"]
    # Create a new conversation if one was not provided
    if not conversation_id:
        conversation_id = str(uuid4())

    # Retrieve existing conversation
    existing_state = get_conversation(conversation_id)

    if existing_state:
        state = existing_state

        state["employee_id"] = employee_id
        state["role"] = role

        state["messages"].append(
            HumanMessage(content=message)
        )

    else:
        state: HRAgentState = {
            "messages": [HumanMessage(content=message)],
            "employee_id": employee_id,
            "role": role,
            "intent": None,
            "tool_results": [],
            "final_response": None,
        }

    # Track the number of messages before this agent execution.
    # This allows us to identify tool results generated
    # specifically for the current request.
    previous_message_count = len(state["messages"])

    # Execute LangGraph agent
    result = hr_agent.invoke(state)

    # Only inspect messages generated during this request.
    # This prevents citations from previous conversation turns
    # from leaking into the current response.
    new_messages = result["messages"][previous_message_count:]

    # Save updated conversation state
    save_conversation(
        conversation_id,
        result,
    )

    # Final assistant response
    final_message = result["messages"][-1]

    # Extract citations generated during the current request
    citations = []
    seen_sources = set()

    for message in new_messages:

        # Only inspect tool messages
        if getattr(message, "type", None) != "tool":
            continue

        # Only policy search results can produce policy citations
        if getattr(message, "name", None) != "search_hr_policy":
            continue

        tool_result = message.content

        # ToolMessage content may be returned as a JSON string
        if isinstance(tool_result, str):
            try:
                import json

                tool_result = json.loads(tool_result)

            except json.JSONDecodeError:
                tool_result = []

        if not isinstance(tool_result, list):
            continue

        for item in tool_result:

            if not isinstance(item, dict):
                continue

            source = item.get("source")

            # Ignore missing sources and duplicate sources
            if not source or source in seen_sources:
                continue

            seen_sources.add(source)

            citations.append(
                {
                    "source": source
                }
            )

    return {
        "response": final_message.content,
        "employee_id": employee_id,
        "conversation_id": conversation_id,
        "citations": citations,
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