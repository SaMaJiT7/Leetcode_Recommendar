import re
import json


def wrap_code(language: str, user_code: str, test_input: str, starter_code: str) -> str:
    """
    language     → "python", "java", "cpp"
    user_code    → user's Solution class
    test_input   → "nums = [2,7,11,15], target = 9"
    starter_code → "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:"
    """
    lang   = language.lower()
    params = parse_params_from_starter(starter_code, lang)
    fn     = parse_function_name(starter_code, lang)

    if lang == "python":
        return _wrap_python(user_code, fn, test_input, params)
    elif lang == "java":
        return _wrap_java(user_code, fn, test_input, params)
    elif lang == "cpp":
        return _wrap_cpp(user_code, fn, test_input, params)
    else:
        raise ValueError(f"Unsupported language: {language}")


# ── Starter code parsers ──────────────────────────────────────────────────────

def parse_function_name(starter_code: str, language: str) -> str:
    """Extract function name from starter code for any language."""
    if language == "python":
        match = re.search(r'def (\w+)\(', starter_code)
    elif language == "java":
        match = re.search(r'public\s+\w[\w<>\[\]]*\s+(\w+)\s*\(', starter_code)
    elif language == "cpp":
        match = re.search(r'\w[\w<>]*\s+(\w+)\s*\(', starter_code)
    else:
        match = None
    return match.group(1) if match else "solution"


def parse_params_from_starter(starter_code: str, language: str) -> list:
    """
    Extracts param names and types from starter code.
    Returns: [{"name": "nums", "type": "List[int]"}, {"name": "target", "type": "int"}]
    """
    if language == "python":
        match = re.search(r'def \w+\(self,?\s*(.*?)\)\s*->', starter_code)
        if not match:
            return []
        params_str = match.group(1).strip()
        params = []
        for p in params_str.split(','):
            p = p.strip()
            if not p:
                continue
            if ':' in p:
                name, typ = p.split(':', 1)
                params.append({"name": name.strip(), "type": typ.strip()})
            else:
                params.append({"name": p.strip(), "type": "any"})
        return params

    elif language == "java":
        match = re.search(r'public\s+\w[\w<>\[\]]*\s+\w+\s*\((.*?)\)', starter_code)
        if not match:
            return []
        params_str = match.group(1).strip()
        params = []
        for p in params_str.split(','):
            parts = p.strip().split()
            if len(parts) >= 2:
                params.append({"name": parts[-1], "type": " ".join(parts[:-1])})
        return params

    elif language == "cpp":
        match = re.search(r'\w[\w<>]*\s+\w+\s*\((.*?)\)', starter_code)
        if not match:
            return []
        params_str = match.group(1).strip()
        params = []
        for p in params_str.split(','):
            parts = p.strip().split()
            if len(parts) >= 2:
                params.append({"name": parts[-1], "type": " ".join(parts[:-1])})
        return params

    return []


# ── Python wrapper ────────────────────────────────────────────────────────────

def _wrap_python(user_code: str, fn: str, test_input: str, params: list) -> str:
    arg_names = ", ".join(p["name"] for p in params)

    return f"""\
from typing import List, Optional
import json

{user_code}

# ── Test Runner ──
{test_input}
sol = Solution()
result = sol.{fn}({arg_names})
print(json.dumps(result))
"""


# ── Java wrapper ──────────────────────────────────────────────────────────────

def _wrap_java(user_code: str, fn: str, test_input: str, params: list) -> str:
    parse_lines = _java_parse_input(test_input, params)
    arg_names   = ", ".join(p["name"] for p in params)
    indented    = "\n".join("    " + l for l in user_code.splitlines())

    return f"""\
import java.util.*;

public class Main {{

{indented}

    public static void main(String[] args) {{
{parse_lines}
        Solution sol = new Solution();
        System.out.println(sol.{fn}({arg_names}));
    }}
}}
"""


def _java_parse_input(test_input: str, params: list) -> str:
    """Generate Java variable declarations from test_input string."""
    lines = []
    for p in params:
        name = p["name"]
        typ  = p["type"].replace(" ", "")

        # Extract raw value for this param from test_input
        # e.g. "nums = [2,7,11,15], target = 9"  → nums → "[2,7,11,15]"
        pattern = rf'{name}\s*=\s*(.+?)(?:,\s*\w+\s*=|$)'
        match   = re.search(pattern, test_input)
        value   = match.group(1).strip() if match else "null"

        if typ in ("int", "long", "double", "boolean"):
            lines.append(f"        {typ} {name} = {value};")
        elif typ == "String":
            lines.append(f'        String {name} = {value};')
        elif typ in ("int[]", "int[][]"):
            java_val = value.replace("[", "{").replace("]", "}")
            lines.append(f"        {typ} {name} = new {typ}{{{java_val}}};")
        elif typ == "List<Integer>":
            java_val = value.strip("[]")
            lines.append(f"        List<Integer> {name} = new ArrayList<>(Arrays.asList({java_val}));")
        else:
            lines.append(f"        // TODO: manually parse {name} ({typ}) = {value}")

    return "\n".join(lines)


# ── C++ wrapper ───────────────────────────────────────────────────────────────

def _wrap_cpp(user_code: str, fn: str, test_input: str, params: list) -> str:
    parse_lines = _cpp_parse_input(test_input, params)
    arg_names   = ", ".join(p["name"] for p in params)

    return f"""\
#include <bits/stdc++.h>
using namespace std;

{user_code}

int main() {{
{parse_lines}
    Solution sol;
    auto result = sol.{fn}({arg_names});
    cout << result << endl;
    return 0;
}}
"""


def _cpp_parse_input(test_input: str, params: list) -> str:
    """Generate C++ variable declarations from test_input string."""
    lines = []
    for p in params:
        name = p["name"]
        typ  = p["type"].replace(" ", "")

        pattern = rf'{name}\s*=\s*(.+?)(?:,\s*\w+\s*=|$)'
        match   = re.search(pattern, test_input)
        value   = match.group(1).strip() if match else ""

        if typ == "int":
            lines.append(f"    int {name} = {value};")
        elif typ == "long" or typ == "longlong":
            lines.append(f"    long long {name} = {value};")
        elif typ == "string":
            lines.append(f"    string {name} = {value};")
        elif typ == "vector<int>":
            vals = value.strip("[]")
            lines.append(f"    vector<int> {name} = {{{vals}}};")
        elif typ == "vector<vector<int>>":
            lines.append(f"    // TODO: parse 2D array {name} = {value}")
        else:
            lines.append(f"    // TODO: parse {name} ({typ}) = {value}")

    return "\n".join(lines)
