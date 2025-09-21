from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "CodeMate API is running",
        "version": "1.0.0",
        "endpoints": [
            "/",
            "/health",
            "/info"
        ]
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": "2025-09-21"
    })

@app.route('/info')
def info():
    return jsonify({
        "name": "CodeMate API",
        "version": "1.0.0",
        "author": "Himanshu Gupta",
        "repository": "https://github.com/hiiiHimanshu/codemate-hackathon"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


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
