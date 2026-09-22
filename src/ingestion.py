import json
import logging
import os
from .database import TrackerDatabase
from .source_fetcher import SourceFetcher
from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .embeddings import get_embeddings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IngestionPipeline:
    """Orchestrates the dynamic updating of the knowledge base."""
    
    def __init__(self, config_path="config/sources.json"):
        self.config_path = config_path
        self.db = TrackerDatabase()
        self.fetcher = SourceFetcher()
        self.processor = DocumentProcessor()
        self.embeddings = get_embeddings()
        self.vector_store = VectorStore(self.embeddings)
        
    def _load_sources(self):
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file {self.config_path} not found.")
                return []
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("sources", [])
        except Exception as e:
            logger.error(f"Failed to load sources from config: {e}")
            return []

    def run_update(self):
        """
        Runs the ingestion pipeline:
        1. Load sources
        2. Fetch each
        3. Check hash against tracker DB
        4. If changed/new: chunk, embed, store, update tracker
        """
        logger.info("Starting knowledge base update pipeline...")
        sources = self._load_sources()
        
        results = {
            "total_checked": len(sources),
            "new": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "total_chunks_added": 0
        }
        
        for source in sources:
            url = source.get("url")
            if not url:
                continue
                
            logger.info(f"Checking source: {url}")
            
            # Fetch content
            fetched_data = self.fetcher.fetch_url(url)
            if not fetched_data:
                logger.error(f"Failed to fetch {url}")
                self.db.update_source(url, "", "Failed")
                results["failed"] += 1
                continue
                
            new_hash = fetched_data["content_hash"]
            
            # Check DB
            tracked_source = self.db.get_source(url)
            
            if tracked_source:
                if tracked_source["content_hash"] == new_hash:
                    logger.info(f"No changes detected for {url}. Skipping.")
                    self.db.update_source(url, new_hash, "No Changes")
                    results["skipped"] += 1
                    continue
                else:
                    logger.info(f"Content changed for {url}. Updating.")
                    # Delete old chunks to avoid duplicates of outdated info
                    self.vector_store.delete_by_source_url(url)
                    action = "updated"
            else:
                logger.info(f"New source detected: {url}.")
                action = "new"
                
            # Process and Store
            documents = self.processor.process(fetched_data)
            if documents:
                self.vector_store.add_documents(documents)
                results["total_chunks_added"] += len(documents)
                results[action] += 1
                self.db.update_source(url, new_hash, "Updated" if action == "updated" else "New")
            else:
                logger.warning(f"No text extracted from {url}")
                self.db.update_source(url, new_hash, "Failed (No Text)")
                results["failed"] += 1
                
        logger.info("Knowledge base update pipeline completed.")
        logger.info(f"Results: {results}")
        return results
