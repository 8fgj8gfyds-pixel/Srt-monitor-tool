#!/usr/bin/env python3
"""
Statistics Collector - Collects and processes SRT/Iperf statistics
"""

import time
import json
import threading
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StatsCollector:
    def __init__(self):
        self.stats_history = []
        self.current_stats = {
            "srt": {},
            "iperf": {},
            "system": {}
        }
        self.running = False
        self.lock = threading.Lock()

    def start_collection(self, interval: float = 1.0):
        """Start collecting statistics at given interval"""
        self.running = True
        self.collection_thread = threading.Thread(
            target=self._collect_loop,
            args=(interval,),
            daemon=True
        )
        self.collection_thread.start()

    def stop_collection(self):
        """Stop collecting statistics"""
        self.running = False
        if hasattr(self, 'collection_thread'):
            self.collection_thread.join()

    def _collect_loop(self, interval: float):
        """Main collection loop"""
        while self.running:
            self._collect_single()
            time.sleep(interval)

    def _collect_single(self):
        """Collect statistics from all sources"""
        stats = {
            "timestamp": int(time.time()),
            "datetime": datetime.now().isoformat(),
            "srt": {},
            "iperf": {},
            "system": self._get_system_stats()
        }

        # Collect SRT stats (would integrate with actual SRT stats)
        stats['srt'] = {
            "status": "idle",
            "throughput": 0,
            "packet_loss": 0,
            "retransmitted": 0,
            "dropped": 0,
            "out_of_order": 0
        }

        # Collect iperf stats
        stats['iperf'] = {
            "status": "idle",
            "bandwidth": 0,
            "jitter": 0,
            "packet_loss": 0
        }

        with self.lock:
            self.current_stats = stats
            self.stats_history.append(stats)

            # Keep history limited
            if len(self.stats_history) > 1000:
                self.stats_history = self.stats_history[-1000:]

    def _get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        import psutil
        import socket

        net_io = psutil.net_io_counters()
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()

        return {
            "cpu_usage": cpu,
            "memory_usage": mem.percent,
            "network_rx": net_io.bytes_recv,
            "network_tx": net_io.bytes_sent,
            "hostname": socket.gethostname()
        }

    def get_latest_stats(self) -> Dict[str, Any]:
        """Get latest statistics"""
        with self.lock:
            return self.current_stats.copy()

    def get_stats_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get statistics history"""
        with self.lock:
            return self.stats_history[-limit:].copy()

    def clear_stats(self):
        """Clear all collected statistics"""
        with self.lock:
            self.stats_history = []
            self.current_stats = {
                "srt": {},
                "iperf": {},
                "system": {}
            }
