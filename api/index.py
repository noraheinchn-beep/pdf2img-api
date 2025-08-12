from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, JSONResponse

# 关键：告诉 FastAPI，网关前缀是 /api/index
app = FastAPI(root_path="/api/index")

@app.get("/")
def root():
    return PlainTextResponse("OK: /api/index is alive")

@app.get("/health")
def health():
    return JSONResponse({"ok": True})
