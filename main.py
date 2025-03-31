import os
import sys
from flask import Flask, request
import base64
from escpos.printer import Network
from io import BytesIO
from PIL import Image
import json

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

app = Flask(__name__,
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))

@app.route('/')
def index():
    return '''
        <p>Print Services Running...</p>
        <button onclick="stopServer()">Stop Service</button>
        <script>
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