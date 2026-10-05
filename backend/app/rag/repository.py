from app.db.supabase import supabase


def insert_policy_chunk(
    document_name: str,
    content: str,
    embedding: list[float],
    metadata: dict | None = None,
):
    response = (
        supabase
        .table("policy_documents")
        .insert({
            "document_name": document_name,
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {},
        })
        .execute()
    )

    return response.data