from langchain_chroma import Chroma
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages the ChromaDB instance."""
    
    def __init__(self, embeddings, persist_directory="vectorstore"):
        self.embeddings = embeddings
        self.persist_directory = persist_directory
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        
    def add_documents(self, documents):
        """Adds LangChain documents to ChromaDB."""
        if not documents:
            return
            
        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Successfully added {len(documents)} chunks to ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            raise
            
    def get_retriever(self, search_kwargs={"k": 4}):
        """Returns the retriever interface for the RAG chain."""
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)

    def delete_by_source_url(self, source_url: str):
        """
        Deletes all chunks associated with a specific source URL.
        Useful when a document is updated and we need to replace its old chunks.
        """
        try:
            # We must get all IDs that match the metadata source_url
            results = self.vector_store.get(where={"source_url": source_url})
            ids_to_delete = results.get("ids", [])
            
            if ids_to_delete:
                self.vector_store.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} old chunks for {source_url}.")
        except Exception as e:
            logger.error(f"Failed to delete old chunks for {source_url}: {e}")

    def get_stats(self):
        """Returns statistics about the vector store."""
        try:
            collection = self.vector_store._collection
            count = collection.count()
            return {"total_chunks": count}
        except Exception as e:
            logger.error(f"Failed to get vector store stats: {e}")
            return {"total_chunks": 0}
