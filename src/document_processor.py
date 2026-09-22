from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import uuid
from datetime import datetime

class DocumentProcessor:
    """Chunks text and prepares LangChain Documents with metadata."""
    
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
    def process(self, fetched_data: dict) -> list[Document]:
        """
        Takes raw fetched data, splits it, and attaches metadata.
        Returns a list of LangChain Document objects.
        """
        if not fetched_data or "text" not in fetched_data:
            return []
            
        text = fetched_data["text"]
        url = fetched_data["url"]
        title = fetched_data["title"]
        content_hash = fetched_data["content_hash"]
        
        chunks = self.text_splitter.split_text(text)
        documents = []
        
        ingestion_timestamp = datetime.now().isoformat()
        document_id = str(uuid.uuid4())
        
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": title,
                "source_url": url,
                "document_id": document_id,
                "chunk_id": f"{document_id}_{i}",
                "content_hash": content_hash,
                "ingestion_timestamp": ingestion_timestamp
            }
            doc = Document(page_content=chunk, metadata=metadata)
            documents.append(doc)
            
        return documents
