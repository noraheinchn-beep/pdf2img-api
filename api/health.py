from fastapi import FastAPI

# 告诉 FastAPI：网关前缀是 /api/health
app = FastAPI(root_path="/api/health")

@app.get("/")
def health():
    return {"ok": True}
