# chunker.py

def chunk_text(text, max_length=8000):
    # Découpage simple basé sur les caractères pour approcher les limites de tokens
    chunks = []
    current_chunk = ""
    for paragraph in text.split('\n'):
        if len(current_chunk) + len(paragraph) + 1 <= max_length:
            current_chunk += paragraph + '\n'
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph + '\n'
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

