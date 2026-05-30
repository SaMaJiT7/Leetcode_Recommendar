import requests
import json
from utilis import encode_str, decode_str
from wrapper import wrap_code

def execute_code(language: str, code: str, input_data: str, expected_output: str, prompt: str = "", entry_point: str = "", starter_code: str = ""):
    """Execute the given code using piston API and return the result.
    
    Args:
        language: Programming language
        code: User's solution code
        input_data: Test case input
        expected_output: Expected output
        prompt: (unused, kept for compatibility)
        entry_point: (unused, kept for compatibility)
        starter_code: Starter code template from MongoDB
    """
    
    # Wrap the user code with test harness
    wrapped_code = wrap_code(
        language=language,
        user_code=code,
        test_input=input_data,
        starter_code=starter_code
    )
    
    print(f"🔧 Code wrapped successfully")
    
    API_URL = "https://emkc.org/api/v2/piston/execute"

    runtimes = {
        "python": {"language": "python", "version": "3.10.0"},
        "java":   {"language": "java", "version": "15.0.2"},
        "cpp":    {"language": "c++", "version": "10.2.0"},
    }

    config = runtimes.get(language.lower(), runtimes["python"])

    payload = {
        "language": config["language"],
        "version": config["version"],
        "files": [{"name": "Main", "content": wrapped_code}],  # Use wrapped code
        "stdin": "",  # No stdin needed, input is in the code
        "args": [],
        "compile_timeout": 10000,
        "run_timeout": 3000,
        "compile_memory_limit": -1,
        "run_memory_limit": -1
    }

    # --- DEBUG LOG 1: OUTGOING ---
    print("\n" + "="*30)
    print(f"🚀 SENDING TO PISTON ({config['language']} {config['version']})")
    print(f"Code length: {len(wrapped_code)} chars")
    print("="*30 + "\n")

    try:
        response = requests.post(API_URL, json=payload)
        result = response.json()

        # --- DEBUG LOG 2: INCOMING ---
        print("\n" + "="*30)
        print(f"✅ RECEIVED FROM PISTON (Status: {response.status_code})")
        print(f"Response: {json.dumps(result, indent=2)}")
        print("="*30 + "\n")

        # Check for compilation errors
        compile_stage = result.get("compile", {})
        compile_error = compile_stage.get('stderr', '').strip()
        
        if compile_error:
            return {
                "status": "Compilation Error",
                "is_correct": False,
                "output": compile_stage.get('stdout', '').strip(),
                "expected": expected_output.strip() if expected_output else "",
                "error": compile_error
            }

        run_stage = result.get("run", {})
        std_output = run_stage.get('stdout', '').strip()
        std_error = run_stage.get('stderr', '').strip()



        # Verdict Logic 
        if std_error:
            return {
                "status": "Runtime Error",
                "is_correct": False,
                "output": std_output,
                "expected": expected_output.strip() if expected_output else "",
                "error": std_error
            }
        expected = expected_output.strip() if expected_output else ""
        if expected and std_output == expected:
            return {
                "status": "Accepted",
                "is_correct": True,
                "output": std_output,
                "expected": expected,
                "error": None
            }
        elif expected:
            return {
                "status": "Wrong Answer",
                "is_correct": False,
                "output": std_output,
                "expected": expected,
                "error": None
            }
        else:
            # No expected output provided, just return the output
            return {
                "status": "Accepted",
                "is_correct": True,
                "output": std_output,
                "expected": "",
                "error": None
            }
        
    except Exception as e:
        return {"status": "System Error", "error": str(e), "is_correct": False}


