from app.agent.state import HRAgentState


_conversations: dict[str, HRAgentState] = {}


def get_conversation(conversation_id: str) -> HRAgentState | None:
    return _conversations.get(conversation_id)


def save_conversation(
    conversation_id: str,
    state: HRAgentState,
) -> None:
    _conversations[conversation_id] = state