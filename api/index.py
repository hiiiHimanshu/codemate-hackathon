from flask import Flask, jsonify, request
import psutil
from core.router import CommandRouter
from core.registry import CommandRegistry
from core.session import SessionContext
from fs.ops import (
    pwd_handler, cd_handler, ls_handler, mkdir_handler,
    rm_handler, mv_handler, cp_handler, touch_handler, cat_handler
)
from monitor.stats import cpu, mem, disk

app = Flask(__name__)

# Initialize the command registry and router
registry = CommandRegistry()
router = CommandRouter(registry)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "message": "API is active",
        "endpoints": [
            "/api/system/cpu",
            "/api/system/memory",
            "/api/system/disk",
            "/api/fs/pwd",
            "/api/fs/ls",
            "/api/fs/cd",
            "/api/fs/mkdir",
            "/api/fs/touch",
            "/api/fs/rm",
            "/api/fs/mv",
            "/api/fs/cp",
            "/api/fs/cat"
        ]
    })

@app.route('/api/system/cpu')
def get_cpu():
    return jsonify(cpu())

@app.route('/api/system/memory')
def get_memory():
    return jsonify(mem())

@app.route('/api/system/disk')
def get_disk():
    return jsonify(disk())

@app.route('/api/fs/pwd')
def get_pwd():
    return jsonify(pwd_handler())

@app.route('/api/fs/ls')
def get_ls():
    path = request.args.get('path', '.')
    return jsonify(ls_handler(path))

@app.route('/api/fs/cd', methods=['POST'])
def post_cd():
    data = request.get_json()
    path = data.get('path', '.')
    return jsonify(cd_handler(path))

@app.route('/api/fs/mkdir', methods=['POST'])
def post_mkdir():
    data = request.get_json()
    path = data.get('path')
    if not path:
        return jsonify({"error": "Path is required"}), 400
    return jsonify(mkdir_handler(path))

@app.route('/api/fs/touch', methods=['POST'])
def post_touch():
    data = request.get_json()
    path = data.get('path')
    if not path:
        return jsonify({"error": "Path is required"}), 400
    return jsonify(touch_handler(path))

@app.route('/api/fs/rm', methods=['DELETE'])
def delete_rm():
    data = request.get_json()
    path = data.get('path')
    recursive = data.get('recursive', False)
    if not path:
        return jsonify({"error": "Path is required"}), 400
    return jsonify(rm_handler(path, recursive))

@app.route('/api/fs/mv', methods=['POST'])
def post_mv():
    data = request.get_json()
    src = data.get('src')
    dst = data.get('dst')
    if not src or not dst:
        return jsonify({"error": "Source and destination paths are required"}), 400
    return jsonify(mv_handler(src, dst))

@app.route('/api/fs/cp', methods=['POST'])
def post_cp():
    data = request.get_json()
    src = data.get('src')
    dst = data.get('dst')
    recursive = data.get('recursive', False)
    if not src or not dst:
        return jsonify({"error": "Source and destination paths are required"}), 400
    return jsonify(cp_handler(src, dst, recursive))

@app.route('/api/fs/cat')
def get_cat():
    path = request.args.get('path')
    if not path:
        return jsonify({"error": "Path is required"}), 400
    return jsonify(cat_handler(path))

if __name__ == '__main__':
    app.run()
