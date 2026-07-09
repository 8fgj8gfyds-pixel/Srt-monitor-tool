#!/usr/bin/env python3
"""
Report Generator - Creates PDF and CSV reports from statistics
"""

import os
import json
import csv
from datetime import datetime
from typing import Dict, Any, List
import logging
from fpdf import FPDF
import matplotlib.pyplot as plt
import io

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, output_dir: str = "/var/lib/srt-monitor/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_pdf_report(self, stats_data: List[Dict[str, Any]], filename: str = None) -> str:
        """Generate PDF report from statistics data"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"srt_report_{timestamp}.pdf"

        filepath = os.path.join(self.output_dir, filename)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.cell(200, 10, txt="SRT Monitoring System Report", ln=1, align="C")
        pdf.cell(200, 10, txt=f"Generated: {datetime.now().isoformat()}", ln=1, align="C")
        pdf.ln(10)

        # Summary statistics
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt="Summary Statistics", ln=1)
        pdf.set_font("Arial", size=10)

        # Create throughput graph
        throughput_data = [(s['timestamp'], s['srt'].get('throughput', 0)) for s in stats_data]
        graph_path = self._create_throughput_graph(throughput_data)
        pdf.image(graph_path, x=10, y=None, w=180)
        os.remove(graph_path)

        # Save PDF
        pdf.output(filepath)
        logger.info(f"PDF report generated: {filepath}")
        return filepath

    def generate_csv_report(self, stats_data: List[Dict[str, Any]], filename: str = None) -> str:
        """Generate CSV report from statistics data"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"srt_report_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 'datetime',
                'srt_status', 'srt_throughput', 'srt_packet_loss',
                'iperf_bandwidth', 'iperf_jitter', 'cpu_usage', 'memory_usage'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for stat in stats_data:
                writer.writerow({
                    'timestamp': stat['timestamp'],
                    'datetime': stat['datetime'],
                    'srt_status': stat['srt'].get('status', 'N/A'),
                    'srt_throughput': stat['srt'].get('throughput', 0),
                    'srt_packet_loss': stat['srt'].get('packet_loss', 0),
                    'iperf_bandwidth': stat['iperf'].get('bandwidth', 0),
                    'iperf_jitter': stat['iperf'].get('jitter', 0),
                    'cpu_usage': stat['system'].get('cpu_usage', 0),
                    'memory_usage': stat['system'].get('memory_usage', 0)
                })

        logger.info(f"CSV report generated: {filepath}")
        return filepath

    def _create_throughput_graph(self, data: List[tuple]) -> str:
        """Create throughput graph image"""
        timestamps = [d[0] for d in data]
        values = [d[1] for d in data]

        plt.figure(figsize=(10, 4))
        plt.plot(timestamps, values, label='Throughput (Mbps)')
        plt.title('SRT Throughput Over Time')
        plt.xlabel('Time')
        plt.ylabel('Throughput (Mbps)')
        plt.grid(True)
        plt.legend()

        img_path = "/tmp/throughput_graph.png"
        plt.savefig(img_path)
        plt.close()

        return img_path
