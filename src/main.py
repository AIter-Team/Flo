import asyncio

from dotenv import load_dotenv
from langchain_core.messages import AIMessageChunk, HumanMessage

from src.agents import root_agent

load_dotenv()


async def call_agent_async(message: str):
    async for graph, stream_mode, chunk in root_agent.astream(
        {
            "messages": [HumanMessage(content=message)],
            "user_name": "Revito",
        },
        {"configurable": {"thread_id": "1"}},
        stream_mode=["messages", "custom"],
        subgraphs=True,
    ):
        if stream_mode == "custom":
            print(chunk)
        else:
            msg = chunk[0]
            if isinstance(msg, AIMessageChunk) and msg.content and not msg.tool_calls:
                print(msg.content, end="", flush=True)


async def main():
    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Flo: See You Later!")
            break

        print("Flo: ", end="")
        await call_agent_async(user_input)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
