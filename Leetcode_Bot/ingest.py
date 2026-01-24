from datasets import load_dataset
from langchain_pinecone import PineconeVectorStore
from text_splitter import split_text
from shared import get_embedded_model
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()

print("Loading dataset...")
dataset = load_dataset("greengerong/leetcode", split="all")


texts = []
metadatas = []

def generate_url(row):
    if "slug" in row and row['slug']:
        return f"https://leetcode.com/problems/{row['slug']}/description/"
    elif "title" in row:
        slug = row['title'].lower().replace(" ", "-").replace("'", "")
        return f"https://leetcode.com/problems/{slug}/description/"
    
    return f"https://leetcode.com/problems/"


for row in dataset:
    row = dict(row)
    problem_url = generate_url(row)
    if not row['content'] or not row['title']:
        continue

    combined_text = (
        f"Title: {row['title']}\n"
        f"Content: {row['content']}\n"
        f"Difficulty: {row.get('difficulty') or 'Unknown'}\n"
    )

    texts.append(combined_text)

    metadatas.append({
        "title": row['title'],
        "difficulty": row.get("difficulty") or 'Unknown',
        "url": problem_url,
        "sol_python": row.get('python') or 'Not Available',
        "sol_java": row.get('java') or 'Not Available',
        "sol_cpp": row.get('c++') or 'Not Available'
    })


def ingest_to_pinecone(texts: list[str], metadatas: list[dict]):
    """Store LeetCode problems in Pinecone vector store with chunking."""
    embedding = get_embedded_model()
    
    documents = []
    for text, meta in zip(texts, metadatas):
        # Split long text into chunks
        chunks = split_text(text)
        
        # Each chunk gets the same metadata (so we can trace back to the problem)
        for i, chunk in enumerate(chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={**meta, "chunk_index": i, "total_chunks": len(chunks)}
                )
            )
    
    print(f"Split {len(texts)} problems into {len(documents)} chunks")
    
    vectorstore = PineconeVectorStore.from_documents(
        documents,
        embedding=embedding,
        index_name="leetcoderec"
    )
    return vectorstore


if __name__ == "__main__":
    print(f"Ingesting {len(texts)} LeetCode problems...")
    vectorstore = ingest_to_pinecone(texts, metadatas)
    print("✓ Ingestion complete!")
    print()