from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
try:
    from .shared import get_embedded_model
except ImportError:
    from shared import get_embedded_model
from langchain_groq import ChatGroq
from pinecone import Pinecone
import os

load_dotenv()

pc = Pinecone()
embedding = get_embedded_model()
index_name = os.getenv("index_name")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.6)

@tool
def get_datastore(user_weakness: str, current_level: str):
    """Retrieve a Data from Pinecone vector store based on the weakness and current levels."""
    # 1. Map natural language level to LeetCode difficulty
    level_map = {
        "Beginner": "Easy",
        "Intermediate": "Medium", 
        "Advanced": "Hard"
    }
    difficulty = level_map.get(current_level, "Medium")
    
    
    vectorstore = PineconeVectorStore(
        embedding=embedding,
        index_name=index_name
    )
    
    # Create multiple filter options for better matching
    weakness_lower = user_weakness.lower().replace(" ", "-")
    weakness_variations = [
        user_weakness,  # "Sliding Window" ← This matches dataset format
        weakness_lower,  # "sliding-window"
        user_weakness.replace(" ", ""),  # "SlidingWindow"
        weakness_lower.replace("-", ""),  # "slidingwindow"
    ]
    
    try:
        # This guarantees the difficulty is correct, so the vector search only focuses on the Topic.
        base_retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 5, # Fetch more candidates since we might filter some out later
                "filter": {"difficulty": difficulty, "tags": {"$in": weakness_variations}}
                }
        )
    except Exception as e:
        print(f"⚠️ Filtering failed: {e}, using difficulty only")
        base_retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {"difficulty": difficulty}
                }
        )

    prompt = PromptTemplate(
        input_variables=["question"],
        template="""You are an expert coding interviewer. The user needs to practice '{question}'.
        Generate 3 search queries that describe the *content* of a coding problem for this topic.
        
        Examples of good queries:
        - "Given an array find the longest subarray with sum k" (if topic is Sliding Window)
        - "Find the maximum depth of a binary tree" (if topic is DFS)
        
        Do not generate generic queries like "best problems for X". Describe the problem logic."""
    )

    multiquery_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm,
        prompt=prompt
    )

    results = multiquery_retriever.invoke(user_weakness)

    result_str = ""
    # Use a set to avoid duplicates from multiple queries
    seen_urls = set()
    
    for idx , doc in enumerate(results):
        url = doc.metadata.get('url', '#')
        if url not in seen_urls:
            task_id = doc.metadata.get('task_id', 'Unknown Task ID')
            result_str += f"{idx+1}. {task_id} ({url})\n"
            seen_urls.add(url)
    
    return result_str if result_str else "No relevant problems found."

if __name__ == "__main__":
    # Example usage
    weakness = "Binary Search Tree"
    level = "Intermediate"
    result = get_datastore.invoke({
        "user_weakness": weakness,
        "current_level": level
    })

    print(result)