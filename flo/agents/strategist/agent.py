from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt

from src.agents.state import State, Context
from src.config.agents import STRATEGIST
from src.tools.capitalist import get_user_investments, get_user_liabilities
from src.tools.essential import (
    check_available_instructions,
    get_current_time,
    get_task_instruction,
    handoff_to_agent,
)
from src.tools.quant import check_balance, check_budget
from src.tools.strategist import *


@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context.user_name
    user_language = request.runtime.context.user_language
    user_currency = request.runtime.context.user_currency

    return (
        STRATEGIST.first.invoke(
            {
                "user_currency": user_currency,
                "user_language": user_language,
                "user_name": user_name,
            }
        )
        .messages[0]
        .content
    )


strategist = create_agent(
    name="strategist",
    model=STRATEGIST.last,
    tools=[
        # Essential tools
        get_current_time,
        get_task_instruction,
        check_available_instructions,
        handoff_to_agent,
        # Strategist tools
        create_financial_goal,
        get_all_goals,
        # Other tools
    ],
    state_schema=State,
    context_schema=Context,
    middleware=[personalized_prompt],
)
