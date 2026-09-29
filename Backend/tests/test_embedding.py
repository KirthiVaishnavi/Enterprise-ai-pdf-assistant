from app.services.embedding_service import generate_embeddings

texts = [
    "The Constitution protects fundamental rights.",
    "Parliament makes laws."
]

embeddings = generate_embeddings(texts)

print("Number of vectors:", len(embeddings))
print("Dimension of vector 1:", len(embeddings[0]))
print("Dimension of vector 2:", len(embeddings[1]))