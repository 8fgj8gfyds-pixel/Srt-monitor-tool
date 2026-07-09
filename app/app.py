#!/usr/bin/env python3
"""
Main Application - Flask web server with Socket.IO
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging
import os
import sys
from srt_manager import SRTManager
from iperf_manager import IperfManager
from stats_collector import StatsCollector
from report_generator import ReportGenerator
import subprocess
import time

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/srt-monitor/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize managers
srt_manager = SRTManager()
iperf_manager = IperfManager()
stats_collector = StatsCollector()
report_generator = ReportGenerator()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/config')
def config():
    """Configuration page"""
    return render_template('config.html')

@app.route('/iperf')
def iperf():
    """Iperf test page"""
    return render_template('iperf.html')

@app.route('/reports')
def reports():
    """Reports page"""
    reports = os.listdir('/var/lib/srt-monitor/reports')
    reports.sort(reverse=True)
    return render_template('reports.html', reports=reports)

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('status_message', 'Connected to SRT Monitor')

@socketio.on('apply_srt_config')
def handle_apply_config(config):
    """Apply SRT configuration"""
    logger.info(f"Applying SRT config: {config}")

    # Stop any running SRT process
    if srt_manager.is_running:
        srt_manager.stop_srt()

    # Start new SRT process based on mode
    mode = config.get('srt_mode', 'listener')

    if mode == 'listener':
        success = srt_manager.start_srt_listener({
            'listener_port': int(config.get('listener_port', 1234)),
            'latency_ms': int(config.get('latency_ms', 100)),
            'payload_size': int(config.get('payload_size', 1316)),
            'max_bandwidth': int(config.get('max_bandwidth', 1000))
        })
    else:
        success = srt_manager.start_srt_caller({
            'remote_address': config.get('remote_address', '127.0.0.1'),
            'remote_port': int(config.get('remote_port', 1234)),
            'caller_port': int(config.get('caller_port', 1235)),
            'latency_ms': int(config.get('latency_ms', 100)),
            'payload_size': int(config.get('payload_size', 1316)),
            'max_bandwidth': int(config.get('max_bandwidth', 1000))
        })

    if success:
        emit('status_message', f'SRT {mode} started successfully')
    else:
        emit('status_message', 'Failed to start SRT')

@socketio.on('start_iperf_test')
def handle_start_iperf(config):
    """Start iperf test"""
    logger.info(f"Starting iperf test: {config}")

    # Stop any running iperf
    if iperf_manager.is_running:
        iperf_manager.stop_iperf()

    mode = config.get('mode', 'server')

    if mode == 'server':
        success = iperf_manager.start_iperf_server({
            'port': int(config.get('port', 5201)),
            'protocol': config.get('protocol', 'tcp')
        })
    else:
        success = iperf_manager.start_iperf_client({
            'server_address': config.get('server_address', '127.0.0.1'),
            'port': int(config.get('port', 5201)),
            'duration': int(config.get('duration', 10)),
            'protocol': config.get('protocol', 'tcp'),
            'bandwidth': config.get('bandwidth', '100M'),
            'parallel': int(config.get('parallel', 1))
        })

    if success:
        emit('status_message', f'Iperf {mode} started successfully')
    else:
        emit('status_message', 'Failed to start iperf')

@socketio.on('clear_stats')
def handle_clear_stats():
    """Clear statistics"""
    stats_collector.clear_stats()
    emit('status_message', 'Statistics cleared')

@socketio.on('save_stats')
def handle_save_stats():
    """Save statistics to report"""
    stats = stats_collector.get_stats_history()
    if stats:
        pdf_path = report_generator.generate_pdf_report(stats)
        csv_path = report_generator.generate_csv_report(stats)
        emit('status_message', f'Reports saved: {pdf_path}, {csv_path}')
    else:
        emit('status_message', 'No statistics to save')

def background_stats_collection():
    """Background thread for collecting statistics"""
    stats_collector.start_collection(interval=1.0)

    while True:
        stats = stats_collector.get_latest_stats()
        socketio.emit('stats_update', stats)
        time.sleep(1)

if __name__ == '__main__':
    # Start background thread
    import threading
    stats_thread = threading.Thread(target=background_stats_collection, daemon=True)
    stats_thread.start()

    # Start Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
