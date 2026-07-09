from flask import Flask, render_template, jsonify, request, send_file
import os
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)
app.config.from_pyfile('config.py')

# In-memory stats storage
stats_data = {
    'timestamp': [],
    'throughput': [],
    'bandwidth': [],
    'dropped_packets': [],
    'lost_packets': [],
    'retransmitted': [],
    'out_of_order': [],
    'latency': []
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'stats': stats_data,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        config_data = request.json
        # Save configuration
        with open(os.path.join(app.config['DATA_DIR'], 'config.json'), 'w') as f:
            json.dump(config_data, f)
        return jsonify({'status': 'success'})
    else:
        # Load configuration
        config_path = os.path.join(app.config['DATA_DIR'], 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({
            'srt_mode': False,
            'buffer_size': 1000,
            'payload_size': 1316,
            'latency': 120,
            'port': 9000
        })

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
