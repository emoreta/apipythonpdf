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
from PyPDF2 import PdfFileReader
import io

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

# Función para extraer el autor del PDF
def extract_pdf_author(pdf_bytes: bytes) -> str:
    try:
        reader = PdfFileReader(io.BytesIO(pdf_bytes))
        metadata = reader.getDocumentInfo()
        author = metadata.author if metadata.author else "Desconocido"
        return author
    except Exception as e:
        return "Desconocido"  # Si no se puede extraer el autor, retornamos "Desconocido"

# Función que extrae el texto y cuenta las páginas
def get_pdf_text_and_page_count(pdf_bytes: bytes, pdf_filename: str) -> PDFResponse:
    try:
        # Extraemos el texto del PDF
        text = extract_text(BytesIO(pdf_bytes)).strip()
        
        # Extraemos el autor del PDF
        author = extract_pdf_author(pdf_bytes)
        
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

            # Generar un document_id aleatorio con fecha y hora
            document_id = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            return PDFResponse(
                document_id=document_id,
                pdf_filename=pdf_filename,
                upload_date=datetime.now().strftime('%Y-%m-%d'),
                author=author,
                page_count=page_count,
                pages=pages_info
            )
        else:
            document_id = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return PDFResponse(
                document_id=document_id,
                pdf_filename=pdf_filename,
                upload_date=datetime.now().strftime('%Y-%m-%d'),
                author=author,
                page_count=0,
                pages=[]
            )
    except PDFSyntaxError as e:
        document_id = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return PDFResponse(
            document_id=document_id,
            pdf_filename=pdf_filename,
            upload_date=datetime.now().strftime('%Y-%m-%d'),
            author="Desconocido",
            page_count=0,
            pages=[],
            message=f"Error de sintaxis en el PDF: {str(e)}"
        )
    except Exception as e:
        document_id = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return PDFResponse(
            document_id=document_id,
            pdf_filename=pdf_filename,
            upload_date=datetime.now().strftime('%Y-%m-%d'),
            author="Desconocido",
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
            author="Desconocido",
            page_count=0,
            pages=[],
            message=f"Error procesando el archivo: {str(e)}"
        )

#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 8000))  # Usa el puerto de la variable de entorno o 8000 por defecto
#    uvicorn.run("apiReadPdf:app", host="0.0.0.0", port=port)  # Asegúrate de que el nombre del archivo es correcto
