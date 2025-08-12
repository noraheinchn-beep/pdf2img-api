from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/")
def root():
    return PlainTextResponse("OK: /api/index is alive")

@app.get("/health")
def health():
    return {"ok": True}
