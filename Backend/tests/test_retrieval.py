from app.database import SessionLocal
from app.models import DocumentChunk
from app.services.embedding_service import generate_embeddings


db = SessionLocal()

try:
    question = "What is the probation period for the Enforcement Officer/Accounts Officer post?"

    query_embedding = generate_embeddings([question])[0]
    distance=DocumentChunk.embedding.cosine_distance(query_embedding)
    results = (
        db.query(
            DocumentChunk,
            distance
        )
        .filter(DocumentChunk.document_id == 1)
        .order_by(distance).limit(5).all()
    )

    for chunk, distance in results:
        print(
            f"\n--- ID: {chunk.id} | "
            f"Page: {chunk.page_number} | "
            f"Chunk: {chunk.chunk_index} | "
            f"Distance: {distance} ---"
        )
        print(chunk.text)

finally:
    db.close()