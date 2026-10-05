import re


def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[str]:

    text = re.sub(r"\n{3,}", "\n\n", text.strip())

    if not text:
        return []

    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:

        # Add paragraph to current chunk if it fits
        if len(current) + len(paragraph) + 2 <= chunk_size:
            current = f"{current}\n\n{paragraph}".strip()
            continue

        # Save current chunk
        if current:
            chunks.append(current)

        # Start new chunk
        current = paragraph

        # If a single paragraph is too large, split it safely
        while len(current) > chunk_size:
            split_at = current.rfind(" ", 0, chunk_size)

            if split_at == -1:
                split_at = chunk_size

            chunks.append(current[:split_at].strip())
            current = current[split_at:].strip()

    if current:
        chunks.append(current)

    return chunks