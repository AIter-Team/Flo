from langchain.tools import tool


# C.I.A Agent
@tool("c.i.a", description="C.I.A or Can I Afford Agent is Agent for measuring how")
def call_cia(query: str):
    pass


@tool(
    "event-planner",
    description="Agent that specialized in planning financial based for specific events",
)
def call_event_planner(query: str):
    pass

@tool(
    "sql-agent",
    description="Agent for READ-ONLY SQL queries",
)
def call_sql_agent(query: str):
    pass