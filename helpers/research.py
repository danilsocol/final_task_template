import requests

iam_token = 'eyJhbGciOiJQUzI1NiIsImtpZCI6ImFqZWZzZWxyN3JlbTY3dnZsMDA1IiwidHlwIjoiSldUIn0.eyJhdWQiOiJodHRwczovL2lhbS5hcGkuY2xvdWQueWFuZGV4Lm5ldC9pYW0vdjEvdG9rZW5zIiwiaXNzIjoiYWplcnQ5Y2s2dDRsbzg5MmdranIiLCJpYXQiOjE3MzMzMjY5MTcsImV4cCI6MTczMzMzMDUxN30.CwBkXTmIx2HcTvU7JlwovqR5lFM2DU5TG0SqKIcubEGVCQNedTD1TqPRnYnn16zfwOIQ9S9rNoUzg1zJwCMpHNKzlzERSm1WuzeI6_XWxN84wnfPZxXt4OpERUw4vxXOqo54ubawkohVv7a3iS4mT3nMKlF09CvrgCdD6Y8oa72CCt0tPje-tEKryawpu5XYKDTgEh_JzMGSPMSKKXjKzGxZpe-ruOHdiF1YkXSALO40bnTgw8M0Lh20fw3Pxdbf6BF4VxAg2eUph-LeHxvm8kJy8byC5wJ1OmeGzRrspASF61jTd5RI6uBMFFJTYhW6UgUH0XcsB1duB5BwRSP5MQ'

data_file = 'body.json'

# Заголовки запроса
headers = {
    'Authorization': f'Bearer {iam_token}',
    'Content-Type': 'application/json'
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

# Вывод ответа
print(response.status_code)
print(response.json())