from flask import Flask, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

target_url = 'https://zksync2-mainnet.zksync.io'
headers = {'Content-Type': 'application/json'}

MAX_RETRIES = 3

def send_request(payload):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            if 'Proxy' in request.headers:
                response = requests.post(target_url, json=payload, proxies={'http': request.headers['Proxy'], 'https': request.headers['Proxy']}, headers=headers)
            else:
                response = requests.post(target_url, json=payload, headers=headers)

            response.raise_for_status()  # Генерирует исключение, если получен некорректный статусный код
            return response.text, response.status_code

        except requests.RequestException:
            retry_count += 1

    return 'Ошибка при отправке запроса', 500


@app.route('/', methods=['POST'])
def proxy_request():
    payload = request.get_json()
    response_text, response_status = send_request(payload)
    return response_text, response_status


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
