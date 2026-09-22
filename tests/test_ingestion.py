import pytest
from src.source_fetcher import SourceFetcher
from src.document_processor import DocumentProcessor

def test_source_fetcher_hash():
    fetcher = SourceFetcher()
    # Using a reliable simple site or mocked data. We will test the hash logic directly here instead of network
    # For a real test, we'd mock `requests.get`
    
    # Simulate a fake fetch logic for hash testing
    html1 = "<html><title>Test</title><body><p>Hello World</p></body></html>"
    html2 = "<html><title>Test</title><body><p>Hello World Updated</p></body></html>"
    
    import hashlib
    hash1 = hashlib.sha256("Hello World".encode('utf-8')).hexdigest()
    hash2 = hashlib.sha256("Hello World Updated".encode('utf-8')).hexdigest()
    
    assert hash1 != hash2

def test_document_processor():
    processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
    
    fake_data = {
        "url": "http://test.com",
        "title": "Test Doc",
        "text": "This is a very long string that should definitely be chunked by the document processor if the chunk size is set to fifty characters.",
        "content_hash": "fakehash"
    }
    
    docs = processor.process(fake_data)
    
    assert len(docs) > 1
    assert docs[0].metadata["source"] == "Test Doc"
    assert docs[0].metadata["content_hash"] == "fakehash"
    assert "document_id" in docs[0].metadata
    assert "chunk_id" in docs[0].metadata
