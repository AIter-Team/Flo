from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt

from src.agents.state import State
from src.config.agents import STEWARD
from src.tools import (
    check_available_instructions,
    get_current_time,
    get_task_instruction,
    handoff_to_agent,
)

from src.tools.quant import read_transactions, check_balance, check_budget
from src.tools.capitalist import get_user_liabilities

@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    user_name = request.state.get("user_name", "User")
    user_language = request.state.get("user_language", "English")
    user_currency = request.state.get("user_currency", "USD")

    return (
        STEWARD.first.invoke(
            {
                "user_currency": user_currency,
                "user_language": user_language,
                "user_name": user_name,
            }
        )
        .messages[0]
        .content
    )

steward = create_agent(
    name="steward",
    model=STEWARD.last,
    tools=[
        # Essential tools
        get_current_time,
        get_task_instruction,
        check_available_instructions,
        handoff_to_agent,

        # Steward tools


        # Other tools
        check_balance,
        check_budget,
        get_user_liabilities,
        read_transactions,
    ],
    state_schema=State,
    middleware=[personalized_prompt],
)
