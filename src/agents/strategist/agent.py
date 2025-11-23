from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt

from src.agents.state import State
from src.config.agents import STRATEGIST
from src.tools.essential import (
    check_available_instructions,
    get_current_time,
    get_task_instruction,
    handoff_to_agent,
)
from src.tools.strategist import create_financial_goal, get_all_goals


@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    user_name = request.state.get("user_name", "User")
    user_language = request.state.get("user_language", "English")
    user_currency = request.state.get("user_currency", "USD")

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
    ],
    state_schema=State,
    middleware=[personalized_prompt],
)
