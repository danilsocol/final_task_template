from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

from models.news_item import NewsItem

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Данные новостей
data = {
    'Студентка журфака ЧелГУ — в тройке лучших спортивных журналистов страны': {
        'date': '03.12.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/akimova.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    },
    'Психологи ЧелГУ создали биопсихосоциальную модель здоровья лиц, перенёсших COVID-19': {
        'date': '03.12.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/psihologi0312.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    },
    'Спортсменов ЧелГУ наградили на ежегодном празднике «Звёзды студенческого спорта»': {
        'date': '03.12.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/sport0312.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    },
    'Учёные из Китая стали участниками семинара по передовому материаловедению в ЧелГУ': {
        'date': '02.12.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/kitay02121.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    },
    'Учёные ЧелГУ выступили на XV Гороховских чтениях': {
        'date': '02.12.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/gorohovskiechteniya.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    },
    'Студенты ЧелГУ провели квиз для фанатов фильмов, сериалов, видеоигр': {
        'date': '02.12.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/fankviz02121.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    },
    'Юбилей празднует директор института экономики отраслей, бизнеса и администрирования Юнер Капкаев': {
        'date': '30.11.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/kapkaev3011.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    },
    'Учёные ЧелГУ под эгидой Уральского НОЦ работают с предприятиями региона': {
        'date': '29.11.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/nots2911.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    },
    'В ЧелГУ написали географический диктант': {
        'date': '29.11.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/diktantgeo.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    },
    'Студентка ЧелГУ — бронзовый призёр соревнований по конькобежному спорту': {
        'date': '29.11.2024',
        'relate_image_link': 'https://www.csu.ru/PublishingImages/news/news/sapegina.jpg',
        'description': 'В будущем, когда Тимур все сделает здесь будет много текста'
    }
}

@app.get("/api/news", response_model=List[NewsItem])
async def get_news():
    news_list = []
    for title, details in data.items():
        news_list.append(NewsItem(
            title=title,
            date=details['date'],
            relate_image_link=details['relate_image_link'],
            description=details['description']
        ))
    return news_list



@app.get("/")
def index():
    return HTMLResponse(content=open("index.html", "r", encoding="utf-8").read())