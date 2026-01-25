import base64

def encode_str(text: str) -> str:
    """Helper to base64 encode strings for Judge0"""
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def decode_str(text: str) -> str:
    """Helper to decode Judge0 responses"""
    if not text: return ""
    return base64.b64decode(text.encode('utf-8')).decode('utf-8')