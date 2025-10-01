"""
Backup Data Script for Morgan AI Chatbot

This script creates comprehensive backups of the Morgan AI system including
vector embeddings, conversation threads, and knowledge base files.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Create backup of Morgan AI Chatbot data"
    )
    
    parser.add_argument(
        '--include-vectors',
        action='store_true',
        default=True,
        help='Include vector embeddings in backup (default: True)'
    )
    
    parser.add_argument(
        '--no-vectors',
        action='store_false',
        dest='include_vectors',
        help='Exclude vector embeddings from backup'
    )
    
    parser.add_argument(
        '--include-threads',
        action='store_true',
        default=True,
        help='Include conversation threads in backup (default: True)'
    )
    
    parser.add_argument(
        '--no-threads',
        action='store_false',
        dest='include_threads',
        help='Exclude conversation threads from backup'
    )
    
    parser.add_argument(
        '--include-knowledge',
        action='store_true',
        default=True,
        help='Include knowledge base files in backup (default: True)'
    )
    
    parser.add_argument(
        '--no-knowledge',
        action='store_false',
        dest='include_knowledge',
        help='Exclude knowledge base files from backup'
    )
    
    parser.add_argument(
        '--backup-name',
        type=str,
        default=None,
        help='Custom backup name (default: auto-generated)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Custom output directory (default: data/backups)'
    )
    
    parser.add_argument(
        '--list-backups',
        action='store_true',
        help='List existing backups and exit'
    )
    
    parser.add_argument(
        '--delete-backup',
        type=str,
        metavar='BACKUP_NAME',
        help='Delete a specific backup'
    )
    
    parser.add_argument(
        '--cleanup-old',
        type=int,
        metavar='DAYS',
        help='Delete backups older than N days'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

async def create_backup(args):
    """Create a comprehensive backup"""
    try:
        logger.info("Starting backup creation...")
        
        # Import here to avoid circular imports
        from app.api.routes.admin import BackupService
        
        backup_service = BackupService()
        
        # Generate backup name if not provided
        backup_name = args.backup_name
        if not backup_name:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            components = []
            if args.include_vectors:
                components.append("vectors")
            if args.include_threads:
                components.append("threads")
            if args.include_knowledge:
                components.append("kb")
            
            component_str = "_".join(components) if components else "empty"
            backup_name = f"manual_backup_{component_str}_{timestamp}"
        
        # Create backup
        backup_info = await backup_service.create_full_backup(
            include_vectors=args.include_vectors,
            include_threads=args.include_threads,
            include_knowledge_base=args.include_knowledge,
            backup_name=backup_name
        )
        
        # Display results
        print("\n" + "="*60)
        print("BACKUP COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Backup Name: {backup_info['backup_name']}")
        print(f"Created: {backup_info['created_at']}")
        print(f"Status: {backup_info['status']}")
        print(f"Total Size: {backup_info.get('total_size', 0):,} bytes")
        
        if 'archive_path' in backup_info:
            print(f"Archive: {backup_info['archive_path']}")
            print(f"Archive Size: {backup_info.get('archive_size', 0):,} bytes")
        
        # Show component details
        if 'components' in backup_info:
            print("\nComponents backed up:")
            for component, details in backup_info['components'].items():
                status = details.get('status', 'unknown')
                print(f"  {component}: {status}")
                
                if component == 'vectors' and 'total_vectors' in details:
                    print(f"    - Total vectors: {details['total_vectors']}")
                elif component == 'threads' and 'total_threads' in details:
                    print(f"    - Total threads: {details['total_threads']}")
                    print(f"    - Exported threads: {details['exported_threads']}")
                elif component == 'knowledge_base' and 'total_files' in details:
                    print(f"    - Total files: {details['total_files']}")
                    print(f"    - Total size: {details['total_size']:,} bytes")
        
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        return False

async def list_backups():
    """List existing backups"""
    try:
        from app.api.routes.admin import BackupService
        
        backup_service = BackupService()
        backups = await backup_service.list_backups()
        
        if not backups:
            print("No backups found.")
            return
        
        print("\n" + "="*80)
        print("EXISTING BACKUPS")
        print("="*80)
        print(f"{'Name':<30} {'Created':<20} {'Size':<12} {'Status':<10}")
        print("-"*80)
        
        total_size = 0
        for backup in backups:
            name = backup.get('backup_name', 'Unknown')[:28]
            created = backup.get('created_at', 'Unknown')[:19].replace('T', ' ')
            size = backup.get('file_size', 0)
            status = backup.get('status', 'Unknown')
            
            size_str = f"{size:,}" if size else "Unknown"
            total_size += size if size else 0
            
            print(f"{name:<30} {created:<20} {size_str:<12} {status:<10}")
        
        print("-"*80)
        print(f"Total backups: {len(backups)}")
        print(f"Total size: {total_size:,} bytes ({total_size / (1024**2):.1f} MB)")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Failed to list backups: {str(e)}")

async def delete_backup(backup_name):
    """Delete a specific backup"""
    try:
        from app.api.routes.admin import BackupService
        
        backup_service = BackupService()
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete backup '{backup_name}'? (y/N): ")
        if confirm.lower() != 'y':
            print("Deletion cancelled.")
            return False
        
        success = await backup_service.delete_backup(backup_name)
        
        if success:
            print(f"Backup '{backup_name}' deleted successfully.")
            return True
        else:
            print(f"Backup '{backup_name}' not found.")
            return False
            
    except Exception as e:
        logger.error(f"Failed to delete backup: {str(e)}")
        return False

async def cleanup_old_backups(days):
    """Delete backups older than specified days"""
    try:
        from app.api.routes.admin import BackupService
        from datetime import timedelta
        
        backup_service = BackupService()
        backups = await backup_service.list_backups()
        
        if not backups:
            print("No backups found.")
            return
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_backups = []
        
        for backup in backups:
            try:
                created_str = backup.get('created_at', '')
                created_date = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                
                if created_date < cutoff_date:
                    old_backups.append(backup)
            except ValueError:
                continue
        
        if not old_backups:
            print(f"No backups older than {days} days found.")
            return
        
        print(f"\nFound {len(old_backups)} backups older than {days} days:")
        for backup in old_backups:
            name = backup.get('backup_name', 'Unknown')
            created = backup.get('created_at', 'Unknown')
            print(f"  - {name} (created: {created})")
        
        confirm = input(f"\nDelete these {len(old_backups)} old backups? (y/N): ")
        if confirm.lower() != 'y':
            print("Cleanup cancelled.")
            return
        
        deleted_count = 0
        for backup in old_backups:
            backup_name = backup.get('backup_name')
            if backup_name:
                success = await backup_service.delete_backup(backup_name)
                if success:
                    deleted_count += 1
                    print(f"Deleted: {backup_name}")
                else:
                    print(f"Failed to delete: {backup_name}")
        
        print(f"\nCleanup completed. Deleted {deleted_count}/{len(old_backups)} backups.")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")

def print_backup_summary(args):
    """Print summary of what will be backed up"""
    print("Backup Configuration:")
    print(f"  Include vectors: {args.include_vectors}")
    print(f"  Include threads: {args.include_threads}")
    print(f"  Include knowledge base: {args.include_knowledge}")
    print(f"  Backup name: {args.backup_name or 'auto-generated'}")
    print(f"  Output directory: {args.output_dir or 'default'}")
    print()

async def main_process(args):
    """Main backup process"""
    try:
        # Set verbose logging if requested
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.info("Verbose logging enabled")
        
        # Handle list backups
        if args.list_backups:
            await list_backups()
            return True
        
        # Handle delete backup
        if args.delete_backup:
            return await delete_backup(args.delete_backup)
        
        # Handle cleanup old backups
        if args.cleanup_old:
            await cleanup_old_backups(args.cleanup_old)
            return True
        
        # Handle backup creation
        if not any([args.include_vectors, args.include_threads, args.include_knowledge]):
            print("Warning: No components selected for backup. Nothing to do.")
            return False
        
        print_backup_summary(args)
        
        # Create backup
        return await create_backup(args)
        
    except KeyboardInterrupt:
        logger.info("Backup cancelled by user")
        return False
    except Exception as e:
        logger.error(f"Backup process failed: {str(e)}")
        return False

def main():
    """Main function"""
    import asyncio
    
    print("Morgan AI Chatbot - Backup Utility")
    print("=" * 35)
    
    # Parse arguments
    args = parse_arguments()
    
    # Run backup process
    success = asyncio.run(main_process(args))
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()