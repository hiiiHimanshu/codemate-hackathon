from flask import Flask, jsonify, request
import psutil
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "running",
        "message": "API is active",
        "endpoints": [
            "/api/system/status",
            "/api/system/memory",
            "/api/system/disk",
        ]
    })

@app.route('/api/system/status', methods=['GET'])
def get_status():
    try:
        return jsonify({
            "status": "ok",
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/memory', methods=['GET'])
def get_memory():
    try:
        memory = psutil.virtual_memory()
        return jsonify({
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/disk', methods=['GET'])
def get_disk():
    try:
        disk = psutil.disk_usage('/')
        return jsonify({
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handler for all exceptions
@app.errorhandler(Exception)
def handle_error(error):
    response = {
        "error": str(error),
        "message": "An unexpected error occurred"
    }
    return jsonify(response), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
