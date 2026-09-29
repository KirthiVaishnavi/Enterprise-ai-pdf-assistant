from sqlalchemy.orm import Session
from app.models import DocumentChunk

def retrieve_chunks(
    document_id: int,
    db: Session,
    query_embedding: list,
    top_k:int= 5
):
    chunks=db.query(DocumentChunk).filter(
        DocumentChunk.document_id==document_id
    ).order_by(
        DocumentChunk.embedding.cosine_distance(query_embedding)
        ).limit(top_k).all()
    
    return chunks