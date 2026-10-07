from app.rag.ingest import ingest_policy_pdf


count = ingest_policy_pdf("app/assets/wfh_docs/WFH_Policy.pdf")

print(f"Successfully inserted {count} policy chunks")