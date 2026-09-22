import requests
from bs4 import BeautifulSoup
import logging
import hashlib

logger = logging.getLogger(__name__)

class SourceFetcher:
    """Fetches content from URLs and extracts plain text."""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        
    def fetch_url(self, url: str) -> dict:
        """
        Fetches the URL, extracts text, computes hash, and returns a dictionary.
        Returns None if fetching fails.
        """
        try:
            headers = {
                "User-Agent": "DynamicKnowledgeBaseBot/1.0"
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else url
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()
                
            text = soup.get_text(separator=' ', strip=True)
            
            # Compute hash
            content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            
            return {
                "url": url,
                "title": title,
                "text": text,
                "content_hash": content_hash
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None
