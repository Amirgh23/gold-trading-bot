"""Log rotation and archiving."""

import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class LogRotation:
    """Manages log rotation and archiving."""
    
    def __init__(self, log_dir: str = "logs", archive_dir: str = "logs/archive"):
        self.log_dir = Path(log_dir)
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def rotate_logs(self, max_size_mb: int = 100) -> bool:
        """
        Rotate logs when they exceed max size.
        
        Args:
            max_size_mb: Maximum log file size in MB
        
        Returns:
            True if rotation performed
        """
        try:
            rotated = False
            max_size_bytes = max_size_mb * 1024 * 1024
            
            for log_file in self.log_dir.glob("*.json"):
                if log_file.stat().st_size > max_size_bytes:
                    self._rotate_file(log_file)
                    rotated = True
            
            if rotated:
                logger.info("Log rotation completed")
            
            return rotated
        except Exception as e:
            logger.error(f"Error rotating logs: {e}")
            return False
    
    def rotate_daily(self) -> bool:
        """Rotate logs daily."""
        try:
            rotated = False
            
            for log_file in self.log_dir.glob("*.json"):
                # Check if file was modified today
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime.date() < datetime.now().date():
                    self._rotate_file(log_file)
                    rotated = True
            
            if rotated:
                logger.info("Daily log rotation completed")
            
            return rotated
        except Exception as e:
            logger.error(f"Error rotating daily logs: {e}")
            return False
    
    def _rotate_file(self, log_file: Path) -> bool:
        """Rotate a single log file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{log_file.stem}_{timestamp}.json.gz"
            archive_path = self.archive_dir / archive_name
            
            # Compress and move to archive
            with open(log_file, 'rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Clear original file
            log_file.write_text("")
            
            logger.info(f"Rotated {log_file.name} to {archive_name}")
            return True
        except Exception as e:
            logger.error(f"Error rotating file {log_file}: {e}")
            return False
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Delete archived logs older than specified days.
        
        Args:
            days: Number of days to keep
        
        Returns:
            Number of files deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            for archive_file in self.archive_dir.glob("*.gz"):
                file_mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    archive_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old log: {archive_file.name}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old log files")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")
            return 0
    
    def get_log_stats(self) -> dict:
        """Get statistics about logs."""
        try:
            stats = {
                'active_logs': 0,
                'active_size_mb': 0,
                'archived_logs': 0,
                'archived_size_mb': 0,
            }
            
            # Active logs
            for log_file in self.log_dir.glob("*.json"):
                stats['active_logs'] += 1
                stats['active_size_mb'] += log_file.stat().st_size / (1024 * 1024)
            
            # Archived logs
            for archive_file in self.archive_dir.glob("*.gz"):
                stats['archived_logs'] += 1
                stats['archived_size_mb'] += archive_file.stat().st_size / (1024 * 1024)
            
            return stats
        except Exception as e:
            logger.error(f"Error getting log stats: {e}")
            return {}
