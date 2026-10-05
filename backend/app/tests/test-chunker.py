from app.rag.document_loader import extract_pdf_text
from app.rag.chunker import chunk_text


pdf_path = "app/assets/policy_docs/sample_hr_leave_policy.pdf"

text = extract_pdf_text(pdf_path)

chunks = chunk_text(text)

print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print(chunk)