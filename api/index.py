import base64, io
from typing import List, Optional
import fitz  # PyMuPDF
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/render")
async def render_pdf(
    file: UploadFile = File(...),
    scale: float = Form(2.0),
    start: int = Form(1),
    end: Optional[int] = Form(None),
    max_pages: int = Form(100)
):
    if (file.content_type or "").lower() not in ("application/pdf", "application/octet-stream"):
        return JSONResponse({"error": "Please upload a PDF file."}, status_code=400)

    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    n = len(doc)
    s = max(1, start)
    e = min(n, end if end is not None else n)
    if e - s + 1 > max_pages:
        return JSONResponse({"error": f"Too many pages requested (> {max_pages})."}, status_code=400)

    mx = fitz.Matrix(scale, scale)
    figures: List[dict] = []
    for i in range(s - 1, e):
        page = doc[i]
        pix = page.get_pixmap(matrix=mx, alpha=False)
        b64 = base64.b64encode(pix.tobytes("png")).decode()
        figures.append({
            "id": f"fig_page_{i+1}",
            "filename": f"page_{i+1}.png",
            "width": pix.width,
            "height": pix.height,
            "bytes_base64": b64
        })
    return {"page_count": n, "figures": figures}
