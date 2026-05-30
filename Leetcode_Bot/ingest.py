from datasets import load_dataset
from langchain_pinecone import PineconeVectorStore
from text_splitter import split_text
from shared import get_embedded_model
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
import re
import json
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# Initialize Pinecone client
pc = Pinecone()
INDEX_NAME = "leetcoderec"

# Create index if it doesn't exist
existing_indexes = [index.name for index in pc.list_indexes()]
if INDEX_NAME not in existing_indexes:
    print(f"Creating new index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,  # Adjust based on your embedding model dimensions
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"  # Change to your preferred region
        )
    )
    print(f"✓ Index '{INDEX_NAME}' created")
else:
    print(f"✓ Index '{INDEX_NAME}' already exists")

print("Loading dataset...")
dataset = load_dataset("newfacade/LeetCodeDataset", split="all")


texts = []
metadatas = []

def generate_test_case(content: str):
    """Extracting the testcases from the problem description."""
    test_cases = []
    
    # Try multiple patterns to extract test cases
    # Pattern 1: "Example N: Input: ... Output: ..."
    pattern1 = r'Example\s+\d+:\s*\n*Input:\s*(.*?)\n+Output:\s*(.*?)(?=\n*(?:Example|Constraints|Explanation|$))'
    matches = re.findall(pattern1, content, re.DOTALL | re.IGNORECASE)
    
    # Pattern 2: "Input: ... \nOutput: ..." (without Example prefix)
    if not matches:
        pattern2 = r'Input:\s*(.*?)\n+Output:\s*(.*?)(?=\n*(?:Input:|Constraints|Explanation|$))'
        matches = re.findall(pattern2, content, re.DOTALL | re.IGNORECASE)

    for inp, output in matches:
        inp = inp.strip()
        output = output.strip()
        # Only add if both input and output are substantial (not single characters)
        if inp and output and len(inp) > 1 and len(output) > 1:
            test_cases.append({
                "input": inp,
                "expected": output
            })
    
    # Return empty list if no test cases found - that's OK
    # The frontend will handle missing test cases gracefully
    return test_cases


def generate_url(row):
    if "task_id" in row and row['task_id']:
        return f"https://leetcode.com/problems/{row['task_id']}/description/"
    
    return f"https://leetcode.com/problems/"


for row in dataset:
    row = dict(row)
    problem_url = generate_url(row)
    
    # Check for problem_description field (not content or title)
    if not row.get('problem_description'):
        continue

    # Extract tags/topics - check common field names
    tags = row.get('tags', [])
    
    # Convert to list of strings if it's list of dicts
    if tags and isinstance(tags[0], dict):
        tags = [tag.get('name', tag.get('slug', str(tag))) for tag in tags]
    
    tags_str = ", ".join(tags) if tags else ""
    
    # Debug: Print first problem's info
    if len(texts) == 0:
        print(f"\n{'='*50}")
        print(f"First problem task_id: {row.get('task_id')}")
        print(f"Available fields: {list(row.keys())}")
        print(f"Tags extracted: {tags}")
        print(f"Difficulty: {row.get('difficulty')}")
        print(f"{'='*50}\n")

    # Use problem_description as the content
    combined_text = f"Task ID: {row.get('task_id', 'Unknown')}\nProblem: {row['problem_description']}\nDifficulty: {row.get('difficulty') or 'Unknown'}\n"
    if tags_str:
        combined_text += f"Topics/Tags: {tags_str}\n"

    texts.append(combined_text)

    # Extract test cases from dataset (limit to 3 to avoid size issues)
    dataset_test_cases = row.get('input_output', []) or []
    test_cases = []
    for tc in dataset_test_cases[:3]:  # Only take first 3 test cases
        if isinstance(tc, dict) and 'input' in tc:
            test_cases.append({
                "input": str(tc.get('input', ''))[:200],  # Limit input size
                "expected": str(tc.get('output', tc.get('expected', '')))[:200]  # Limit output size
            })
    
    # Store limited test cases as compact JSON
    test_cases_json = json.dumps(test_cases) if test_cases else "[]"
    
    metadatas.append({
        "title": row['problem_description'][:100] + "...",  # Truncate for display
        "difficulty": row.get("difficulty") or 'Unknown',
        "url": problem_url,
        "tags": tags,  # Store tags as list of strings
        "task_id": row.get('task_id', ''),
        "test_cases": test_cases_json  # Store limited test cases
    })


def ingest_to_pinecone(texts: list[str], metadatas: list[dict]):
    """Store LeetCode problems in Pinecone vector store with chunking."""
    embedding = get_embedded_model()
    
    documents = []
    for idx, (text, meta) in enumerate(zip(texts, metadatas)):
        # Split long text into chunks
        chunks = split_text(text)
        
        # Debug: Check if splitting is working
        if idx == 0:
            print(f"First problem: {meta.get('title')}")
            print(f"Text length: {len(text)} chars")
            print(f"Chunks created: {len(chunks)}")
        
        # If no chunks created, use full text
        if not chunks:
            chunks = [text]
        
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

    # Delete all existing vectors from the index
    print(f"⚠️  Deleting all existing data from index '{INDEX_NAME}'...")
    try:
        index = pc.Index(INDEX_NAME)
        # Delete all vectors by deleting everything in all namespaces
        index.delete(delete_all=True)
        print(f"✓ All existing data deleted from '{INDEX_NAME}'")
    except Exception as e:
        print(f"❌ Error deleting data: {e}")
    
    # Now ingest fresh data
    vectorstore = ingest_to_pinecone(texts, metadatas)
    print("✓ Ingestion complete!")
    print()