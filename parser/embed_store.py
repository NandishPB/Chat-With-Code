import os 
from typing import List
from sentence_transformers import SentenceTransformer
# from dotenv import load_dotenv
from parser.code_parser import SimpleCppParser, CodeChunk

model = SentenceTransformer("BAAI/bge-large-en-v1.5")

def chunk_to_text(chunk: CodeChunk) -> str:

    parts = [
        f"Function: {chunk.function_name}",
        f"Lines: {chunk.line_start}-{chunk.line_end}",
        f"comments: {chunk.comments}",
        f"code:\n{chunk.function_body}",
    ]
    return "\n".join(parts)

def generate_embedding(text: str) -> List[float]:

    try:
        return model.encode(text).tolist()
    except Exception as e:
        print(f"failed to embed:  {e}")
        return []
    
if __name__ == "__main__":
    parser = SimpleCppParser()
    chunks = parser.parse_directory("data/lprint")
    
    for chunk in chunks[:3]:
        text = chunk_to_text(chunk)
        vector = generate_embedding(text)
        print(f"\n {chunk.function_name}-> {len(vector)} dimension")