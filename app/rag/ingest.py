from pathlib import Path

from app.rag.document_loader import extract_pdf_text
from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embedding
from app.rag.repository import insert_policy_chunk


def ingest_policy_pdf(file_path: str) -> int:
    document_name = Path(file_path).name

    text = extract_pdf_text(file_path)

    chunks = chunk_text(text)

    inserted_count = 0

    for index, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)

        insert_policy_chunk(
            document_name=document_name,
            content=chunk,
            embedding=embedding,
            metadata={
                "chunk_index": index,
                "source": "pdf",
            },
        )

        inserted_count += 1

    return inserted_count