from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

class TestCase(BaseModel):
    input_data: str = Field(description="The raw input string to be passed to stdin (e.g., '2 3' or '[1,2,3]').")
    expected_output: str= Field(description="The Expected output string (e.g., '5' or '6')")

class TestCaselist(BaseModel):
    test_cases: List[TestCase]

def generate_testcase(problem_description: str) -> List[dict]:
    """Generating the testcases from the problem description using LLM and returning as list of dicts."""

    parser = JsonOutputParser(pydantic_object=TestCaselist)
    prompt = PromptTemplate(
        template="""
        You are a QA Engineer. I will give you a coding problem description.
        Your job is to generate 2 SIMPLE test cases for this problem.
        
        RULES:
        1. The 'input_data' must be formatted exactly how a standard competitive programming judge reads from STDIN.
        2. The 'expected_output' must be the exact string printed to STDOUT.
        3. Do not include explanations. Just the data.
        
        PROBLEM:
        {problem}
        
        {format_instructions}
        """,
        input_variables=["problem"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    chain = prompt | llm | parser

    try:
        print("⚙️ Generating missing test cases via AI...")
        result = chain.invoke({"problem": problem_description})
        return result['test_cases']
    except Exception as e:
        print(f"⚠️ Test Case Generation Failed: {e}")
        # Fallback: Return a dummy case so the app doesn't crash
        return [{"input_data": "", "expected_output": ""}]