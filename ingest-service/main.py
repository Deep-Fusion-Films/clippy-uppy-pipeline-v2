from fastapi import FastAPI
from router import router

app = FastAPI(title="Ingest Service", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router, prefix="/v1")

