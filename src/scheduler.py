from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime
from .ingestion import IngestionPipeline

logger = logging.getLogger(__name__)

class UpdateScheduler:
    """Manages periodic updates of the knowledge base."""
    
    def __init__(self, interval_hours=1):
        self.scheduler = BackgroundScheduler()
        self.pipeline = IngestionPipeline()
        self.interval_hours = interval_hours
        
    def start(self):
        """Starts the background scheduler."""
        if not self.scheduler.running:
            self.scheduler.add_job(
                func=self.run_update_job,
                trigger=IntervalTrigger(hours=self.interval_hours),
                id='kb_update_job',
                name='Update Knowledge Base',
                replace_existing=True
            )
            self.scheduler.start()
            logger.info(f"Scheduler started. Next run in {self.interval_hours} hours.")
            
    def stop(self):
        """Stops the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped.")
            
    def run_update_job(self):
        """Wrapper to run the ingestion pipeline."""
        logger.info(f"Running scheduled update job at {datetime.now()}")
        try:
            self.pipeline.run_update()
        except Exception as e:
            logger.error(f"Scheduled update failed: {e}")
            
    def get_next_run_time(self):
        """Returns the next scheduled run time."""
        if self.scheduler.running:
            job = self.scheduler.get_job('kb_update_job')
            if job:
                return job.next_run_time
        return None
