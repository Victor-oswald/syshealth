from flask import Flask, request, jsonify
import uuid
from cryptography.fernet import Fernet

app = Flask(__name__)

device_keys = {}

@app.route('/register_device', methods=['POST'])
def register_device():
    device_id = request.json['device_id']
    if device_id not in device_keys:
        key = Fernet.generate_key()
        device_keys[device_id] = key
        return jsonify({'status': 'success', 'key': key.decode('utf-8')})
    else:
        return jsonify({'status': 'error', 'message': 'Device already registered'})

@app.route('/get_key', methods=['POST'])
def get_key():
    device_id = request.json['device_id']
    if device_id in device_keys:
        return jsonify({'status': 'success', 'key': device_keys[device_id].decode('utf-8')})
    else:
        return jsonify({'status': 'error', 'message': 'Device not registered'})

if __name__ == '__main__':
    app.run(debug=True)
