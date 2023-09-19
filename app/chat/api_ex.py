import asyncio
from fastapi import Request, APIRouter
from sse_starlette import EventSourceResponse


chat = APIRouter()

COUNTER = 0
MESSAGE_STREAM_DELAY = 1
MESSAGE_STREAM_RETRY_TIMEOUT = 15000


def get_message() -> tuple[int, bool]:
    global COUNTER
    COUNTER += 1
    return COUNTER, COUNTER < 10


@chat.get("/stream")
async def message_stream(request: Request):
    async def event_generator():
        global COUNTER
        while True:
            if await request.is_disconnected():
                break

            counter, exists = get_message()
            if exists:
                yield {
                    "event": "new_message",
                    "id": COUNTER,
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": f"Counter value {counter}",
                }
            else:
                yield {
                    "event": "end_event",
                    "id": "message_id",
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": "End of the stream",
                }
            if COUNTER == 10:
                COUNTER = 0
            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(event_generator())
