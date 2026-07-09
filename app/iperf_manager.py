#!/usr/bin/env python3
"""
Iperf3 Integration Manager
"""

import subprocess
import json
import threading
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class IperfManager:
    def __init__(self):
        self.process = None
        self.is_running = False
        self.output_file = "/tmp/iperf_output.json"

    def start_iperf_server(self, config: Dict[str, Any]) -> bool:
        """Start iperf3 server"""
        try:
            cmd = [
                "iperf3",
                "-s",
                "-p", str(config['port']),
                "-J"  # JSON output
            ]

            if config.get('protocol') == 'udp':
                cmd.extend(["-u"])

            if config.get('bandwidth'):
                cmd.extend(["-b", config['bandwidth']])

            logger.info(f"Starting iperf3 server: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=open(self.output_file, 'w'),
                stderr=subprocess.PIPE,
                text=True
            )

            self.is_running = True
            return True
        except Exception as e:
            logger.error(f"Failed to start iperf3 server: {e}")
            return False

    def start_iperf_client(self, config: Dict[str, Any]) -> bool:
        """Start iperf3 client"""
        try:
            cmd = [
                "iperf3",
                "-c", config['server_address'],
                "-p", str(config['port']),
                "-t", str(config['duration']),
                "-J"  # JSON output
            ]

            if config.get('protocol') == 'udp':
                cmd.extend(["-u"])
            else:
                cmd.extend(["-P", str(config.get('parallel', 1))])

            if config.get('bandwidth'):
                cmd.extend(["-b", config['bandwidth']])

            logger.info(f"Starting iperf3 client: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=open(self.output_file, 'w'),
                stderr=subprocess.PIPE,
                text=True
            )

            self.is_running = True
            return True
        except Exception as e:
            logger.error(f"Failed to start iperf3 client: {e}")
            return False

    def stop_iperf(self) -> bool:
        """Stop iperf process"""
        if self.process and self.is_running:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.is_running = False
                return True
            except Exception as e:
                logger.error(f"Error stopping iperf: {e}")
                return False
        return True

    def get_iperf_results(self) -> Optional[Dict[str, Any]]:
        """Parse iperf JSON output"""
        try:
            with open(self.output_file, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Error reading iperf output: {e}")
            return None
