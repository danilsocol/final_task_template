import base64
import time
from time import sleep

import xml.etree.ElementTree as ET
import jwt
import json

import requests

# Чтение закрытого ключа из JSON-файла
with open('closeKey1.json', 'r') as f:
    obj = f.read()
    obj = json.loads(obj)
    private_key = obj['private_key']
    key_id = obj['id']
    service_account_id = obj['service_account_id']

now = int(time.time())
payload = {
    'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
    'iss': service_account_id,
    'iat': now,
    'exp': now + 3600
}

# Формирование JWT.
encoded_token = jwt.encode(
    payload,
    private_key,
    algorithm='PS256',
    headers={'kid': key_id}
)

# Запись ключа в файл
with open('jwt_token.txt', 'w') as j:
    j.write(encoded_token)

# Вывод в консоль
print(encoded_token)


headers = {
    'Content-Type': 'application/json'
}
data = {
    'jwt': encoded_token
}

# Отправка POST-запроса
response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', headers=headers, json=data)
responseJson = response.json()
iam_token = responseJson.get('iamToken')

print(iam_token)

data_file = 'body.json'

# Заголовки запроса
headers = {
    'Authorization': f'Bearer {iam_token}'
}

# Чтение данных из файла
with open(data_file, 'r') as file:
    data = file.read()

    # data.query.queryText = 'Челгу'

# Отправка POST-запроса
response = requests.post(
    'https://searchapi.api.cloud.yandex.net/v2/web/searchAsync',
    headers=headers,
    data=data
)
responseJson = response.json()
request_id = responseJson.get('id')


# Вывод ответа
print(response.status_code)
print(response.json())
print(response)

while True:

    # Отправка GET-запроса
    response1 = requests.get(f'https://operation.api.cloud.yandex.net/operations/{request_id}', headers=headers)

    # Проверка успешности запроса
    response1.raise_for_status()

    responseReq = response1.json().get('response')

    if responseReq:
        raw_data = responseReq.get('rawData')
        # Кодирование rawData в Base64
        encoded_data = base64.b64encode(raw_data).decode()

        # Создание XML-документа
        root = ET.Element("data")
        data_element = ET.SubElement(root, "rawData")
        data_element.text = encoded_data

        # Запись XML-документа в файл
        tree = ET.ElementTree(root)
        tree.write("raw_data.xml", encoding='utf-8', xml_declaration=True)

        print(f'Raw data успешно записана в файл raw_data.xml')
    else:
        print(f'rawData не найдена в ответе')

    # Вывод ответа в формате JSON
    print(f'Response: {response1.json()}')

    sleep(5)

# Вывод ответа в формате JSON
print(f'Response True: {response1.json()}')
