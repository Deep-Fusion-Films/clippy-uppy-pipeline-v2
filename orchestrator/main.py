from fastapi import FastAPI, Request, HTTPException
from pubsub_handlers import handle_pipeline_start

app = FastAPI(title="Orchestrator (Flash Pipeline)", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/pipeline/start")
async def pipeline_start(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        result = handle_pipeline_start(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

