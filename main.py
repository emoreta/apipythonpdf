# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 21:34:27 2025

@author: Desarrollador
"""

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from io import BytesIO
import uvicorn
import os
from datetime import datetime

app = FastAPI()

# Definimos la estructura del modelo que se devolverá en la respuesta.
class PageEmbedding(BaseModel):
    page_number: int
    text: str

class PDFResponse(BaseModel):
    document_id: str
    pdf_filename: str
    upload_date: str
    author: str
    page_count: int
    pages: list[PageEmbedding]

# Función que extrae el texto y cuenta las páginas
def get_pdf_text_and_page_count(pdf_bytes: bytes, pdf_filename: str) -> PDFResponse:
    try:
        text = extract_text(BytesIO(pdf_bytes)).strip()
        if text:
            # Dividir el texto por páginas, que normalmente se marca con '\x0c' (fin de página en PDF)
            pages = text.split('\x0c')  # Cada página se separa por '\x0c'
            page_count = len(pages)
            pages_info = []

            # Por cada página, generamos el texto correspondiente
            for i, page_text in enumerate(pages):
                pages_info.append({
                    "page_number": i + 1,
                    "text": page_text.strip()
                })

            return PDFResponse(
                document_id="documento_12345",  # Aquí puedes generar un ID único si lo necesitas.
                pdf_filename=pdf_filename,
                upload_date=datetime.now().strftime('%Y-%m-%d'),
                author="Autor del PDF",  # Esta parte se puede personalizar si tienes esta información.
                page_count=page_count,
                pages=pages_info
            )
        else:
            return PDFResponse(
                document_id="documento_12345",
                pdf_filename=pdf_filename,
                upload_date=datetime.now().strftime('%Y-%m-%d'),
                author="Autor del PDF",
                page_count=0,
                pages=[]
            )
    except PDFSyntaxError as e:
        return PDFResponse(
            document_id="documento_12345",
            pdf_filename=pdf_filename,
            upload_date=datetime.now().strftime('%Y-%m-%d'),
            author="Autor del PDF",
            page_count=0,
            pages=[],
            message=f"Error de sintaxis en el PDF: {str(e)}"
        )
    except Exception as e:
        return PDFResponse(
            document_id="documento_12345",
            pdf_filename=pdf_filename,
            upload_date=datetime.now().strftime('%Y-%m-%d'),
            author="Autor del PDF",
            page_count=0,
            pages=[],
            message=f"Error al procesar el PDF: {str(e)}"
        )

# Endpoint para leer el PDF y devolver la respuesta
@app.post("/read-pdf", response_model=PDFResponse)
async def read_pdf(file: UploadFile = File(...)):
    try:
        # Leemos el archivo PDF directamente como bytes
        pdf_bytes = await file.read()
        response = get_pdf_text_and_page_count(pdf_bytes, file.filename)
        return response
    except Exception as e:
        return PDFResponse(
            document_id="documento_12345",
            pdf_filename="documento.pdf",
            upload_date=datetime.now().strftime('%Y-%m-%d'),
            author="Autor del PDF",
            page_count=0,
            pages=[],
            message=f"Error procesando el archivo: {str(e)}"
        )

#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 8000))  # Usa el puerto de la variable de entorno o 8000 por defecto
#    uvicorn.run("apiReadPdf:app", host="0.0.0.0", port=port)  # Asegúrate de que el nombre del archivo es correcto
