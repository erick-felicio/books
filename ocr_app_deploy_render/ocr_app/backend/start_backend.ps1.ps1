# start_backend.ps1
$env:Path += ";C:\Program Files\Tesseract-OCR"  # Adiciona Tesseract ao PATH

# Ativa o ambiente virtual
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
.\.venv\Scripts\activate

# Instala dependências (só na primeira execução)
if (-not (Test-Path ".venv\Lib\site-packages\fastapi")) {
    pip install -r requirements.txt
}

# Inicia o servidor
uvicorn server:app --reload --host 0.0.0.0 --port 8000