from app.rag.embeddings import generate_embedding
from app.rag.repository import insert_policy_chunk


policy_text = """
Employees are entitled to 12 days of casual leave per calendar year.
Casual leave can be taken for personal reasons and requires manager approval.
"""


embedding = generate_embedding(policy_text)

result = insert_policy_chunk(
    document_name="HR Leave Policy",
    content=policy_text,
    embedding=embedding,
    metadata={
        "policy_type": "leave",
        "section": "casual_leave",
    },
)

print("Inserted:", result)