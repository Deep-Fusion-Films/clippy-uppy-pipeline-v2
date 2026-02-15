from fastapi import FastAPI, Request, HTTPException
from utils import decode_pubsub_request
from pipeline_batch import start_batch_pipeline
from pipeline_pro import start_pro_pipeline

app = FastAPI(title="Batch Orchestrator", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/pipeline/batch")
async def pipeline_batch(request: Request):
    try:
        payload = await request.json()
        unified_asset = decode_pubsub_request(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not unified_asset:
        return {"status": "ignored"}

    message_id = start_batch_pipeline(unified_asset)
    return {"status": "ok", "asset_id": unified_asset.get("asset_id"), "message_id": message_id}


@app.post("/v1/pipeline/pro")
async def pipeline_pro(request: Request):
    try:
        payload = await request.json()
        unified_asset = decode_pubsub_request(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not unified_asset:
        return {"status": "ignored"}

    message_id = start_pro_pipeline(unified_asset)
    return {"status": "ok", "asset_id": unified_asset.get("asset_id"), "message_id": message_id}

