# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 21:34:27 2025

@author: Desarrollador
"""

from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
import base64
from io import BytesIO
import uvicorn
import os

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las fuentes. Cambia esto por una lista específica de dominios en producción.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

class PDFResponse(BaseModel):
    pages: int
    text: str
    success: bool
    message: str

def get_pdf_text_and_page_count(pdf_bytes: bytes) -> PDFResponse:
    try:
        text = extract_text(BytesIO(pdf_bytes)).strip()
        if text:
            page_count = text.count('\x0c') or 1  # '\x0c' indica fin de página en PDF
            return PDFResponse(pages=page_count, text=text, success=True, message="Texto leído correctamente.")
        else:
            return PDFResponse(pages=0, text="", success=False, message="No se pudo extraer texto del PDF.")
    except PDFSyntaxError as e:
        return PDFResponse(pages=0, text="", success=False, message=f"Error de sintaxis en el PDF: {str(e)}")
    except Exception as e:
        return PDFResponse(pages=0, text="", success=False, message=f"Error al procesar el PDF: {str(e)}")

@app.post("/read-pdf", response_model=PDFResponse)
async def read_pdf(base64_pdf: str = Form(...)):
    try:
        pdf_bytes = base64.b64decode(base64_pdf)
        response = get_pdf_text_and_page_count(pdf_bytes)
        return response
    except Exception as e:
        return PDFResponse(pages=0, text="", success=False, message=f"Error decodificando el archivo: {str(e)}")

#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 8000))  # Usa el puerto de la variable de entorno o 8000 por defecto
#    uvicorn.run("apiReadPdf:app", host="0.0.0.0", port=port)
