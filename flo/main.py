from typing import AsyncIterable
from fastapi import FastAPI, Request, Form
from fastapi.sse import EventSourceResponse, ServerSentEvent
from langchain.messages import HumanMessage, AIMessageChunk
from dotenv import load_dotenv


from flo.agents import flo

load_dotenv()

app = FastAPI()


async def event_generator(
    request: Request,
    active_agent: str,
    message: str,
) -> AsyncIterable[ServerSentEvent]:

    try:
        async for node, stream_mode, chunk in flo.astream(
            {
                "messages": [{"role": "user", "content": message}],
                "active_agent": active_agent,
            },
            stream_mode=["messages", "custom"],
            subgraphs=True,
        ):
            if await request.is_disconnected():
                break

            if stream_mode == "custom":
                yield ServerSentEvent(event="status", data={"message": chunk})

            elif stream_mode == "messages":
                msg = chunk[0]

                if len(node) > 1:
                    continue

                if (
                    isinstance(msg, AIMessageChunk)
                    and msg.content
                    and not msg.tool_calls
                ):
                    yield ServerSentEvent(event="token", raw_data=msg.content)

    except Exception as e:
        yield ServerSentEvent(event="error", data={"error": str(e)})

    finally:
        yield ServerSentEvent(event="end", raw_data="Streaming Finished.")


@app.post("/flo/chat", response_class=EventSourceResponse)
async def stream_response(
    request: Request,
    message: str = Form(...),
    active_agent: str | None = Form(None),
) -> AsyncIterable[ServerSentEvent]:

    async for event in event_generator(
        request,
        active_agent,
        message,
    ):
        yield event


async def main():
    while True:
        msg = input("User: ")
        if msg in ["q"]:
            print("Flo: See you later!")
            return

        print("Flo: ", end="")
        async for chunk in flo.astream(
            {"messages": [HumanMessage(content=msg)]},
            {"configurable": {"thread_id": "1"}},
            stream_mode=["messages", "custom"],
            subgraphs=True,
            version="v2",
        ):
            if chunk["type"] == "messages":
                token, metadata = chunk["data"]
                print(token.content, end="", flush=True)

        print("\n")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    # import asyncio
    # asyncio.run(main())
