# Books — experimento de OCR

Protótipo de conversão de imagens em texto e formatos de livro. O backend FastAPI está em `ocr_app/backend`; o frontend em `ocr_app/frontend` ainda é uma tela de demonstração e não envia arquivos. `ocr_app_deploy_render` e o ZIP são cópias antigas, não sincronizadas com as correções em `ocr_app`.

## Executar a API localmente

Instale Python, Tesseract com os idiomas português, inglês e espanhol, e as dependências listadas em `ocr_app/backend/requirements.txt`. Calibre é opcional para MOBI. No diretório `ocr_app/backend`:

```sh
python -m venv .venv
pip install -r requirements.txt
uvicorn server:app --host 127.0.0.1 --port 8000
```

Ative o ambiente virtual antes de instalar. A documentação interativa fica em `http://127.0.0.1:8000/docs`. Envie até 50 imagens PNG/JPEG de até 20 MB cada para `/process/`; consulte `/status/{task_id}` e baixe em `/download/{task_id}/{fmt}`. MOBI depende do Calibre. O processamento real requer Tesseract instalado; a qualidade do OCR e do PDF resultante precisa ser conferida.

As tarefas ficam no diretório local `tasks` e não são apagadas automaticamente. A API não tem autenticação ou isolamento entre usuários: use apenas localmente e não envie documentos sensíveis a uma instalação exposta à internet. A configuração Render existente é antiga e precisa ser revisada antes de qualquer implantação.

## Testes da API

Com FastAPI, python-multipart e httpx instalados, execute `python -m unittest discover -s tests` a partir de `ocr_app/backend`. Os testes simulam o motor de OCR e não substituem um teste real com Tesseract.

