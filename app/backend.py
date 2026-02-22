import sys
import os
import requests
import json
from datetime import datetime
from typing import List, Optional, Annotated

# --- 1. SETUP PATHS ---
# Add parent directory to path so we can import sibling modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient

# --- 2. INTERNAL IMPORTS ---
from judge_service import execute_code
from Leetcode_Bot.Mentor import get_mentor_response # Ensure this function name matches your file
# Assuming get_datastore is not needed if we init manually below, 
# otherwise keep it.

# --- 3. IMPORTS ---
from Leetcode_Bot.recomendation import get_datastore  # ✅ Only this
from Leetcode_Bot.generate_testcase import generate_testcase  # ✅ Keep this

app = FastAPI()

# --- 4. MONGODB CONNECTION ---
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["leetcode"]
problems_collection = mongo_db["problems"]



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
    task_id: str  # Added to fetch problem details from MongoDB
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
        
        print(f"🔍 Step 1: Querying Pinecone for recommendations...")
        # Use Pinecone to get recommended problem
        results = get_datastore.invoke({
            "user_weakness": request.user_weakness,
            "current_level": request.current_level
        })
        
        if not results or len(results) == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"No problems found for '{request.user_weakness}' at {request.current_level} level."
            )
        
        # Get task_id from Pinecone result
        doc = results[0]
        metadata = doc['metadata']
        task_id = metadata.get('task_id')
        
        if not task_id:
            raise HTTPException(status_code=500, detail="No task_id found in Pinecone metadata")
        
        print(f"✅ Pinecone recommended: {task_id}")
        print(f"🔍 Step 2: Fetching full problem from MongoDB...")
        
        # Fetch complete problem details from MongoDB
        problem = problems_collection.find_one({"_id": task_id})
        
        if not problem:
            raise HTTPException(
                status_code=404, 
                detail=f"Problem '{task_id}' not found in MongoDB. Run db.py to populate."
            )
        
        print(f"✅ MongoDB found: {problem.get('title', task_id)}")
        
        # Extract test cases (limited to first 3)
        test_cases = []
        for tc in (problem.get('test_cases', []) or [])[:3]:
            if isinstance(tc, dict):
                test_cases.append({
                    "input": str(tc.get('input', ''))[:200],
                    "expected": str(tc.get('output', ''))[:200]
                })
        
        return {
            "task_id": task_id,
            "title": problem.get('title', 'Unknown Title'),
            "url": f"https://leetcode.com/problems/{task_id}/",
            "difficulty": problem.get('difficulty', request.current_level),
            "content": problem.get('description', ''),
            "starter_code": problem.get('starter_code', {}),  # {python: "...", java: "...", cpp: "..."}
            "date": today,
            "topic": request.user_weakness,
            "test_cases": test_cases
        }
    except Exception as e:
        print(f"Error: {str(e)}") # Log it to console for debugging
        raise HTTPException(status_code=500, detail=f"Error fetching daily challenge: {str(e)}")

@app.post("/submit")
async def submit_problem(submission: Submission):
    print(f"🚀 Running {submission.language} code for problem: {submission.task_id}")
    
    # Fetch problem details from MongoDB
    problem = problems_collection.find_one({"_id": submission.task_id})
    
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{submission.task_id}' not found in MongoDB")
    
    # Get prompt (full code template) and entry_point (how to call function)
    prompt = problem.get('prompt', '')
    entry_point = problem.get('entry_point', '')
    
    print(f"📋 Entry point: {entry_point}")

    # If test cases provided, run all of them
    if submission.test_cases and len(submission.test_cases) > 0:
        results_list = []
        passed_count = 0
        
        for i, case in enumerate(submission.test_cases):
            # Execute Code with wrapping using prompt and entry_point
            result = execute_code(
                submission.language,
                submission.code,
                case.get('input', ""),
                case.get('expected', ""),
                prompt=prompt,
                entry_point=entry_point
            )
            
            # Track results
            is_correct = result.get('is_correct', False)
            if is_correct:
                passed_count += 1
            
            results_list.append({
                'case_number': i + 1,
                'status': result['status'],
                'is_correct': is_correct,
                'input': case.get('input', ''),
                'expected': case.get('expected', ''),
                'output': result.get('output', '')
            })
            
            # Stop at the first error and ask Mentor
            if not is_correct:
                final_verdict = result['status']
                
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
                    "passed_cases": passed_count,
                    "total_cases": len(submission.test_cases),
                    "failed_on_case": i + 1,
                    "input": case.get('input', ''),
                    "expected": case.get('expected', ''),
                    "your_output": result.get('output', ''),
                    "ai_hint": hint,
                    "all_results": results_list
                }
        
        # If loop finishes without returning, everything passed
        return {
            "verdict": "Accepted",
            "passed_cases": passed_count,
            "total_cases": len(submission.test_cases),
            "ai_hint": "Great job! Your solution passed all test cases. 🎉",
            "all_results": results_list
        }
    
    # If no test cases provided, just run and show output
    else:
        print("No test cases provided, running code without validation...")
        result = execute_code(
            submission.language,
            submission.code,
            submission.input_data or "",
            submission.expected_output or "",
            prompt=prompt, # type: ignore
            entry_point=entry_point # type: ignore
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