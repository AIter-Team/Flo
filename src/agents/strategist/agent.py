from langchain.agents import create_agent

from src.tools.essential import get_current_time, get_task_instruction, check_available_instruction, handoff_to_agent
from src.tools.strategist import create_financial_goal, get_all_goals

from src.agents.state import State
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from src.utils import client

STRATEGIST = client.pull_prompt("flo/strategist-agent", include_model=True)

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


strategist_agent = create_agent(
    name="strategist_agent",
    model=STRATEGIST.last,
    tools=[
        # Essential tools
        get_current_time,
        get_task_instruction,
        check_available_instruction,
        handoff_to_agent,

        # Strategist tools
        create_financial_goal,
        get_all_goals
    ],
    state_schema=State,
    middleware=[personalized_prompt],
)


