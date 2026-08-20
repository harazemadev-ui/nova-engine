from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from ..engine.request import NovaRequest
from ..engine.engine import NovaEngine

app = FastAPI(
    title="Nova Engine API",
    description="API interface for the Nova Engine.",
    version="0.1.0",
)

engine = NovaEngine()


@app.post("/process")
def post_process_request(request: NovaRequest):
    response = engine.process(request)

    if response is None:
        return {"response": None}

    return response.to_dict()


@app.post("/process/stream")
def post_process_stream(request: NovaRequest):

    def generate():
        yield from engine.stream(request)

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
