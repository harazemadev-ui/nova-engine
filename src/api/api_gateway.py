from fastapi import FastAPI, HTTPException, Header

from ..engine.request import NovaRequest
from ..engine.engine import NovaEngine
from ..security.keys import NovaKey

nova_key = NovaKey()


app = FastAPI(
    title="Nova Engine API",
    description="API interface for the Nova Engine.",
    version="0.1.0",
)

engine = NovaEngine()


@app.post("/process")
def post_process_request(
    request: NovaRequest,
    x_nova_api_key: str = Header(None)
):

    if not nova_key.verify_api_key(
        x_nova_api_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid NOVA API Key"
        )

    response = engine.process(request)

    if response is None:
        return {
            "response": None
        }

    return response.to_dict()
