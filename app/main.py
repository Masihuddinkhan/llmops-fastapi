import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="LLM Dataset Explorer",
    version="1.0",
    description="Upload dataset, view structure, and query via local LLM"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")

os.makedirs(static_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include dataset routes
from app.routes import dataset
app.include_router(dataset.router, prefix="/api/dataset", tags=["Dataset"])
print("[INFO] Dataset routes loaded successfully.")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
