from langchain.agents import create_agent
from flo.config.model import gemini


quant_agent = create_agent(
    name="quant_agent",
    model=gemini,
    system_prompt="You are the Quant Agent, you can help user with accounting.",
)
