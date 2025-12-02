"""
Backs up knowledge base, embeddings, and database
"""

import asyncio
import json
import logging
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.pinecone_service import PineconeService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackupManager:
    """Manage backups for the Morgan AI Chatbot"""
    
    def __init__(self):
        self.backup_dir = Path("/app/backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.knowledge_base_dir = settings.KNOWLEDGE_BASE_DIR
        self.processed_dir = settings.PROCESSED_DIR
        self.pinecone_service = PineconeService()
        
    def create_backup_name(self, prefix: str = "backup") -> str:
        """Generate a unique backup filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}"
    
    async def backup_knowledge_base(self, backup_path: Path) -> Dict[str, Any]:
        """Backup all knowledge base files"""
        kb_backup = backup_path / "knowledge_base"
        kb_backup.mkdir(parents=True, exist_ok=True)
        
        files_backed_up = 0
        total_size = 0
        
        try:
            # Copy all files from knowledge base directory
            for file_path in self.knowledge_base_dir.iterdir():
                if file_path.is_file():
                    dest = kb_backup / file_path.name
                    shutil.copy2(file_path, dest)
                    files_backed_up += 1
                    total_size += file_path.stat().st_size
                    logger.info(f"Backed up: {file_path.name}")
            
            return {
                "success": True,
                "files_backed_up": files_backed_up,
                "total_size_bytes": total_size,
                "backup_path": str(kb_backup)
            }
            
        except Exception as e:
            logger.error(f"Knowledge base backup failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def backup_vector_metadata(self, backup_path: Path) -> Dict[str, Any]:
        """Backup vector database metadata and stats"""
        vector_backup = backup_path / "vectors"
        vector_backup.mkdir(parents=True, exist_ok=True)
        
        try:
            # Initialize Pinecone
            await self.pinecone_service.initialize()
            
            # Get index stats
            stats = await self.pinecone_service.get_stats()
            
            # Save stats to file
            stats_file = vector_backup / "index_stats.json"
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            
            logger.info(f"Backed up vector stats: {stats.get('total_vector_count', 0)} vectors")
            
            return {
                "success": True,
                "vector_count": stats.get("total_vector_count", 0),
                "stats_file": str(stats_file)
            }
            
        except Exception as e:
            logger.error(f"Vector backup failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def backup_processed_data(self, backup_path: Path) -> Dict[str, Any]:
        """Backup processed data and logs"""
        processed_backup = backup_path / "processed"
        processed_backup.mkdir(parents=True, exist_ok=True)
        
        files_backed_up = 0
        
        try:
            # Copy all files from processed directory
            if self.processed_dir.exists():
                for file_path in self.processed_dir.iterdir():
                    if file_path.is_file():
                        dest = processed_backup / file_path.name
                        shutil.copy2(file_path, dest)
                        files_backed_up += 1
            
            return {
                "success": True,
                "files_backed_up": files_backed_up,
                "backup_path": str(processed_backup)
            }
            
        except Exception as e:
            logger.error(f"Processed data backup failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_archive(self, backup_path: Path) -> Optional[Path]:
        """Create a compressed archive of the backup"""
        archive_name = f"{backup_path.name}.tar.gz"
        archive_path = self.backup_dir / archive_name
        
        try:
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(backup_path, arcname=backup_path.name)
            
            logger.info(f"Created archive: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Archive creation failed: {str(e)}")
            return None
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """Remove old backups, keeping only the most recent ones"""
        try:
            # Get all backup archives
            archives = sorted(
                self.backup_dir.glob("backup_*.tar.gz"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove old backups
            if len(archives) > keep_count:
                for archive in archives[keep_count:]:
                    archive.unlink()
                    logger.info(f"Removed old backup: {archive.name}")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
    
    async def create_full_backup(self, include_vectors: bool = True) -> Dict[str, Any]:
        """Create a complete backup of the system"""
        backup_name = self.create_backup_name()
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Creating full backup: {backup_name}")
        start_time = datetime.now()
        
        results = {
            "backup_name": backup_name,
            "start_time": start_time.isoformat(),
            "components": {}
        }
        
        # Backup knowledge base
        kb_result = await self.backup_knowledge_base(backup_path)
        results["components"]["knowledge_base"] = kb_result
        
        # Backup vector metadata
        if include_vectors:
            vector_result = await self.backup_vector_metadata(backup_path)
            results["components"]["vectors"] = vector_result
        
        # Backup processed data
        processed_result = await self.backup_processed_data(backup_path)
        results["components"]["processed_data"] = processed_result
        
        # Save backup metadata
        metadata_file = backup_path / "backup_metadata.json"
        results["end_time"] = datetime.now().isoformat()
        results["duration_seconds"] = (datetime.now() - start_time).total_seconds()
        
        with open(metadata_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Create archive
        archive_path = self.create_archive(backup_path)
        if archive_path:
            results["archive_path"] = str(archive_path)
            results["archive_size_mb"] = archive_path.stat().st_size / (1024 * 1024)
            
            # Remove uncompressed backup
            shutil.rmtree(backup_path)
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        logger.info("="*50)
        logger.info(f"Backup complete: {backup_name}")
        logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
        if archive_path:
            logger.info(f"Archive size: {results['archive_size_mb']:.2f} MB")
        logger.info("="*50)
        
        return results
    
    async def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """Restore from a backup archive"""
        archive_path = self.backup_dir / f"{backup_name}.tar.gz"
        
        if not archive_path.exists():
            return {
                "success": False,
                "error": f"Backup not found: {backup_name}"
            }
        
        try:
            logger.info(f"Restoring from backup: {backup_name}")
            
            # Extract archive
            temp_dir = self.backup_dir / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(exist_ok=True)
            
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # Find extracted backup directory
            backup_dir = next(temp_dir.iterdir())
            
            # Restore knowledge base
            kb_source = backup_dir / "knowledge_base"
            if kb_source.exists():
                for file_path in kb_source.iterdir():
                    dest = self.knowledge_base_dir / file_path.name
                    shutil.copy2(file_path, dest)
                logger.info("Restored knowledge base files")
            
            # Restore processed data
            processed_source = backup_dir / "processed"
            if processed_source.exists():
                for file_path in processed_source.iterdir():
                    dest = self.processed_dir / file_path.name
                    shutil.copy2(file_path, dest)
                logger.info("Restored processed data")
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            return {
                "success": True,
                "backup_name": backup_name,
                "restored_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for archive in self.backup_dir.glob("backup_*.tar.gz"):
            stat = archive.stat()
            backups.append({
                "name": archive.stem,
                "path": str(archive),
                "size_mb": stat.st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)

async def main():
    """Main entry point for backup script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup Morgan AI Chatbot data")
    parser.add_argument(
        "--action",
        choices=["backup", "restore", "list"],
        default="backup",
        help="Action to perform"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Backup name for restore operation"
    )
    parser.add_argument(
        "--no-vectors",
        action="store_true",
        help="Exclude vector metadata from backup"
    )
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.action == "backup":
        result = await manager.create_full_backup(include_vectors=not args.no_vectors)
        if result.get("archive_path"):
            print(f"\nBackup created successfully: {result['backup_name']}")
            print(f"Archive: {result['archive_path']}")
        else:
            print("\nBackup failed")
            sys.exit(1)
            
    elif args.action == "restore":
        if not args.name:
            print("Backup name required for restore")
            sys.exit(1)
        
        result = await manager.restore_backup(args.name)
        if result["success"]:
            print(f"\nRestore successful: {args.name}")
        else:
            print(f"\nRestore failed: {result.get('error')}")
            sys.exit(1)
            
    elif args.action == "list":
        backups = manager.list_backups()
        if backups:
            print("\nAvailable backups:")
            for backup in backups:
                print(f"  {backup['name']} - {backup['size_mb']:.2f} MB - {backup['created']}")
        else:
            print("\nNo backups found")

if __name__ == "__main__":
    asyncio.run(main())