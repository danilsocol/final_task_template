import json
import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
import uuid
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List
from datetime import datetime

from helpers.researchAPIv1 import fetch_yandex_search_results, parse_xml_data
from models.news_item import NewsItem
from models.search import SearchResult
from parser.news_parser import NewsParser
from models.message import Message, ChatMessage, ChatHistory, ChatHistoryForModel
from models.local_ml import MLModel

# Константы
MAX_HISTORY_LENGTH = 10
MAX_SESSION_AGE = timedelta(hours=24)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ml_model = MLModel()

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await asyncio.to_thread(ml_model.initialize)
        yield
    finally:
        ml_model.cleanup()


app = FastAPI(lifespan=lifespan)

async def generate_response_with_timeout(messages: List[ChatMessage]) -> str:
    try:
        response = await asyncio.to_thread(ml_model.generate_response, messages)
        return response
        
    except Exception as e:
        logger.error(f"Ошибка при генерации ответа: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

chat_histories: Dict[str, ChatHistory] = {}  # История для UI
model_histories: Dict[str, ChatHistoryForModel] = {}  # История для модели

async def cleanup_old_sessions():
    current_time = datetime.now()
    expired_sessions = [
        session_id for session_id, history in chat_histories.items()
        if (current_time - history.last_activity) > MAX_SESSION_AGE
    ]
    for session_id in expired_sessions:
        del chat_histories[session_id]
    logger.info(f"Очищено {len(expired_sessions)} неактивных сессий")

async def run_parser_async():
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(executor, run_parser)
        except Exception as e:
            print(f"Ошибка при парсинге: {str(e)}")

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

@app.post("/chat")
async def chat(message: Message, session_id: Optional[str] = None):
    try:
        await cleanup_old_sessions()
        
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Создание новой сессии: {session_id}")
            history = ChatHistoryForModel(messages=[], session_id=session_id)
            model_histories[session_id] = history
        else:
            history = model_histories.get(session_id)
            if not history:
                history = ChatHistoryForModel(messages=[], session_id=session_id)
                model_histories[session_id] = history
        
        logger.info(f"Количество сообщений в истории: {len(history.messages)}")
        history.update_activity()
        
        # Добавляем сообщение пользователя
        user_message = ChatMessage(role="user", content=message.text)
        history.messages.append(user_message)
        print(history.messages)
        # Генерируем ответ
        response = await ml_model.generate_response(history.messages)
        # Добавляем сообщение пользователя
        # Добавляем ответ ассистента в историю
        assistant_message = ChatMessage(role="assistant", content=response)
        history.messages.append(assistant_message)
        # Генерируем ответ
        return {
            "response": response,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Ошибка в чате: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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