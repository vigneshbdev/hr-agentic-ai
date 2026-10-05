import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents="What is the company's annual leave policy?",
    config={
        "output_dimensionality": 768
    }
)

embedding = result.embeddings[0].values

print("Embedding dimensions:", len(embedding))
print("First 5 values:", embedding[:5])