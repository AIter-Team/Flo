from dataclasses import dataclass, field

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated


@dataclass
class State:
    messages: Annotated[list[AnyMessage], add_messages]
    user_name: str = field(default="User")
    user_language: str = field(default="English")
    user_currency: str = field(default="USD")
    user_balance: int = field(default=0)
    active_agent: str = field(default="root")
