# -*- coding: utf-8 -*-

import json
import os

class DataHandler:
    @staticmethod
    def save_to_json(news_data, filename='news_data.json'):
        os.makedirs('data', exist_ok=True)
        file_path = os.path.join('data', filename)
        
        existing_data = DataHandler._read_existing_data(file_path)
        updated_data = DataHandler._update_news_data(existing_data, news_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)
        
        print(f"Данные успешно сохранены в {file_path}")
    
    @staticmethod
    def _read_existing_data(file_path):
        if not os.path.exists(file_path):
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []
    
    @staticmethod
    def _update_news_data(existing_data, news_data):
        for news in news_data:
            if not any(existing['url'] == news['url'] for existing in existing_data):
                existing_data.append(news)
        return existing_data 