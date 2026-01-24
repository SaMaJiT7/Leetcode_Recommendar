from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
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
    vectorstore = PineconeVectorStore(
        embedding=embedding,
        index_name=index_name
    )

    prompt = PromptTemplate(
        input_variables=["question"],
        template="Generate the best query to find Leetcode Problems for a user based on their given weakness and current level: {question}"
    )

    multiquery_retriever = MultiQueryRetriever.from_llm(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        llm=llm,
        prompt=prompt
    )

    query = f"LeetCode problems suitable for {current_level} level programmers | based on more Topic like: {user_weakness} | Help improve this skill"
    
    results = multiquery_retriever.invoke(query)

    result_str = ""
    for idx, doc in enumerate(results):
        title = doc.metadata.get('title', 'Unknown Title')
        url = doc.metadata.get('url', '#')
        result_str += f"{idx+1}. {title} ({url})\n"
    
    return result_str if result_str else "No relevant problems found."

if __name__ == "__main__":
    # Example usage
    weakness = "Sliding Window"
    level = "Intermediate"
    result = get_datastore.invoke({
        "user_weakness": weakness,
        "current_level": level
    })

    print(result)