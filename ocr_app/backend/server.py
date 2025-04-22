from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4
import os
import shutil
from pathlib import Path
from typing import List
import logging
from utils import process_images

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Diretórios base
TASKS_DIR = Path("tasks")
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf'}
OUTPUT_FORMATS = {'txt', 'pdf', 'epub', 'docx', 'mobi'}

@app.post("/process/")
async def process(
    background_tasks: BackgroundTasks, 
    files: List[UploadFile] = File(...)
):
    """Endpoint para processar arquivos de imagem via OCR"""
    try:
        # Validação de arquivos
        if not files:
            raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")

        task_id = str(uuid4())
        workdir = TASKS_DIR / task_id
        workdir.mkdir(parents=True, exist_ok=True)
        
        paths = []
        for file in files:
            # Verifica extensão do arquivo
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Formato {file_ext} não suportado"
                )

            path = workdir / file.filename
            try:
                with open(path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                paths.append(str(path))
            except Exception as e:
                logger.error(f"Erro ao salvar arquivo {file.filename}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Falha ao processar arquivo {file.filename}"
                )

        # Processamento em background
        output_dir = workdir / "output"
        output_dir.mkdir(exist_ok=True)
        
        background_tasks.add_task(
            process_images,
            str(workdir),
            paths,
            str(output_dir)
        )

        return {
            "task_id": task_id,
            "status": "processing",
            "output_formats": list(OUTPUT_FORMATS)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro inesperado no processamento")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")


@app.get("/download/{task_id}/{fmt}")
def download(task_id: str, fmt: str):
    """Endpoint para download dos arquivos processados"""
    try:
        # Validação do formato
        if fmt not in OUTPUT_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato {fmt} não suportado. Use: {', '.join(OUTPUT_FORMATS)}"
            )

        filepath = TASKS_DIR / task_id / "output" / f"output.{fmt}"
        
        if not filepath.exists():
            raise HTTPException(
                status_code=404,
                detail="Arquivo não encontrado ou processamento incompleto"
            )

        return FileResponse(
            filepath,
            filename=f"ocr_result.{fmt}",
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao recuperar arquivo {task_id}.{fmt}")
        raise HTTPException(status_code=500, detail="Erro ao recuperar arquivo")


@app.on_event("startup")
async def startup_event():
    """Garante que os diretórios necessários existam ao iniciar"""
    TASKS_DIR.mkdir(exist_ok=True)
    logger.info("Diretórios de tarefas verificados")