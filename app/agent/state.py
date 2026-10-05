from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class HRAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    employee_id: str | None
    intent: str | None
    tool_results: list
    final_response: str | None