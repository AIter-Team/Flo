import asyncio
import json
import logging
import os
import uuid
from dotenv import load_dotenv
from langchain_core.messages import AIMessageChunk, HumanMessage

from src.agents import flo
from src.config.database import engine, initialize_db
from src.config.directory import DB_PATH, MEMORY_DIR

load_dotenv()
logger = logging.getLogger(__name__)


# Database Setup
def setup_database():
    """Check for the database and initialize if it not found"""
    if not os.path.exists(DB_PATH):
        logger.warning("Database not found. Initializing...")
        try:
            initialize_db(engine)
            logger.info(f"Database created successfully at: {DB_PATH}")
        except Exception as e:
            logger.critical(f"Error initializing database: {e}")
            raise
    else:
        logger.info("Database already exists. Skipping initialization.")


async def call_agent_async(message: str, profile: dict, thread_id: str):
    async for _, stream_mode, chunk in flo.astream(
        {"messages": [HumanMessage(content=message)], **profile},
        {"configurable": {"thread_id": thread_id}},
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
    thread_id = str(uuid.uuid4())

    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "r") as file:
        data = json.load(file)

    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Flo: See You Later!")
            break

        print("Flo: ", end="")
        await call_agent_async(user_input, data["profile"], thread_id)
        print("\n")


if __name__ == "__main__":
    setup_database()
    asyncio.run(main())
