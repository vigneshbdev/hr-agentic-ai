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


def search_policy(
    query_embedding: list[float],
    match_count: int = 5,
):
    """
    Search HR policy documents using vector similarity.
    """

    response = (
        supabase
        .rpc(
            "match_policy_documents",
            {
                "query_embedding": query_embedding,
                "match_count": match_count,
            },
        )
        .execute()
    )

    return response.data or []