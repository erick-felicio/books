# Guia Simplificado de Instalação e Uso

## 1. Pré-requisitos

### Backend
1. Instale o Python 3.9+ (https://www.python.org/downloads/)  
2. Instale o Tesseract OCR e adicione ao PATH (https://github.com/tesseract-ocr/tesseract)  
3. (Opcional) Instale o Calibre para gerar .mobi (https://calibre-ebook.com/download)

### Frontend
1. Instale Node.js e npm (https://nodejs.org/)

## 2. Backend (API REST)

1. Abra o terminal/prompt e navegue até `ocr_app/backend`.  
2. Crie e ative um ambiente virtual:
   - Windows: `python -m venv .venv`  
     `.venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv`  
     `source .venv/bin/activate`
3. Instale dependências:
   ```
   pip install -r requirements.txt
   ```
4. Rode o servidor:
   ```
   uvicorn server:app --reload
   ```
5. Acesse `http://127.0.0.1:8000/docs` para testar uploads.

## 3. Frontend (PWA)

1. Abra outro terminal e navegue até `ocr_app/frontend`.  
2. Instale dependências:
   ```
   npm install
   ```
3. Inicie em modo de desenvolvimento:
   ```
   npm start
   ```
4. Abra no navegador `http://localhost:3000`.  
5. Para build de produção:
   ```
   npm run build
   ```
   Hospede a pasta `build` num serviço estático (Netlify, Vercel).

## 4. Uso Geral

1. No frontend, selecione as imagens das páginas.  
2. Clique em “Processar”.  
3. Espere a tarefa finalizar e baixe o PDF (ou outros formatos) pelo link.  
4. Para usar como app:
   - **Windows/Chrome**: clique em “Instalar” no navegador.  
   - **iPhone/Safari**: “Compartilhar” → “Adicionar à Tela de Início”.  
   - **Android/Chrome**: toque em “Instalar App”.

Qualquer dúvida, retorne a este guia!
