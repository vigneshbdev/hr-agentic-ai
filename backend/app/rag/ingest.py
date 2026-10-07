from pathlib import Path

from app.rag.document_loader import extract_pdf_text
from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embedding
from app.rag.repository import insert_policy_chunk


def ingest_policy_pdf(
    file_path: str,
    policy_key: str | None = None,
    version: str | None = None,
    effective_date: str | None = None,
    status: str = "active",
) -> int:

    document_name = Path(file_path).name

    text = extract_pdf_text(file_path)

    chunks = chunk_text(text)

    inserted_count = 0

    for index, chunk in enumerate(chunks):

        embedding = generate_embedding(chunk)

        metadata = {
            "chunk_index": index,
            "source": "pdf",
        }

        if policy_key:
            metadata["policy_key"] = policy_key

        if version:
            metadata["version"] = version

        if effective_date:
            metadata["effective_date"] = effective_date

        metadata["status"] = status

        insert_policy_chunk(
            document_name=document_name,
            content=chunk,
            embedding=embedding,
            metadata=metadata,
        )

        inserted_count += 1

    return inserted_count