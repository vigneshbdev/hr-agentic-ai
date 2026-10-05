from app.rag.ingest import ingest_policy_pdf


count = ingest_policy_pdf("app/assets/policy_docs/sample_hr_leave_policy.pdf")

print(f"Successfully inserted {count} policy chunks")