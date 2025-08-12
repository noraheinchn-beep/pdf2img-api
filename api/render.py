import base64
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

# 关键：告诉 FastAPI 这个函数的网关前缀
app = FastAPI(root_path="/api/render")

@app.post("/")
async def render_pdf(
    file: UploadFile = File(..., description="PDF file"),
    scale: float = Form(2.0),
    start: int = Form(1),
    end: Optional[int] = Form(None),
    max_pages: int = Form(100)
):
    # 懒加载 PyMuPDF，避免冷启动导入失败导致整个路由不可用
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        return JSONResponse({"error": f"PyMuPDF not available: {e}"}, status_code=500)

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
