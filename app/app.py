# Check /app/app.py for these common issues:

# ISSUE 1: Missing imports
import os
import pandas as pd
from flask import Flask, render_template, jsonify, request
import subprocess
import json
from datetime import datetime

# ISSUE 2: Port conflict - change from 5000 to avoid conflicts
app = Flask(__name__, static_folder='static')

# ISSUE 3: Add proper error handling
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Use port 5001 to avoid conflicts
    app.run(host='0.0.0.0', port=5001, debug=False)
