import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TrackerDatabase:
    """
    SQLite database to track source URLs, content hashes, and last updated timestamps.
    This prevents re-ingesting documents that haven't changed.
    """
    def __init__(self, db_path="data/tracker.db"):
        self.db_path = db_path
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sources (
                        url TEXT PRIMARY KEY,
                        content_hash TEXT,
                        last_updated TEXT,
                        status TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")

    def get_source(self, url: str) -> dict:
        """Retrieves tracking information for a source."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT content_hash, last_updated, status FROM sources WHERE url = ?', (url,))
                row = cursor.fetchone()
                if row:
                    return {
                        "url": url,
                        "content_hash": row[0],
                        "last_updated": row[1],
                        "status": row[2]
                    }
                return None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving source {url}: {e}")
            return None

    def update_source(self, url: str, content_hash: str, status: str):
        """Updates or inserts a source record."""
        now = datetime.now().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sources (url, content_hash, last_updated, status)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        content_hash=excluded.content_hash,
                        last_updated=excluded.last_updated,
                        status=excluded.status
                ''', (url, content_hash, now, status))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating source {url}: {e}")

    def get_all_sources(self) -> list:
        """Returns all tracked sources."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT url, content_hash, last_updated, status FROM sources')
                rows = cursor.fetchall()
                return [
                    {
                        "url": row[0],
                        "content_hash": row[1],
                        "last_updated": row[2],
                        "status": row[3]
                    } for row in rows
                ]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all sources: {e}")
            return []
