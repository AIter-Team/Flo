from src.utils import client
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import dynamic_prompt, ModelRequest

from src.agents.state import State
from src.tools import insert_debt, insert_installment, insert_subscription, get_user_liabilities
from src.tools.handoffs import handoff_to_agent
from src.tools.utils import get_task_instruction, check_available_instruction

CAPITALIST = client.pull_prompt("flo/capitalist-agent", include_model=True)

tools = [handoff_to_agent, get_task_instruction, check_available_instruction, insert_debt, insert_installment, insert_subscription, get_user_liabilities]

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
    tools=tools,
    state_schema=State,
    middleware=[personalized_prompt]
)