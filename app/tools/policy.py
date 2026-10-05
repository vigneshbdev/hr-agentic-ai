from langchain_core.tools import tool

from app.db.supabase import supabase
from app.rag.embeddings import generate_embedding

@tool
def search_hr_policy(query: str) -> list[dict]:
    """
    Search the HR policy documents for information relevant to the employee's question.

    Use this tool when the employee asks about company policies,
    leave rules, eligibility, approvals, working hours, benefits,
    holidays, or other HR policy-related information.
    """
    query_embedding = generate_embedding(query)

    response = supabase.rpc(
        "match_policy_documents",
        {
            "query_embedding": query_embedding,
            "match_count": 5,
        },
    ).execute()

    return response.data