from langchain_core.tools import tool

from app.db.supabase import supabase
from app.rag.embeddings import generate_embedding


@tool
def search_hr_policy(query: str) -> list[dict]:
    """
    Search HR policy documents for information relevant to the employee's question.

    Use this tool when the employee asks about:
    - HR policies
    - leave rules
    - leave eligibility
    - leave approval
    - working hours
    - benefits
    - holidays
    - other HR policy-related information

    Returns relevant policy content together with source information
    that can be used to cite the policy in the final response.
    """

    query_embedding = generate_embedding(query)

    response = supabase.rpc(
        "match_policy_documents",
        {
            "query_embedding": query_embedding,
            "match_count": 5,
        },
    ).execute()

    results = response.data or []

    citations = []

    for result in results:
        metadata = result.get("metadata") or {}

        citations.append({
            "content": result.get("content"),
            "source": result.get("document_name"),
            "chunk_index": metadata.get("chunk_index"),
            "similarity": result.get("similarity"),
        })

    return citations