from flask import Flask, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

target_url = 'https://zksync2-mainnet.zksync.io'
headers = {'Content-Type': 'application/json'}


@app.route('/', methods=['POST'])
def proxy_request():
    payload = request.get_json()
    if 'Proxy' in request.headers:
        response = requests.post(target_url, json=payload, proxies={
                                 'http': request.headers['Proxy'], 'https': request.headers['Proxy']}, headers=headers)
    else:
        response = requests.post(target_url, json=payload, headers=headers)
    return response.text, response.status_code


@app.route('/', methods=['GET'])
def get_proxy_external_ip():
    try:
        session = requests.Session()
        if 'Proxy' in request.headers:
            session.proxies = {
                'http': request.headers['Proxy'],
                'https': request.headers['Proxy']
            }
        response = session.get('http://httpbin.org/ip')

        if response.status_code == 200:
            return response.json()['origin']
        else:
            return 'Ошибка при запросе к httpbin.org'
    except requests.RequestException:
        return 'Ошибка при подключении к прокси-серверу'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
