import base64

import requests

apiKey = "AQVNwIPBbpnUTJLNxEogsr3jw4ZVgHu3_SCCvyL5"
query = "Chelgy"

url = f"https://yandex.ru/search/xml"
params = {
    "folderid": "b1gkt9gihidtbvm78blg",
    "apikey": apiKey,
    "query": query,
    "lr": "56",
    "l10n": "ru",
    "sortby": "rlv",
    "filter": "none",
    "maxpassages": "1",
    "groupby": "attr,,doc",
    "page": "0"
}
response = requests.get(url, params=params)
print(response)
print(response.text)

response.raise_for_status()

with open('output1.xml', 'w', encoding='utf-8') as file:
    file.write(response.text)
