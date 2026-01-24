from langchain_huggingface import HuggingFaceEmbeddings

# Singleton instance - loads only once
_embedding_model = None

def get_embedded_model():
    global _embedding_model
    if _embedding_model is None:
        print("⏳ Loading embedding model (one-time)...")
        _embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        print("✓ Embedding model loaded")
    return _embedding_model