from fastapi import APIRouter,File, UploadFile, Depends, HTTPException, status
from app.auth import get_current_user
from app.models import User, Document
from app.database import get_db
from app.services.pdf_service import extract_pages
from app.services.document_service import validate_file, save_file, generate_file_path, create_document, create_chunks
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import generate_embeddings

from sqlalchemy.orm import Session
from pathlib import Path

router=APIRouter()

@router.post("/upload")
def upload_documents(
   file:UploadFile=File(...),
   current_user:User=Depends(get_current_user),
   db: Session=Depends(get_db) 
):
            
    file_bytes=validate_file(file)
    
    pages=extract_pages(file_bytes)
    
    chunks=chunk_pages(pages)
    
    texts=[chunk["text"] for chunk in chunks]
    
    embeddings=generate_embeddings(texts)
    
    if len(embeddings) != len(chunks):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding count does not match chunk count"
        )
    
    for chunk, embedding in zip(chunks,embeddings):
        chunk["embedding"]=embedding
    
    file_path=generate_file_path()
    
    save_file(file_bytes, file_path)
    
    try:
        document=create_document(db, current_user.id, Path(file.filename).name, file_path)
        document_chunks=create_chunks(db, document.id, chunks)
        db.commit()
    
    except Exception:
        db.rollback()
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= "Unable to save document"
        )
    
    return{
        "id": document.id,
        "filename":document.filename,
        "user_id":document.user_id,
        "created_at":document.created_at
    }
    
@router.get("")
def get_documents(
    current_user:User=Depends(get_current_user),
    db: Session=Depends(get_db)
):
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [
        {
            "id": document.id,
            "filename": document.filename,
            "user_id": document.user_id,
            "created_at": document.created_at
        }
        for document in documents
    ]