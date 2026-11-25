import json
import time
import jwt
import requests

# Укажите правильный путь к вашему JSON-файлу с ключом
KEY_PATH = r'C:\Users\User\Downloads\authorized_key.json' 

with open(KEY_PATH, 'r') as f:
    key_data = json.load(f)

now = int(time.time())
payload = {
    'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
    'iss': key_data['service_account_id'],
    'iat': now,
    'exp': now + 3600
}
encoded_jwt = jwt.encode(
    payload,
    key_data['private_key'],
    algorithm='PS256',
    headers={'kid': key_data['id']}
)

url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
headers = {'Content-Type': 'application/json'}
data = {'jwt': encoded_jwt}

response = requests.post(url, headers=headers, json=data)
response.raise_for_status()
iam_token = response.json().get('iamToken')

print(f"Ваш IAM_TOKEN: {iam_token}")