"""
Knowledge Base Refresh Script for Morgan AI Chatbot

This script refreshes the vector embeddings by reprocessing
the training data and updating the Pinecone index.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.services.langchain_service import LangChainRAGService
from app.services.pinecone_service import PineconeService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Refresh Morgan AI knowledge base embeddings"
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh even if recent data exists'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        default=True,
        help='Create backup before refresh (default: True)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_false',
        dest='backup',
        help='Skip backup creation'
    )
    
    parser.add_argument(
        '--data-path',
        type=str,
        default=None,
        help='Custom path to knowledge base data'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

async def check_existing_data():
    """Check if there's existing data in the index"""
    try:
        pinecone_service = PineconeService()
        stats = await pinecone_service.get_index_stats()
        
        total_vectors = stats.get('total_vectors', 0)
        logger.info(f"Current index contains {total_vectors} vectors")
        
        return total_vectors > 0
        
    except Exception as e:
        logger.warning(f"Could not check existing data: {str(e)}")
        return False

async def create_backup():
    """Create a backup of the current knowledge base"""
    try:
        logger.info("Creating backup before refresh...")
        
        # Import here to avoid circular imports
        from app.api.routes.admin import BackupService
        
        backup_service = BackupService()
        
        backup_info = await backup_service.create_full_backup(
            include_vectors=True,
            include_threads=False,  # Don't backup threads during knowledge refresh
            include_knowledge_base=True,
            backup_name=f"pre_refresh_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )
        
        logger.info(f"Backup created: {backup_info['backup_name']}")
        return True
        
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        return False

async def refresh_knowledge_base(data_path=None):
    """Refresh the knowledge base embeddings"""
    try:
        logger.info("Starting knowledge base refresh...")
        
        # Initialize RAG service
        rag_service = LangChainRAGService()
        
        # Process knowledge base
        if data_path:
            logger.info(f"Using custom data path: {data_path}")
            success = await rag_service.process_knowledge_base(data_path)
        else:
            logger.info("Using default knowledge base path")
            success = await rag_service.process_knowledge_base()
        
        if success:
            logger.info(" Knowledge base refresh completed successfully")
            
            # Get updated stats
            pinecone_service = PineconeService()
            stats = await pinecone_service.get_index_stats()
            total_vectors = stats.get('total_vectors', 0)
            logger.info(f"Index now contains {total_vectors} vectors")
            
            return True
        else:
            logger.error(" Knowledge base refresh failed")
            return False
            
    except Exception as e:
        logger.error(f"Knowledge base refresh failed: {str(e)}")
        return False

async def verify_refresh():
    """Verify that the refresh was successful"""
    try:
        logger.info("Verifying refresh results...")
        
        # Test basic RAG functionality
        rag_service = LangChainRAGService()
        
        # Test queries
        test_queries = [
            "Morgan State Computer Science",
            "faculty information",
            "course requirements",
            "student organizations"
        ]
        
        for query in test_queries:
            try:
                context = await rag_service.get_relevant_context(query, max_results=2)
                if context and len(context.strip()) > 50:
                    logger.info(f" Test query '{query}' returned relevant context")
                else:
                    logger.warning(f" Test query '{query}' returned limited context")
            except Exception as e:
                logger.error(f" Test query '{query}' failed: {str(e)}")
                return False
        
        logger.info(" Verification completed - knowledge base is working")
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return False

async def main_refresh_process(args):
    """Main refresh process"""
    try:
        # Set verbose logging if requested
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.info("Verbose logging enabled")
        
        # Check existing data
        has_existing_data = await check_existing_data()
        
        if has_existing_data and not args.force:
            logger.info("Existing data found in index")
            confirm = input("Continue with refresh? This will replace existing data (y/N): ")
            if confirm.lower() != 'y':
                logger.info("Refresh cancelled by user")
                return False
        
        # Create backup if requested
        if args.backup and has_existing_data:
            backup_success = await create_backup()
            if not backup_success:
                logger.warning("Backup failed, but continuing with refresh...")
        
        # Refresh knowledge base
        refresh_success = await refresh_knowledge_base(args.data_path)
        if not refresh_success:
            return False
        
        # Verify the refresh
        verify_success = await verify_refresh()
        if not verify_success:
            logger.warning("Verification had issues, but refresh may still be successful")
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Refresh cancelled by user")
        return False
    except Exception as e:
        logger.error(f"Refresh process failed: {str(e)}")
        return False

def main():
    """Main function"""
    import asyncio
    
    print("Morgan AI Chatbot - Knowledge Base Refresh")
    print("=" * 45)
    
    # Parse arguments
    args = parse_arguments()
    
    # Display configuration
    print(f"Force refresh: {args.force}")
    print(f"Create backup: {args.backup}")
    print(f"Data path: {args.data_path or 'default'}")
    print(f"Verbose: {args.verbose}")
    print()
    
    # Run refresh process
    success = asyncio.run(main_refresh_process(args))
    
    if success:
        print("\n" + "="*50)
        print(" Knowledge base refresh completed successfully!")
        print("\nNext steps:")
        print("1. Test the chatbot with some queries")
        print("2. Check the admin dashboard for updated statistics")
        print("3. Monitor the logs for any issues")
        print("="*50)
        sys.exit(0)
    else:
        print("\n Knowledge base refresh failed!")
        print("Check the logs above for error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()