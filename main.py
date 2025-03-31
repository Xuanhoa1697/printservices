import os
import sys
from flask import Flask, request, jsonify
import base64
from escpos.printer import Network
from io import BytesIO
from PIL import Image
import json
import subprocess
import time
import requests
from pyngrok import ngrok

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

app = Flask(__name__,
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))

@app.route('/start_ngrok', methods=['POST'])
def start_ngrok_route():
    try:
        token = request.json.get('token')
        path = request.json.get('path')
        subprocess.run([path, "config", "add-authtoken", token])
        process = subprocess.Popen([path, "http", str(5000)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Chờ một chút để ngrok khởi động
        time.sleep(2)
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = response.json()
        return jsonify({
            'success': True,
            'url': data["tunnels"][0]["public_url"]
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/')
def index():
    return '''
        <h1>Print Services Running...</h1>
        <input type="text" id="path" placeholder="Enter your path ngrok">
        <input type="password" id="token" placeholder="Enter your ngrok auth token Ngrok" value="2aCo7NQtPgzibVWzUjnKZhKytVo_3c7CGtCYaAtmvaE6XMJDr">
        <button class="btn start-btn" onclick="startNgrok()">Start Service</button>
        <button onclick="stopServer()">Stop Service</button>
        <div class="url" id="url"></div>
        <script>
            function startNgrok() {
                const token = document.getElementById('token').value;
                const path = document.getElementById('path').value;
                if (!token || !path) {
                    Alert('Please enter your ngrok auth token and path');
                    return;
                }
                document.getElementById('url').style.display = 'none';

                // Call API
                fetch('/start_ngrok', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ token: token, path: path }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    document.getElementById('url').textContent = data.url;
                    document.getElementById('url').style.display = 'block';
                })
            }
            function stopServer() {
                fetch('/shutdown', { method: 'POST' })
                .then(response => response.text())
                .then(data => alert(data))
                .catch(error => console.error(error));
            }
        </script>
    '''

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    ngrok.kill()
    if shutdown_func:
        shutdown_func()
        return "Server đang tắt..."
    else:
        os._exit(0)  # Dừng ngay lập tức nếu không có `werkzeug`
        return "Không thể dừng server!"

@app.route('/send_print', methods=['POST'])
def send_print():
    try:
        data = json.loads(request.data)
        base64_string = data['data']
        printer = Network(data['print_ip'], data['port'])
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        max_width = 576
        width_percent = max_width / float(image.size[0])
        new_height = int((float(image.size[1]) * float(width_percent)))
        image = image.resize((max_width, new_height))
        # In ảnh
        printer.image(image)
        # Cắt giấy
        printer.cut()
        # Đóng kết nối
        printer.close()

    except Exception as e:
        return {
            'msg': 'Không thành công',
            'code': 500
        }
    return {
        'msg': 'Thành công',
        'code': 200
    }

def main():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()