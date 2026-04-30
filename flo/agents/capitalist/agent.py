from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt

from src.agents.state import Context, State
from src.config.agents import CAPITALIST
from src.tools.essential import (
    check_available_instructions,
    create_currency_converter,
    get_asset_market_price,
    get_current_time,
    get_task_instruction,
    handoff_to_agent,
    search_asset_symbol,
)
from src.tools.capitalist import *


@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context.user_name
    user_language = request.runtime.context.user_language
    user_currency = request.runtime.context.user_currency

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
        create_currency_converter(),
        get_asset_market_price,
        search_asset_symbol,
        # Networth tools
        calculate_networth,
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
    context_schema=Context,
    middleware=[personalized_prompt],
)
