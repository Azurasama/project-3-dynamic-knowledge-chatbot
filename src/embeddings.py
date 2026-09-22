from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    """
    Returns the HuggingFaceEmbeddings model for local embedding generation.
    Uses 'all-MiniLM-L6-v2' as it is small, fast, and good for basic RAG.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
