import sys
import os
import requests
from datetime import datetime
from typing import List, Optional, Annotated

# --- 1. SETUP PATHS ---
# Add parent directory to path so we can import sibling modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 2. INTERNAL IMPORTS ---
from judge_service import execute_code
from Leetcode_Bot.Mentor import get_mentor_response # Ensure this function name matches your file
# Assuming get_datastore is not needed if we init manually below, 
# otherwise keep it.

# --- 3. HEAVY IMPORTS (MOVED TO GLOBAL SCOPE) ---
# We load these ONCE at startup to make the API fast.
from Leetcode_Bot.recomendation import embedding, index_name, llm
from langchain_pinecone import PineconeVectorStore
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import PromptTemplate
from Leetcode_Bot.generate_testcase import generate_testcase

app = FastAPI()

# --- 4. INITIALIZE VECTOR STORE (ONCE) ---
print("🔌 Connecting to Pinecone...")
vectorstore = PineconeVectorStore(
    embedding=embedding,
    index_name=index_name
)

retriever_prompt = PromptTemplate(
    input_variables=["question"],
    template="""Generate 3 diverse search queries to find LeetCode problems that specifically use the technique or pattern mentioned.
    
    Focus on:
    - Problems that explicitly require the mentioned technique (e.g., "sliding window", "two pointers")
    - The difficulty level specified
    - Include the technique name in the query
    
    Original question: {question}"""
)

# Create the retriever once - get more results for better filtering
multiquery_retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    llm=llm,
    prompt=retriever_prompt
)
print("✅ Vector Store Ready!")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        # Add your production domain here
        # "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class Submission(BaseModel):
    language: str
    code: str
    input_data: Optional[str] = ""
    expected_output: Optional[str] = ""
    test_cases: Optional[List[dict]] = None

class DailyChallengeRequest(BaseModel):
    user_weakness: Optional[str] = "General"
    current_level: Optional[str] = "Intermediate"

# --- ENDPOINTS ---

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {"status": "API is running"}

@app.post("/daily-challenge")
async def get_daily_challenge(request: DailyChallengeRequest):
    """Get a daily challenge problem based on user weakness and level"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Construct the query
        query = f"LeetCode problems suitable for {request.current_level} level programmers | based on more Topic like: {request.user_weakness} | Help improve this skill"
        
        # Use the pre-initialized retriever
        results = multiquery_retriever.invoke(query)
        
        if not results:
            raise HTTPException(status_code=404, detail="No problems found")
        
        # Get first result
        doc = results[0]
        metadata = doc.metadata
        content = doc.page_content
        
        # Check if test cases exist in metadata, otherwise we might need to parse them later
        test_cases = metadata.get('test_cases', [])

        #The fix if the testcases are not in metadata
        if not test_cases:
            generate_tc = generate_testcase(content)

            # Format them for your frontend
            test_cases = [
                {
                    "input": case['input_data'],
                    "expected": case['expected_output']
                }
                for case in generate_tc
            ]
        
        return {
            "title": metadata.get('title', 'Unknown Title'),
            "url": metadata.get('url', '#'),
            "difficulty": metadata.get('difficulty', request.current_level),
            "content": content,
            "date": today,
            "topic": request.user_weakness,
            "test_cases": test_cases
        }
    except Exception as e:
        print(f"Error: {str(e)}") # Log it to console for debugging
        raise HTTPException(status_code=500, detail=f"Error fetching daily challenge: {str(e)}")

@app.post("/submit")
async def submit_problem(submission: Submission):
    print(f"🚀 Running {submission.language} code...")

    # If test cases provided, run all of them
    if submission.test_cases and len(submission.test_cases) > 0:
        for i, case in enumerate(submission.test_cases):
            # 1. Execute Code for this test case
            result = execute_code(
                submission.language,
                submission.code,
                case.get('input', ""),
                case.get('expected', "")
            )
            
            # Logic to catch the first failure
            if not result.get('is_correct', False):
                final_verdict = result['status']
                
                # Stop at the first error and ask Mentor
                print("🤔 Code failed, asking AI Mentor...")
                hint = get_mentor_response(
                    verdict_type=result['status'],
                    language=submission.language,
                    error_log=result.get('error', ''),
                    user_code=submission.code,
                    expected=case.get('expected', ''),
                    actual=result.get('output', '')
                )
                
                return {
                    "verdict": final_verdict,
                    "failed_on_case": i + 1,
                    "input": case.get('input', ''),
                    "expected": case.get('expected', ''),
                    "your_output": result.get('output', ''),
                    "ai_hint": hint
                }
        
        # If loop finishes without returning, everything passed
        return {
            "verdict": "Accepted",
            "ai_hint": "Great job! Your solution passed all test cases. 🎉"
        }
    
    # If no test cases provided, just run and show output
    else:
        print("No test cases provided, running code without validation...")
        result = execute_code(
            submission.language,
            submission.code,
            submission.input_data or "",
            submission.expected_output or ""
        )
        
        response = {
            "verdict": result['status'],
            "output": result.get('output', ''),
            "is_correct": result.get('is_correct', False)
        }
        
        # Only call AI mentor if code failed
        if not result.get('is_correct', False):
            print("🤔 Code failed, asking AI Mentor...")
            response["ai_hint"] = get_mentor_response(
                verdict_type=result['status'],
                language=submission.language,
                error_log=result.get('error', ''),
                user_code=submission.code,
                expected=result.get('expected', ''),
                actual=result.get('output', '')
            )
        else:
            response["ai_hint"] = "Great job! Your solution executed successfully. 🎉"
        
        # Add expected output if available
        if 'expected' in result:
            response['expected'] = result['expected']
        
        return response