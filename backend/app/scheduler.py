import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.sources.perplexity_source import pull_perplexity_signals
from app.sources.x_source import pull_x_signals

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def pull_all_sources():
    """Pull data from all sources"""
    try:
        logger.info("Starting scheduled data pull...")
        
        perplexity_count = pull_perplexity_signals()
        logger.info(f"Pulled {perplexity_count} events from Perplexity")
        
        x_count = pull_x_signals()
        logger.info(f"Pulled {x_count} events from X")
        
        total = perplexity_count + x_count
        logger.info(f"Total: {total} new events added to stream")
        
    except Exception as e:
        logger.error(f"Error during scheduled pull: {e}", exc_info=True)

def start_scheduler():
    """Start the background scheduler"""
    # Pull immediately on startup
    pull_all_sources()
    
    # Schedule pulls every 5 minutes
    scheduler.add_job(pull_all_sources, 'interval', minutes=5, id='pull_sources')
    scheduler.start()
    logger.info("Background scheduler started - pulling data every 5 minutes")

def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")
