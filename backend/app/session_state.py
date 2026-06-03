from dataclasses import dataclass, field
from typing import Optional

'''
in-memory session management, stores conversation state
'''
@dataclass
class ChatSessionState:
    active_product_name: Optional[str] = None
    active_area: Optional[str] = None
    active_filters: dict = field(default_factory=dict)
    price_mode: bool = False


SESSION_STORE: dict[str, ChatSessionState] = {}


def get_session_state(session_id: str) -> ChatSessionState:
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = ChatSessionState()

    return SESSION_STORE[session_id]


def update_session_state(
    session_id: str,
    product_name: str | None = None,
    area: str | None = None,
    filters: dict | None = None,
    price_mode: bool | None = None,
):
    state = get_session_state(session_id)

    if product_name:
        state.active_product_name = product_name

    if area is not None:
        state.active_area = area

    if filters is not None:
        state.active_filters = filters

    if price_mode is not None:
        state.price_mode = price_mode

    return state