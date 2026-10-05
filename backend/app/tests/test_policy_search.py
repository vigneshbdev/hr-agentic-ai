from app.rag.embeddings import generate_embedding
from app.db.supabase import supabase


question = "How many casual leave days do employees get?"

query_embedding = generate_embedding(question)

result = supabase.rpc(
    "match_policy_documents",
    {
        "query_embedding": query_embedding,
        "match_count": 5,
    },
).execute()

for row in result.data:
    print(row)