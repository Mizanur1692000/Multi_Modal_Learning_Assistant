# app/main.py
import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from dotenv import load_dotenv
import shutil
from pathlib import Path

load_dotenv()

from .ingest import STORE
from .stt_tts import transcribe_audio_file, text_to_speech
from .gemini_client import generate_answer
from .utils import make_sample_chart

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR.parent / "templates"))

# serve static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR.parent / "app/static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # accept pdf or txt
    suffix = Path(file.filename).suffix.lower()
    save_to = Path("uploads")
    save_to.mkdir(exist_ok=True)
    dest = save_to / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    if suffix in [".pdf"]:
        STORE.ingest_pdf(str(dest))
    else:
        STORE.ingest_txt(str(dest))
    return {"status":"ok", "filename": str(dest)}

@app.post("/stt")
async def stt_endpoint(file: UploadFile = File(...)):
    tmp = Path("tmp")
    tmp.mkdir(exist_ok=True)
    dest = tmp / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    text = transcribe_audio_file(str(dest))
    return {"text": text}

@app.post("/ask")
async def ask(question: str = Form(...), want_audio: bool = Form(False), want_chart: bool = Form(False)):
    # retrieve top contexts
    contexts = STORE.retrieve(question, k=4)
    context_text = "\n\n".join(contexts) if contexts else ""
    prompt = f"Answer the user's question concisely. If numeric data or guidance can be shown as a small chart, say 'INCLUDE_CHART' followed by CSV-like numbers. User Q: {question}\n\nContext:\n{context_text}"
    answer = generate_answer(prompt=prompt, context_text=context_text)
    response = {"answer": answer}
    # simple rule: if answer contains 'INCLUDE_CHART' then produce a sample chart
    if "INCLUDE_CHART" in answer or want_chart:
        # here demo: parse numbers if returned or use dummy numbers
        sample_numbers = [1,2,3,4,3,2,5]
        chart_path = make_sample_chart(sample_numbers)
        response["chart"] = chart_path
    if want_audio:
        mp3_path = text_to_speech(answer)
        response["audio"] = mp3_path
    return JSONResponse(response) 