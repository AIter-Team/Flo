from langchain.agents import create_agent
from flo.config.model import gemini


general_agent = create_agent(
    name="general_agent",
    model=gemini,
    system_prompt="You are a general agent of a financial assistant, your job is to answer any user question that doesn not related into financial terms. (e.g chit-chat)",
)
