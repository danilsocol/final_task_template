import json
import os
from http.client import HTTPException
import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Request, requests, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

from helpers.researchAPIv1 import fetch_yandex_search_results, parse_xml_data
from models.news_item import NewsItem
from models.search import SearchResult, SearchRequest
from parser.news_parser import NewsParser

def load_news_data():
    try:
        with open('data/news_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def parse_arguments():
    parser = argparse.ArgumentParser(description='Запуск FastAPI сервера с опцией парсинга новостей')
    parser.add_argument('--parse', action='store_true', help='Запустить парсер новостей при старте, автозапуск парсинга 5 первых страниц за 2024 год')
    parser.add_argument('--pages', type=str, 
                       default='5', 
                       help='Количество страниц для парсинга (по умолчанию 5), None для бесконечного парсинга')    
    args = parser.parse_args()
    
    if args.pages.lower() == 'none':
        args.pages = None
    else:
        try:
            args.pages = int(args.pages)
        except ValueError:
            raise ValueError("Значение --pages должно быть числом или 'None'")
    
    return args

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/news", response_model=List[NewsItem])
async def get_news():
    news_data = load_news_data()
    news_list = []
    
    for item in news_data:
        news_list.append(NewsItem(
            title=item['title'],
            date=item['date'],
            relate_image_link=item['relate_image'],
            description=item.get('content', 'Описание отсутствует')
        ))
    return news_list

@app.get("/search", response_model=list[SearchResult])
async def search(query: str = Query(...)):
    try:
        xml = fetch_yandex_search_results(query)
        results = parse_xml_data(xml)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {str(e)}")

@app.get("/")
def index():
    return HTMLResponse(content=open("index.html", "r", encoding="utf-8").read())

if __name__ == "__main__":
    args = parse_arguments()
    
    def run_parser():
        if args.parse:
            print(f"Запуск парсера новостей (страниц: {args.pages})...")
            parser = NewsParser(max_pages=args.pages)
            try:
                parser.parse_news()
            except Exception as e:
                print(f"Ошибка при парсинге: {str(e)}")
            finally:
                parser.driver.quit()
    
    # Запускаем парсер в отдельном потоке
    with ThreadPoolExecutor() as executor:
        parser_future = executor.submit(run_parser)
        
        # Запускаем FastAPI сервер в основном потоке
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)