#!/usr/bin/env python3
try:
    from langchain.retrievers.multi_query import MultiQueryRetriever
    print("✓ Found: langchain.retrievers.multi_query")
except ImportError:
    try:
        from langchain_community.retrievers.multi_query import MultiQueryRetriever
        print("✓ Found: langchain_community.retrievers.multi_query")
    except ImportError:
        print("✗ MultiQueryRetriever not found in standard locations")
        print("\nAlternative: Use basic vector store retriever instead")
