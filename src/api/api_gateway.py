from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse

from ..engine.request import NovaRequest
from ..engine.engine import NovaEngine
from ..security.nova_api_key import NovaKey
from ..errors.nova_error import NovaError

nova_key = NovaKey()


app = FastAPI(
    title="Nova Engine API",
    description="API interface for the Nova Engine.",
    version="0.1.0",
)

engine = NovaEngine()


@app.exception_handler(NovaError)
async def nova_error_handler(
    request: Request,
    error: NovaError
):
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": error.to_dict()
        }
    )


@app.post("/process")
def post_process_request(
    request: NovaRequest,
    x_nova_api_key: str = Header(None)
):
    if not nova_key.verify(x_nova_api_key):
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


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "nova-engine"
    }
