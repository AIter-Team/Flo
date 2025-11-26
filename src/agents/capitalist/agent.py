from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt

from src.agents.state import State
from src.config.agents import CAPITALIST
from src.tools import (
    check_available_instructions,
    get_current_time,
    get_task_instruction,
    handoff_to_agent,
)
from src.tools.capitalist import *


@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    user_name = request.state.get("user_name", "User")
    user_language = request.state.get("user_language", "English")
    user_currency = request.state.get("user_currency", "USD")

    return (
        CAPITALIST.first.invoke(
            {
                "user_currency": user_currency,
                "user_language": user_language,
                "user_name": user_name,
            }
        )
        .messages[0]
        .content
    )


capitalist = create_agent(
    name="capitalist",
    model=CAPITALIST.last.bound,
    tools=[
        # Essential tools
        get_current_time,
        get_task_instruction,
        check_available_instructions,
        handoff_to_agent,

        # Liabilities tools
        insert_debt,
        insert_installment,
        insert_subscription,
        get_user_liabilities,

        # Investments tools
        insert_asset,
        insert_fixed_deposit,
        get_user_investments,
        update_asset,
        update_fixed_deposit,
    ],
    state_schema=State,
    middleware=[personalized_prompt],
)
