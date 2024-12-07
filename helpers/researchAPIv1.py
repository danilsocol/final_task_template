import base64

import xml.etree.ElementTree as ET
from http.client import HTTPException

import requests



url_api = f"https://yandex.ru/search/xml"
default_params  = {
    "folderid": "b1gkt9gihidtbvm78blg",
    "apikey": "AQVNwIPBbpnUTJLNxEogsr3jw4ZVgHu3_SCCvyL5",
    "query": "Челгу",
    "lr": "56",
    "l10n": "ru",
    "sortby": "rlv",
    "filter": "none",
    "maxpassages": "1",
    "groupby": "attr,,doc",
    "page": "0"
}


def parse_xml_data(xml_string):
    try:
        root = ET.fromstring(xml_string)
        results = []

        for doc in root.findall('.//doc'):
            url = doc.find('url').text
            title_element = doc.find('title')
            title = ''.join(title_element.itertext()) if title_element is not None else None
            headline_element = doc.find('headline')
            headline_element = ''.join(headline_element.itertext()) if headline_element is not None else None
            headline = headline_element if headline_element is not None else None

            results.append({
                'headline': headline,
                'url': url,
                'title': title,
            })

        return results

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к Яндексу: {str(e)}")


def fetch_yandex_search_results(query: str):
    try:
        params = default_params.copy()
        params["query"] = query
        response = requests.get(url_api, params=params)
        response.raise_for_status()

        with open('output.xml', 'w', encoding='utf-8') as file:
            file.write(response.text)

        return response.text
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к Яндексу: {str(e)}") from e
