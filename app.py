from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Function to check the site based on the provided script logic
def check_site(url):
    # Replace this with the actual script logic for checking the site
    result = {
        "url": url,
        "gateway_status": "OK",           # Example status
        "cloudflare_status": "Active",    # Example status
        "captcha_status": "None"          # Example status
    }
    return result

@app.route('/check', methods=['POST'])
def check():
    data = request.json
    urls = data.get("urls", [])
    results = [check_site(url) for url in urls]
    return jsonify({"results": results})

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    urls = file.read().decode('utf-8').splitlines()
    results = [check_site(url) for url in urls]
    return jsonify({"results": results})

if __name__ == '__main__':
    # Bind to the port specified by the environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
