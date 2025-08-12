import base64, io
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

# 网关前缀固定为 /api/render
app = FastAPI(root_path="/api/render")

@app.post("/")
async def render_pdf(
    file: UploadFile = File(..., description="PDF file"),
    scale: float = Form(2.0),        # 1.5~2.0 常用；更高更清晰但更大
    start: int = Form(1),            # 起始页：1-based
    end: Optional[int] = Form(None), # 结束页（含）
    max_pages: int = Form(100)       # 保护阈值
):
    if (file.content_type or "").lower() not in ("application/pdf", "application/octet-stream"):
        return JSONResponse({"error": "Please upload a PDF file."}, status_code=400)

    # 读入 PDF 二进制
    pdf_bytes = await file.read()

    # 懒加载依赖（冷启动更稳）
    try:
        import pypdfium2 as pdfium
        from PIL import Image
    except Exception as e:
        return JSONResponse({"error": f"Render deps not available: {e}"}, status_code=500)

    # 打开文档（用内存流）
    try:
        doc = pdfium.PdfDocument(io.BytesIO(pdf_bytes))
    except Exception as e:
        return JSONResponse({"error": f"Failed to open PDF: {e}"}, status_code=400)

    n = len(doc)
    s = max(1, start)
    e = min(n, end if end is not None else n)
    if e < s:
        return JSONResponse({"error": "Invalid page range"}, status_code=400)
    if e - s + 1 > max_pages:
        return JSONResponse({"error": f"Too many pages requested (> {max_pages})."}, status_code=400)

    figures: List[dict] = []
    try:
        for i in range(s - 1, e):
            page = doc[i]
            # 渲染：scale 控制清晰度（1.0 基础倍率）
            bitmap = page.render(scale=scale, rotation=0)
            pil_img = bitmap.to_pil()  # -> Pillow Image
            # 转 PNG base64
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            figures.append({
                "id": f"fig_page_{i+1}",
                "filename": f"page_{i+1}.png",
                "width": pil_img.width,
                "height": pil_img.height,
                "bytes_base64": b64
            })
    except Exception as e:
        return JSONResponse({"error": f"Render failed: {e}"}, status_code=500)

    return {"page_count": n, "figures": figures}
