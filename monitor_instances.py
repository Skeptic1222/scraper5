"""
Server Instance Monitoring for Enhanced Media Scraper
- Monitors running instances
- Ensures single instance operation
- Memory tracking and optimization
"""

import os
import sys
import time
import psutil
import logging
from subprocess import run
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_scraper_processes():
    """Get all running scraper processes"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('scraper' in arg.lower() for arg in cmdline):
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def format_memory(bytes):
    """Format memory size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}TB"

def check_memory_usage():
    """Check memory usage of all scraper processes"""
    total_memory = 0
    process_info = []

    for proc in get_scraper_processes():
        try:
            memory = proc.info['memory_info'].rss
            total_memory += memory
            process_info.append({
                'pid': proc.info['pid'],
                'memory': memory,
                'cmdline': ' '.join(proc.info['cmdline'])
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return total_memory, process_info

def ensure_single_instance(max_instances=1):
    """Ensure only one instance is running"""
    processes = get_scraper_processes()

    if len(processes) > max_instances:
        logger.warning(f"Found {len(processes)} instances running - enforcing single instance")

        # Sort by memory usage and keep the lowest memory instance
        processes.sort(key=lambda p: p.info['memory_info'].rss)

        # Keep the first process (lowest memory usage)
        for proc in processes[max_instances:]:
            try:
                proc.terminate()
                logger.info(f"Terminated excess process {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.error(f"Failed to terminate process {proc.info['pid']}: {e}")

def optimize_memory():
    """Optimize memory usage"""
    total_memory, processes = check_memory_usage()
    memory_limit = 1024 * 1024 * 1024  # 1GB

    if total_memory > memory_limit:
        logger.warning(f"Memory usage ({format_memory(total_memory)}) exceeds limit")

        # Find largest memory consumer
        largest_proc = max(processes, key=lambda p: p['memory'])

        logger.info(f"Largest process: PID {largest_proc['pid']} using {format_memory(largest_proc['memory'])}")

        try:
            # First try Python's garbage collection
            import gc
            gc.collect()

            # Check if that helped
            new_total, _ = check_memory_usage()
            if new_total < memory_limit:
                logger.info("Memory optimization successful")
                return

            # If still high, restart the process
            proc = psutil.Process(largest_proc['pid'])
            proc.terminate()
            logger.info(f"Terminated high-memory process {largest_proc['pid']}")

            # Start a new instance
            run([sys.executable, 'start_production.py'])
            logger.info("Started new instance after memory optimization")

        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")

def main():
    """Main monitoring loop"""
    logger.info("Starting server instance monitoring")

    check_interval = 60  # Check every minute

    while True:
        try:
            # Ensure single instance
            ensure_single_instance()

            # Check and optimize memory
            optimize_memory()

            # Log status
            total_memory, processes = check_memory_usage()
            logger.info(f"Status: {len(processes)} instances, {format_memory(total_memory)} total memory")

            # Brief status for each process
            for proc in processes:
                logger.info(f"PID {proc['pid']}: {format_memory(proc['memory'])}")

            time.sleep(check_interval)

        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            time.sleep(check_interval)

if __name__ == '__main__':
    main()