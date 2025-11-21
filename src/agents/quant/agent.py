from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langchain_openai import ChatOpenAI

from src.agents.state import State
from src.tools.handoffs import handoff_to_agent
from src.tools import *
from src.utils import client

load_dotenv()

QUANT = client.pull_prompt("flo/quant-agent", include_model=True)


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


quant_agent = create_agent(
    name="quant_agent",
    model=QUANT.last.bound,
    tools=[
        get_current_time,
        get_task_instruction,
        write_transaction,
        handoff_to_agent,
        update_balance,
        check_balance,
        check_budget,
        update_budget
    ],
    state_schema=State,
    middleware=[personalized_prompt],
)
