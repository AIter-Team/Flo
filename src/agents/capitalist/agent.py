from src.utils import client
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import dynamic_prompt, ModelRequest

from src.agents.state import State
from src.tools import handoff_to_agent, get_current_time, get_task_instruction, check_available_instruction
from src.tools.capitalist import *

CAPITALIST = client.pull_prompt("flo/capitalist-agent", include_model=True)

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


capitalist_agent = create_agent(
    name="capitalist_agent",
    model=CAPITALIST.last.bound,
    tools=[
        # Essential tools
        get_current_time,
        get_task_instruction,
        check_available_instruction,
        handoff_to_agent,

        # Capitalist tools
        insert_debt, 
        insert_installment, 
        insert_subscription, 
        get_user_liabilities
    ],
    state_schema=State,
    middleware=[personalized_prompt]
)