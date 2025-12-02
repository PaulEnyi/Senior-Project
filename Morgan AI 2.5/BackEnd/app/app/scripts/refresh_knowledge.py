import asyncio
import logging
from datetime import datetime
from pathlib import Path
import sys
sys.path.append('..')

from app.scripts.ingest_data import KnowledgeBaseIngestor
from app.services.knowledge_updater import KnowledgeUpdateService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def refresh_knowledge_base():
    """Refresh the knowledge base by re-ingesting all data"""
    try:
        logger.info(f"Starting knowledge base refresh at {datetime.utcnow()}")
        
        update_service = KnowledgeUpdateService()
        await update_service.initialize()
        result = await update_service.full_refresh()
        
        logger.info(f"Knowledge base refresh complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Knowledge base refresh failed: {str(e)}")
        raise

async def incremental_update(document_path: str = None):
    """Update specific documents without full refresh"""
    try:
        logger.info(f"Starting incremental update at {datetime.utcnow()}")
        
        update_service = KnowledgeUpdateService()
        await update_service.initialize()
        
        if document_path:
            # Update specific document
            logger.info(f"Updating document: {document_path}")
            files = [Path(document_path)]
            result = await update_service.incremental_update(files)
        else:
            # Update all modified documents
            logger.info("Checking for modified documents...")
            result = await update_service.incremental_update()
            
        logger.info(f"Incremental update complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Incremental update failed: {str(e)}")
        raise

async def start_auto_update_service(interval_hours: int = 24):
    """Start the automatic update service with file watching"""
    try:
        logger.info("Starting automatic knowledge base update service...")
        
        update_service = KnowledgeUpdateService()
        await update_service.initialize()
        
        # Start periodic updates in background
        update_task = asyncio.create_task(
            update_service.schedule_periodic_update(interval_hours)
        )
        
        # Start file watcher in background
        from app.services.knowledge_updater import start_file_watcher
        watcher_task = asyncio.create_task(
            start_file_watcher(update_service)
        )
        
        logger.info(f"Auto-update service started (checking every {interval_hours} hours)")
        logger.info("File watcher active for real-time updates")
        
        # Wait for both tasks
        await asyncio.gather(update_task, watcher_task)
        
    except Exception as e:
        logger.error(f"Auto-update service failed: {str(e)}")
        raise

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Refresh knowledge base")
    parser.add_argument(
        "--mode",
        choices=["full", "incremental", "auto"],
        default="full",
        help="Refresh mode: full (complete refresh), incremental (changed files only), auto (continuous monitoring)"
    )
    parser.add_argument(
        "--document",
        type=str,
        help="Specific document to update (incremental mode only)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=24,
        help="Update interval in hours (auto mode only, default: 24)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full":
        asyncio.run(refresh_knowledge_base())
    elif args.mode == "incremental":
        asyncio.run(incremental_update(args.document))
    elif args.mode == "auto":
        asyncio.run(start_auto_update_service(args.interval))

if __name__ == "__main__":
    main()