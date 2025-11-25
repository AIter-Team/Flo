from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt

from src.agents.state import State
from src.config.agents import QUANT
from src.tools import (
    check_available_instructions,
    get_current_time,
    get_task_instruction,
    handoff_to_agent,
)
from src.tools.quant import *

load_dotenv()


@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    user_name = request.state.get("user_name", "User")
    user_language = request.state.get("user_language", "English")
    user_currency = request.state.get("user_currency", "USD")

    return (
        QUANT.first.invoke(
            {
                "user_currency": user_currency,
                "user_language": user_language,
                "user_name": user_name,
            }
        )
        .messages[0]
        .content
    )


quant = create_agent(
    name="quant",
    model=QUANT.last.bound,
    tools=[
        # Essential tools
        get_current_time,
        get_task_instruction,
        check_available_instructions,
        handoff_to_agent,

        # Quant tools
        get_avg_income,
        write_transaction,
        update_balance,
        check_balance,
        check_budget,
        update_budget,
    ],
    state_schema=State,
    middleware=[personalized_prompt],
)
