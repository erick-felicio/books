import logging
import shutil
from pathlib import Path
from typing import List
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from utils import process_images

logger = logging.getLogger(__name__)
app = FastAPI()
TASKS_DIR = Path("tasks")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
OUTPUT_FORMATS = {"txt", "pdf", "epub", "docx", "mobi"}
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_FILES = 50


def task_directory(task_id: str) -> Path:
    try:
        canonical = str(UUID(task_id))
        if canonical != task_id:
            raise ValueError("noncanonical UUID")
    except ValueError:
        raise HTTPException(status_code=400, detail="Identificador de tarefa inválido")
    return TASKS_DIR / canonical


def run_task(workdir: Path, paths: list[str]) -> None:
    try:
        process_images(str(workdir), paths)
        (workdir / "status.txt").write_text("completed", encoding="utf-8")
    except Exception:
        logger.exception("Falha no processamento OCR")
        (workdir / "status.txt").write_text("failed", encoding="utf-8")


@app.post("/process/")
async def process(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    if not files or len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Envie de 1 a {MAX_FILES} imagens")
    extensions = [Path(file.filename or "").suffix.lower() for file in files]
    if any(ext not in ALLOWED_EXTENSIONS for ext in extensions):
        raise HTTPException(status_code=400, detail="Use imagens PNG ou JPEG")
    task_id = str(uuid4())
    workdir = TASKS_DIR / task_id
    workdir.mkdir(parents=True)
    paths = []
    try:
        for index, (file, ext) in enumerate(zip(files, extensions)):
            path = workdir / f"{index:04d}{ext}"
            total = 0
            with path.open("wb") as dest:
                while chunk := await file.read(1024 * 1024):
                    total += len(chunk)
                    if total > MAX_FILE_BYTES:
                        raise HTTPException(status_code=413, detail="Imagem excede 20 MB")
                    dest.write(chunk)
            paths.append(str(path))
        (workdir / "status.txt").write_text("processing", encoding="utf-8")
        background_tasks.add_task(run_task, workdir, paths)
        return {"task_id": task_id, "status": "processing", "output_formats": sorted(OUTPUT_FORMATS)}
    except Exception:
        shutil.rmtree(workdir, ignore_errors=True)
        raise
    finally:
        for file in files:
            await file.close()


@app.get("/status/{task_id}")
def status(task_id: str):
    status_path = task_directory(task_id) / "status.txt"
    if not status_path.is_file():
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return {"task_id": task_id, "status": status_path.read_text(encoding="utf-8")}


@app.get("/download/{task_id}/{fmt}")
def download(task_id: str, fmt: str):
    if fmt not in OUTPUT_FORMATS:
        raise HTTPException(status_code=400, detail="Formato não suportado")
    filepath = task_directory(task_id) / "output" / f"livro_OCR.{fmt}"
    if not filepath.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado ou processamento incompleto")
    return FileResponse(filepath, filename=f"ocr_result.{fmt}", media_type="application/octet-stream")

