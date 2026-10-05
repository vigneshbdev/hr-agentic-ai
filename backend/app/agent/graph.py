from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.agent.state import HRAgentState

from app.tools.leave import get_leave_balance
from app.tools.employee import get_employee_profile
from app.tools.policy import search_hr_policy
from app.tools.eligibility import check_leave_eligibility
from app.tools.calculation import calculate_leave_days
from app.tools.leave_validation import validate_leave_request
from app.tools.leave_request import submit_leave_request, get_leave_requests

from app.llm.client import llm


tools = [
    get_leave_balance,
    get_employee_profile,
    search_hr_policy,
    check_leave_eligibility,
    calculate_leave_days,
    validate_leave_request,
    get_leave_requests,
    submit_leave_request
]

llm_with_tools = llm.bind_tools(tools)


def agent_node(state: HRAgentState) -> HRAgentState:
    response = llm_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }


def route_after_agent(state: HRAgentState):
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


tool_node = ToolNode(tools)


def build_graph():
    graph = StateGraph(HRAgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")

    graph.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph.add_edge("tools", "agent")

    return graph.compile()


hr_agent = build_graph()