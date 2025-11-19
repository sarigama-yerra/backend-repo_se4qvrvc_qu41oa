import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


# -----------------------------
# PDF Export: HTML + CSS source
# -----------------------------
HTML_CODE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Senior Software Engineer — Portfolio</title>
  <meta name=\"description\" content=\"Senior Software Engineer portfolio — projects, experience, and contact.\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap\" rel=\"stylesheet\">
  <link rel=\"stylesheet\" href=\"styles.css\" />
</head>
<body>
  <a class=\"skip-link\" href=\"#main\">Skip to content</a>
  <header class=\"site-header\">
    <div class=\"container\">
      <a class=\"brand\" href=\"#\"> <span class=\"brand-badge\" aria-hidden=\"true\">•</span> <span class=\"brand-text\">Your Name</span> </a>
      <input type=\"checkbox\" id=\"nav-toggle\" class=\"nav-toggle\" aria-hidden=\"true\" />
      <label for=\"nav-toggle\" class=\"nav-toggle-label\" aria-label=\"Toggle menu\" role=\"button\" tabindex=\"0\">
        <svg class=\"icon\" viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M3 6h18M3 12h18M3 18h18\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\"/></svg>
        <svg class=\"icon close\" viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M6 6l12 12M6 18L18 6\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\"/></svg>
      </label>
      <nav class=\"nav\">
        <a href=\"#work\">Work</a>
        <a href=\"#about\">About</a>
        <a href=\"#contact\">Contact</a>
        <a class=\"btn btn-outline small\" href=\"resume.pdf\" target=\"_blank\" rel=\"noopener\">Resume</a>
        <div class=\"nav-socials\">
          <a class=\"icon-btn\" href=\"https://github.com/yourhandle\" target=\"_blank\" rel=\"noopener\" aria-label=\"GitHub\"></a>
          <a class=\"icon-btn\" href=\"https://www.linkedin.com/in/yourhandle\" target=\"_blank\" rel=\"noopener\" aria-label=\"LinkedIn\"></a>
        </div>
      </nav>
    </div>
  </header>
  <main id=\"main\">
    <section class=\"hero\"> ... </section>
    <section id=\"work\" class=\"section\"> ... </section>
    <section id=\"about\" class=\"section\"> ... </section>
    <section id=\"contact\" class=\"section\"> ... </section>
  </main>
  <footer class=\"site-footer\"> ... </footer>
  <script>document.getElementById('year') && (document.getElementById('year').textContent = new Date().getFullYear());</script>
</body>
</html>
"""

CSS_CODE = """:root{\n  --bg: #0a0b0f;\n  --panel: #0f1117;\n  --muted: #9aa4b2;\n  --text: #e6e9ef;\n  --accent: #ff6363;\n  --accent-2: #7c3aed;\n  --ring: #2b2f3a;\n  --card: #121420;\n  --card-2: #16192a;\n  --grad-1: #fa709a;\n  --grad-2: #fee140;\n  --grad-3: #7f53ac;\n  --grad-4: #647dee;\n  --shadow: 0 10px 30px rgba(0,0,0,.35), 0 2px 10px rgba(0,0,0,.25);\n}\n/* Full CSS omitted for brevity in PDF header; see full site source for details */\n"""

def _wrap_text(text: str, max_chars: int) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        if not raw_line:
            lines.append("")
            continue
        # Hard wrap without hyphenation
        while len(raw_line) > max_chars:
            lines.append(raw_line[:max_chars])
            raw_line = raw_line[max_chars:]
        lines.append(raw_line)
    return lines

@app.get("/export/htmlcss-pdf")
def export_html_css_pdf():
    """Return a PDF file containing the standalone HTML and CSS code."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except Exception as e:
        return Response(status_code=500, content=f"ReportLab not available: {e}")

    buffer = BytesIO()
    page_w, page_h = LETTER
    c = canvas.Canvas(buffer, pagesize=LETTER)

    # Use built-in Courier to keep things simple and monospace
    font_name = "Courier"
    font_size = 9
    line_height = font_size * 1.35
    left_margin = 0.75 * inch
    right_margin = 0.75 * inch
    top_margin = 0.75 * inch
    bottom_margin = 0.75 * inch

    max_width = page_w - left_margin - right_margin
    # ~90 chars per line approximation for Courier 9pt on US Letter with margins
    max_chars = 95

    def draw_block(title: str, code: str):
        nonlocal c
        # Title
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, page_h - top_margin, title)
        y = page_h - top_margin - (line_height * 1.4)
        c.setFont(font_name, font_size)
        for line in _wrap_text(code, max_chars):
            if y < bottom_margin:
                c.showPage()
                c.setFont("Helvetica-Bold", 12)
                c.drawString(left_margin, page_h - top_margin, title + " (cont.)")
                y = page_h - top_margin - (line_height * 1.4)
                c.setFont(font_name, font_size)
            c.drawString(left_margin, y, line)
            y -= line_height
        # Add some spacing after block
        if y < bottom_margin + line_height * 2:
            c.showPage()
        else:
            y -= line_height
        return y

    # Cover page
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin, page_h - top_margin, "Senior Portfolio — HTML & CSS Source")
    c.setFont("Helvetica", 10)
    c.drawString(left_margin, page_h - top_margin - 18, "Generated by FastAPI on-demand")
    c.showPage()

    draw_block("index.html", HTML_CODE)
    draw_block("styles.css", CSS_CODE)

    c.save()
    buffer.seek(0)

    headers = {
        "Content-Disposition": "attachment; filename=portfolio_html_css_source.pdf"
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
