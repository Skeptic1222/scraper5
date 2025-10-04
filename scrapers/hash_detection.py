"""
Hash-Based Detection System

Detects and prevents download of:
- Fake/placeholder images (by hash)
- Duplicate files (by hash)
- Known bad URLs (by pattern and hash)
"""

import os
import json
import hashlib
import logging
from typing import Dict, Set, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class HashDatabase:
    """Database of known file hashes for fake detection and deduplication"""

    def __init__(self, db_file: str = 'config/hash_database.json'):
        self.db_file = db_file
        self.fake_hashes: Set[str] = set()
        self.fake_urls: Set[str] = set()
        self.seen_hashes: Dict[str, str] = {}  # hash -> filepath
        self.load_database()

    def load_database(self):
        """Load hash database from file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.fake_hashes = set(data.get('fake_hashes', []))
                    self.fake_urls = set(data.get('fake_urls', []))
                    logger.info(f"[HASH DB] Loaded {len(self.fake_hashes)} fake hashes, {len(self.fake_urls)} fake URLs")
            else:
                # Initialize with known fakes
                self._initialize_known_fakes()
                self.save_database()
        except Exception as e:
            logger.error(f"[HASH DB] Error loading database: {e}")
            self._initialize_known_fakes()

    def _initialize_known_fakes(self):
        """Initialize with known fake image hashes"""
        # Known fake/placeholder image hashes
        self.fake_hashes = {
            # plc.gif from motherless (45 bytes)
            '6fbc753e9030176cc6435f20913a698e',

            # Empty file (0 bytes)
            'd41d8cd98f00b204e9800998ecf8427e',

            # Common placeholder images (to be populated as discovered)
            # Add more as we find them
        }

        # Known fake/placeholder URLs
        self.fake_urls = {
            'https://cdn5-static.motherlessmedia.com/images/plc.gif',
            'https://via.placeholder.com/',
            'https://placehold.it/',
            'https://dummyimage.com/',
        }

        logger.info(f"[HASH DB] Initialized with {len(self.fake_hashes)} known fakes")

    def save_database(self):
        """Save hash database to file"""
        try:
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
            data = {
                'fake_hashes': list(self.fake_hashes),
                'fake_urls': list(self.fake_urls),
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"[HASH DB] Saved database to {self.db_file}")
        except Exception as e:
            logger.error(f"[HASH DB] Error saving database: {e}")

    def calculate_hash(self, filepath: str) -> str:
        """Calculate MD5 hash of a file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"[HASH DB] Error calculating hash for {filepath}: {e}")
            return None

    def is_fake_url(self, url: str) -> bool:
        """Check if URL is a known fake"""
        return any(fake_url in url for fake_url in self.fake_urls)

    def is_fake_hash(self, file_hash: str) -> bool:
        """Check if hash matches a known fake"""
        return file_hash in self.fake_hashes

    def is_duplicate(self, file_hash: str) -> Tuple[bool, str]:
        """Check if file hash has been seen before"""
        if file_hash in self.seen_hashes:
            return True, self.seen_hashes[file_hash]
        return False, None

    def register_file(self, filepath: str, file_hash: str = None):
        """Register a file as downloaded"""
        if file_hash is None:
            file_hash = self.calculate_hash(filepath)

        if file_hash:
            self.seen_hashes[file_hash] = filepath

    def mark_as_fake(self, filepath: str = None, file_hash: str = None, url: str = None):
        """Mark a file/URL as fake"""
        if filepath and not file_hash:
            file_hash = self.calculate_hash(filepath)

        if file_hash:
            self.fake_hashes.add(file_hash)
            logger.info(f"[HASH DB] Added fake hash: {file_hash}")

        if url:
            self.fake_urls.add(url)
            logger.info(f"[HASH DB] Added fake URL: {url}")

        self.save_database()

    def validate_file(self, filepath: str, url: str = '') -> Dict[str, any]:
        """
        Comprehensive file validation

        Returns:
            Dict with 'valid', 'reason', 'hash', 'is_duplicate', 'duplicate_path'
        """
        result = {
            'valid': True,
            'reason': None,
            'hash': None,
            'is_duplicate': False,
            'duplicate_path': None
        }

        # Check 1: URL blacklist
        if url and self.is_fake_url(url):
            result['valid'] = False
            result['reason'] = 'fake_url'
            logger.info(f"[HASH DB] ❌ Blocked fake URL: {url}")
            return result

        # Check 2: Calculate hash
        file_hash = self.calculate_hash(filepath)
        if not file_hash:
            result['valid'] = False
            result['reason'] = 'hash_calculation_failed'
            return result

        result['hash'] = file_hash

        # Check 3: Fake hash check
        if self.is_fake_hash(file_hash):
            result['valid'] = False
            result['reason'] = 'fake_hash'
            logger.info(f"[HASH DB] ❌ Blocked fake file (hash: {file_hash}): {os.path.basename(filepath)}")
            return result

        # Check 4: Duplicate check
        is_dup, dup_path = self.is_duplicate(file_hash)
        if is_dup:
            result['is_duplicate'] = True
            result['duplicate_path'] = dup_path
            logger.info(f"[HASH DB] ⚠️  Duplicate detected: {os.path.basename(filepath)} (original: {os.path.basename(dup_path)})")
            # Note: We still mark as valid, but caller can decide to delete

        # Register this file
        self.register_file(filepath, file_hash)

        return result

    def cleanup_duplicates(self, directory: str, delete: bool = True) -> Dict[str, int]:
        """
        Find and optionally delete duplicate files in a directory

        Returns:
            Dict with 'total_files', 'unique_files', 'duplicates', 'deleted'
        """
        stats = {
            'total_files': 0,
            'unique_files': 0,
            'duplicates': 0,
            'deleted': 0,
            'space_saved': 0
        }

        hash_map = {}

        # Scan directory
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                stats['total_files'] += 1

                try:
                    file_hash = self.calculate_hash(filepath)
                    if not file_hash:
                        continue

                    if file_hash in hash_map:
                        # Duplicate found
                        stats['duplicates'] += 1
                        original = hash_map[file_hash]

                        if delete:
                            file_size = os.path.getsize(filepath)
                            os.remove(filepath)
                            stats['deleted'] += 1
                            stats['space_saved'] += file_size
                            logger.info(f"[HASH DB] Deleted duplicate: {filename} (original: {os.path.basename(original)})")
                        else:
                            logger.info(f"[HASH DB] Found duplicate: {filename} (original: {os.path.basename(original)})")
                    else:
                        hash_map[file_hash] = filepath
                        stats['unique_files'] += 1

                except Exception as e:
                    logger.warning(f"[HASH DB] Error processing {filepath}: {e}")

        logger.info(f"[HASH DB] Cleanup complete: {stats['deleted']} duplicates deleted, {stats['space_saved']/1024/1024:.2f} MB saved")
        return stats

    def cleanup_fakes(self, directory: str, delete: bool = True) -> Dict[str, int]:
        """
        Find and optionally delete fake/placeholder files

        Returns:
            Dict with statistics
        """
        stats = {
            'total_scanned': 0,
            'fakes_found': 0,
            'fakes_deleted': 0,
            'space_saved': 0
        }

        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                stats['total_scanned'] += 1

                try:
                    file_hash = self.calculate_hash(filepath)
                    if not file_hash:
                        continue

                    if self.is_fake_hash(file_hash):
                        stats['fakes_found'] += 1

                        if delete:
                            file_size = os.path.getsize(filepath)
                            os.remove(filepath)
                            stats['fakes_deleted'] += 1
                            stats['space_saved'] += file_size
                            logger.info(f"[HASH DB] Deleted fake: {filename} (hash: {file_hash})")

                except Exception as e:
                    logger.warning(f"[HASH DB] Error processing {filepath}: {e}")

        logger.info(f"[HASH DB] Fake cleanup complete: {stats['fakes_deleted']} fakes deleted, {stats['space_saved']/1024:.2f} KB saved")
        return stats

    def get_stats(self) -> Dict[str, any]:
        """Get database statistics"""
        return {
            'fake_hashes': len(self.fake_hashes),
            'fake_urls': len(self.fake_urls),
            'seen_files': len(self.seen_hashes),
            'database_file': self.db_file
        }


# Global hash database instance
hash_db = HashDatabase()


def is_fake_url(url: str) -> bool:
    """Quick check if URL is fake"""
    return hash_db.is_fake_url(url)


def validate_downloaded_file(filepath: str, url: str = '') -> bool:
    """
    Validate a downloaded file

    Returns:
        True if valid, False if fake or duplicate (and should be deleted)
    """
    result = hash_db.validate_file(filepath, url)

    if not result['valid']:
        # Delete fake file
        try:
            os.remove(filepath)
            logger.info(f"[HASH DB] Auto-deleted fake file: {os.path.basename(filepath)} (reason: {result['reason']})")
        except Exception as e:
            logger.warning(f"[HASH DB] Could not delete fake file: {e}")
        return False

    if result['is_duplicate']:
        # Delete duplicate file
        try:
            os.remove(filepath)
            logger.info(f"[HASH DB] Auto-deleted duplicate: {os.path.basename(filepath)}")
        except Exception as e:
            logger.warning(f"[HASH DB] Could not delete duplicate: {e}")
        return False

    return True


def mark_file_as_fake(filepath: str):
    """Mark a file as fake for future detection"""
    hash_db.mark_as_fake(filepath=filepath)


def cleanup_directory(directory: str, remove_duplicates: bool = True, remove_fakes: bool = True):
    """Cleanup a directory of duplicates and fakes"""
    if remove_fakes:
        fake_stats = hash_db.cleanup_fakes(directory, delete=True)
        logger.info(f"[CLEANUP] Removed {fake_stats['fakes_deleted']} fake files")

    if remove_duplicates:
        dup_stats = hash_db.cleanup_duplicates(directory, delete=True)
        logger.info(f"[CLEANUP] Removed {dup_stats['deleted']} duplicate files")


# CLI entry point for manual cleanup
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python hash_detection.py <command> [directory]")
        print("Commands:")
        print("  cleanup <dir>    - Remove duplicates and fakes")
        print("  scan <dir>       - Scan for duplicates and fakes (no delete)")
        print("  stats            - Show database statistics")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'stats':
        stats = hash_db.get_stats()
        print(f"Hash Database Statistics:")
        print(f"  Fake hashes: {stats['fake_hashes']}")
        print(f"  Fake URLs: {stats['fake_urls']}")
        print(f"  Seen files: {stats['seen_files']}")
        print(f"  Database: {stats['database_file']}")

    elif command in ['cleanup', 'scan']:
        directory = sys.argv[2] if len(sys.argv) > 2 else 'downloads'
        delete = command == 'cleanup'

        print(f"{'Cleaning' if delete else 'Scanning'} {directory}...")

        fake_stats = hash_db.cleanup_fakes(directory, delete=delete)
        print(f"Fakes: {fake_stats['fakes_found']} found, {fake_stats['fakes_deleted']} deleted")

        dup_stats = hash_db.cleanup_duplicates(directory, delete=delete)
        print(f"Duplicates: {dup_stats['duplicates']} found, {dup_stats['deleted']} deleted")
        print(f"Space saved: {(fake_stats['space_saved'] + dup_stats['space_saved'])/1024/1024:.2f} MB")
