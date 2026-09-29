from fastapi import UploadFile, HTTPException, status
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Document, DocumentChunk
import uuid

UPLOAD_DIR=Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE=20*1024*1024

def validate_file(file:UploadFile)->bytes:
    if file.content_type!="application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
        
    file.file.seek(0,2)
    file_size=file.file.tell()
    file.file.seek(0)
        
    if file_size>MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must not exceed 20MB"
        )
    
    file_bytes=file.file.read()
    file.file.seek(0)
    return file_bytes
    
def save_file(file_bytes:bytes, file_path:Path):
    with file_path.open("wb") as buffer:
            buffer.write(file_bytes)
    
def generate_file_path()->Path:
    unique_id=uuid.uuid4()
    stored_filename=f"{unique_id}.pdf"
    return UPLOAD_DIR/stored_filename 

def create_document(db: Session, user_id: int, filename: str, file_path: str):
    document=Document(
            user_id=user_id,
            filename=filename,
            file_path=str(file_path)
        )
        
    db.add(document)
    db.flush()
    
    return document
def create_chunks(db: Session, document_id: int, chunks: list):
    document_chunks = []

    for chunk in chunks:
        document_chunk = DocumentChunk(
            document_id=document_id,
            page_number=chunk["page_number"],
            chunk_index=chunk["chunk_index"],
            text=chunk["text"],
            embedding=chunk["embedding"]
        )

        db.add(document_chunk)
        document_chunks.append(document_chunk)

    db.flush()
    return document_chunks