from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

app = FastAPI(root_path="/api/render")

@app.post("/")
async def echo_pdf(
    file: UploadFile = File(...),
    scale: float = Form(2.0),
    start: int = Form(1),
    end: int | None = Form(None),
):
    data = await file.read()
    return JSONResponse({
        "received_filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(data),
        "scale": scale,
        "start": start,
        "end": end
    })
