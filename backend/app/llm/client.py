import os

from dotenv import load_dotenv
from langchain_litellm import ChatLiteLLM

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash",
)

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")

llm = ChatLiteLLM(
    model=f"gemini/{GEMINI_MODEL}",
    api_key=GEMINI_API_KEY,
    temperature=0,
)