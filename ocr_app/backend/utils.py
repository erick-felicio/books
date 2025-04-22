import os
import cv2
import pytesseract
import fitz              # PyMuPDF
from docx import Document
from ebooklib import epub
import subprocess

def process_images(workdir, image_paths):
    output_dir = os.path.join(workdir, "output")
    os.makedirs(output_dir, exist_ok=True)
    full_text = ""
    doc = Document()
    pdf = fitz.open()

    # Processamento de cada imagem
    for path in sorted(image_paths):
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        sharp = cv2.filter2D(th, -1, [[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

        tmp = path + "_tmp.png"
        cv2.imwrite(tmp, sharp)

        # OCR multilíngue
        text = pytesseract.image_to_string(tmp, lang='por+eng+spa')
        full_text += "\n\n" + text
        doc.add_paragraph(text)

        # Página PDF pesquisável
        img_bytes = open(tmp, 'rb').read()
        imgdoc = fitz.open("png", img_bytes)
        page = pdf.new_page(width=imgdoc[0].rect.width,
                            height=imgdoc[0].rect.height)
        page.insert_image(page.rect, stream=img_bytes)
        page.insert_textbox(page.rect, text, fontsize=8, overlay=True)

        os.remove(tmp)

    # Salvar PDF
    pdf.save(os.path.join(output_dir, "livro_OCR.pdf"))
    # Salvar TXT
    with open(os.path.join(output_dir, "livro_OCR.txt"), "w", encoding="utf-8") as f:
        f.write(full_text)
    # Salvar DOCX
    doc.save(os.path.join(output_dir, "livro_OCR.docx"))

    # Gerar EPUB
    book = epub.EpubBook()
    book.set_identifier("ocr")
    book.set_title("Livro OCR")
    book.add_author("Book.converter")
    chapter = epub.EpubHtml(title="OCR", file_name="ocr.xhtml", lang="pt")
    chapter.content = f"<pre>{full_text}</pre>"
    book.add_item(chapter)
    book.toc = (epub.Link("ocr.xhtml", "OCR", "o1"),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", chapter]
    epub.write_epub(os.path.join(output_dir, "livro_OCR.epub"), book)

    # Converter para MOBI (se calibre estiver instalado)
    mobi_out = os.path.join(output_dir, "livro_OCR.mobi")
    try:
        subprocess.run([
            "ebook-convert",
            os.path.join(output_dir, "livro_OCR.epub"),
            mobi_out
        ], check=True)
    except FileNotFoundError:
        # ebook-convert não encontrado; apenas ignora
        pass
