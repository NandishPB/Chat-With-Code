import os 
from typing import List
from sentence_transformers import SentenceTransformer
# from dotenv import load_dotenv
from parser.code_parser import SimpleCppParser, CodeChunk
import chromadb
import torch

device = 'cuda' if torch.cuda.is_available() else "cpu"
print(f"Using Device: {device}")

model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

def chunk_to_text(chunk: CodeChunk) -> str:

    parts = [
        f"Function: {chunk.function_name}",
        f"Lines: {chunk.line_start}-{chunk.line_end}",
        f"comments: {chunk.comments}",
        f"code:\n{chunk.function_body}",
    ]
    return "\n".join(parts)
    
if __name__ == "__main__":
    print("Starting embedding pipeline")

    parser = SimpleCppParser()
    print("parser created")

    chunks = parser.parse_directory("data/lprint")
    print(f" Parsed {len(chunks)} chunks")

    if not chunks:
        print(" No chunks found. Is your data/lprint folder empty")
        exit()
    
    client = chromadb.PersistentClient(path="vector_db")
    collection = client.get_or_create_collection(name="code_chunks")
    print("ChromaDB connected")

    texts = [chunk_to_text(chunk) for chunk in chunks]
    print("Generating batched Embeddings...")
 
    try:
        vectors = model.encode(texts, batch_size = 16, show_progress_bar = True)
    except Exception as e:
        print(f"Failed during embeddings {e}")
        exit()

    print("Storing embeddings to ChromeDB...")

    for i,(chunk, text, vector) in enumerate(zip(chunks, texts, vectors)):
        if not vector:
            print(f"SKipped {chunk.function_name} due to empty embedding")
            continue

        collection.add(
            embeddings = [vector],
            documents = [text],
            ids = [f"{chunk.file_path}-{chunk.function_name}-{i}"],
            metadata = [{
                "file_path" : chunk.file_path,
                "function" : chunk.function_name,
                "start_line" : chunk.line_start,
                "end_line": chunk.line_end
            }]
        )
        print(f"Stored {chunk.function_name} with {len(vector)} dims to ChromaDB")

    print("Embedding and Storage complete!")