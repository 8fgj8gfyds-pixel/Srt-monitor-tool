#!/usr/bin/env python3
"""
SRT Configuration Manager - Handles SRT caller/listener modes
"""

import subprocess
import json
import time
import threading
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SRTManager:
    def __init__(self):
        self.current_config = None
        self.process = None
        self.is_running = False
        self.stats_thread = None
        self.stop_event = threading.Event()

    def start_srt_listener(self, config: Dict[str, Any]) -> bool:
        """Start SRT listener with given configuration"""
        try:
            cmd = [
                "ffmpeg",
                "-i", "udp://0.0.0.0:{}".format(config['listener_port']),
                "-c", "copy",
                "-f", "mpegts",
                "srt://0.0.0.0:{}?mode=listener&latency={}&payloadsize={}&maxbw={}".format(
                    config['listener_port'],
                    config['latency_ms'],
                    config['payload_size'],
                    config['max_bandwidth']
                )
            ]

            logger.info(f"Starting SRT listener: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.is_running = True
            self.current_config = config
            return True
        except Exception as e:
            logger.error(f"Failed to start SRT listener: {e}")
            return False

    def start_srt_caller(self, config: Dict[str, Any]) -> bool:
        """Start SRT caller with given configuration"""
        try:
            cmd = [
                "ffmpeg",
                "-re",
                "-i", "udp://0.0.0.0:{}".format(config['caller_port']),
                "-c", "copy",
                "-f", "mpegts",
                "srt://{}:{}?mode=caller&latency={}&payloadsize={}&maxbw={}".format(
                    config['remote_address'],
                    config['remote_port'],
                    config['latency_ms'],
                    config['payload_size'],
                    config['max_bandwidth']
                )
            ]

            logger.info(f"Starting SRT caller: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.is_running = True
            self.current_config = config
            return True
        except Exception as e:
            logger.error(f"Failed to start SRT caller: {e}")
            return False

    def stop_srt(self) -> bool:
        """Stop SRT process"""
        if self.process and self.is_running:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.is_running = False
                self.current_config = None
                return True
            except Exception as e:
                logger.error(f"Error stopping SRT: {e}")
                return False
        return True

    def get_srt_stats(self) -> Dict[str, Any]:
        """Get SRT statistics (placeholder - would integrate with actual SRT stats)"""
        # In a real implementation, this would parse SRT stats from ffmpeg output
        return {
            "timestamp": int(time.time()),
            "status": "running" if self.is_running else "stopped",
            "config": self.current_config
        }
