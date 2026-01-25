from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.6)

error_prompt = PromptTemplate.from_template(
    """You are a helpful DSA mentor for LeetCode problems. You explain things clearly.
    
    CONTEXT:
    The user wrote this {language} code:
    {user_code}
    
    THE ERROR:
    It produced this error:
    {error_log}
    
    YOUR TASK:
    Explain the error clearly and give a hint to fix it.
    DO NOT give the full solution or corrected code.Try to keep it concise and simple."""
)

wrong_answer_prompt = PromptTemplate.from_template(
    """You are a helpful DSA mentor for LeetCode problems. You explain things clearly.
    
    CONTEXT:
    The user wrote this {language} code:
    {user_code}
    
    THE ISSUE:
    The code produced incorrect output.
    
    EXPECTED OUTPUT:
    {expected}
    
    ACTUAL OUTPUT:
    {actual}
    
    YOUR TASK:
    Explain why the output is incorrect and give a hint to fix it.
    DO NOT give the full solution or corrected code.Try to keep it concise and simple."""
)



def get_mentor_response(verdict_type: str, language: str,
error_log: str = "", user_code: str = "", expected: str = "", actual: str = ""):
    """Generate a mentor response based on the programming language and error log."""
    if verdict_type == "Runtime Error":
        prompt = error_prompt
        inputs = {"error_log": error_log, "user_code": user_code, "language": language}
    elif verdict_type == "Wrong Answer":
        prompt = wrong_answer_prompt
        inputs = {"expected": expected, "actual": actual, "user_code": user_code, "language": language}
    else:
        return "Keep going! You are doing great."
    
    mentor_chain = prompt | llm | StrOutputParser()
    try:
        print("🤖 AI Mentor is thinking...")
        hint = mentor_chain.invoke(inputs)
        return hint
    except Exception as e:
        return f"AI Mentor is taking a nap. (System Error: {str(e)})"
    

# --- QUICK TEST BLOCK ---
if __name__ == "__main__":
    print("Testing Runtime Error Hint...")
    print(get_mentor_response(
        verdict_type="Runtime Error",
        language="python",
        error_log="IndexError: list index out of range",
        user_code="my_list = [10, 20, 30]\nprint(my_list[10])"
    ))