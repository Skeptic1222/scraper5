"""
Memory Manager Stub Module
Provides stub functions to prevent import errors while the actual memory management is disabled.
"""

import logging

logger = logging.getLogger(__name__)

def start_memory_management():
    """Stub function to prevent import errors when memory management is called"""
    logger.info("Memory management stub: start_memory_management called (no-op)")
    pass

def cleanup_memory():
    """Stub function to prevent cleanup errors"""
    logger.info("Memory management stub: cleanup_memory called (no-op)")
    pass

def monitor_memory():
    """Stub function for memory monitoring"""
    logger.info("Memory management stub: monitor_memory called (no-op)")
    return {
        'used': 0,
        'available': 0,
        'percent': 0
    }

def optimize_memory():
    """Stub function for memory optimization"""
    logger.info("Memory management stub: optimize_memory called (no-op)")
    pass

# Export all functions
__all__ = ['start_memory_management', 'cleanup_memory', 'monitor_memory', 'optimize_memory']
