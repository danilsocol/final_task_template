import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from models.message import ChatMessage
from typing import List, Optional
import logging
import gc
from dataclasses import dataclass
from helpers.researchAPIv1 import fetch_yandex_search_results, parse_xml_data

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 1024
    context_window: int = 2048
    model_id: str = "mistralai/Mistral-7B-Instruct-v0.3"

class MLModel:
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self._is_initialized = False
        self.chat_template = None
        
    def initialize(self):
        try:
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA недоступна")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_id)
            if self.tokenizer.pad_token_id is None:
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            
            self.chat_template = self.tokenizer.chat_template
                
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_id,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            self._is_initialized = True
            logger.info("Модель успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка при инициализации модели: {str(e)}")
            raise

    async def generate_search_query(self, user_message: str) -> str:
        """Генерирует поисковый запрос на основе сообщения пользователя"""
        try:
            system_prompt = ChatMessage(
                role="system",
                content="""You are a public relations manager at Chelyabinsk State University. 
                Your task is: 
                1. Answer questions about the university and its programs 
                2. Use mainly Russian language 
                3. Be polite and professional 
                4. Provide accurate information 
                5. If necessary, clarify the details of the issue
                6. Include relevant links from the provided context in your response
                7. Keep responses short and structured
                
                Response format:
                - Do not use the prefixes 'user:' or 'bot:'
                - Respond in a structured way
                - Use the official communication style
                - Include relevant links when available
                - Do not repeat the same information"""
            )
            user_prompt = ChatMessage(
                role="user",
                content=f"Сформулируйте поисковый запрос для вопроса: {user_message}"
            )
            
            inputs = self.tokenizer.apply_chat_template(
                [system_prompt, user_prompt],
                add_generation_prompt=True,
                return_tensors="pt"
            )
            input_length = inputs.shape[1]
            
            attention_mask = torch.ones_like(inputs)
            inputs = inputs.to(self.model.device)
            attention_mask = attention_mask.to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_new_tokens=30,  # Ограничиваем длину запроса
                    temperature=0.1,    # Делаем генерацию более детерминированной
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    repetition_penalty=1.2,
                    no_repeat_ngram_size=2,
                    use_cache=True
                )
            
            query = self.tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
            logger.info(f"Сгенерированный поисковый запрос: {query}")
            
            return query.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при генерации поискового запроса: {str(e)}")
            return f"ЧелГУ {user_message[:50]}" 

    async def get_search_context(self, user_message: str) -> str:
        try:
            search_query = await self.generate_search_query(user_message)
            xml = fetch_yandex_search_results(search_query)
            results = parse_xml_data(xml)
            
            context = "Релевантные источники:\n"
            for result in results[:3]:
                # Очищаем URL от пробелов и лишних символов
                clean_url = result['url'].strip().replace(" ", "")
                context += f"- {result['title']}\n  Ссылка: {clean_url}\n"
                if result['headline']:
                    context += f"  Краткое содержание: {result['headline']}\n"
            
            return context
        except Exception as e:
            logger.error(f"Ошибка при получении контекста поиска: {str(e)}")
            return ""

    async def generate_response(self, messages: List[ChatMessage]) -> str:
        if not self._is_initialized:
            logger.error("Попытка использовать неинициализированную модель")
            raise RuntimeError("Модель не инициализирована")

        try:
            user_message = messages[-1].content
            search_context = await self.get_search_context(user_message)
            logger.info(f"Получен поисковый контекст: {search_context}")
            
            system_message = ChatMessage(
                role="system",
                content=f"""Вы - менеджер по связям с общественностью Челябинского государственного университета. 
                
                Используйте следующую информацию при ответе:
                {search_context}
                
                Формат ответа:
                1. Дайте краткий и информативный ответ на вопрос пользователя
                2. Не включайте ссылки в ответ, они будут добавлены автоматически
                3. Используйте только достоверную информацию из контекста"""
            )
            
            messages_with_context = [system_message] + messages
            
            inputs = self.tokenizer.apply_chat_template(
                messages_with_context,
                add_generation_prompt=True,
                return_tensors="pt"
            )
            
            input_length = inputs.shape[1]
            attention_mask = torch.ones_like(inputs)
            inputs = inputs.to(self.model.device)
            attention_mask = attention_mask.to(self.model.device)

            with torch.no_grad():
                logger.info("Начало генерации")
                outputs = self.model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_new_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    repetition_penalty=1.2,
                    no_repeat_ngram_size=3,
                    use_cache=True
                )
                logger.info("Генерация завершена")
            
            response = self.tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
            
            # Добавляем релевантные источники к ответу
            final_response = f"{response.strip()}\n{search_context}"
            print(f'Что должен видеть пользователь: {final_response}')
            return final_response
                
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {str(e)}")
            raise
        
    def cleanup(self):
        try:
            if self.model:
                self.model.cpu()
                del self.model
            if self.tokenizer:
                del self.tokenizer
            self._is_initialized = False
            torch.cuda.empty_cache()
            gc.collect()
            logger.info("Ресурсы модели успешно очищены")
        except Exception as e:
            logger.error(f"Ошибка при очистке ресурсов модели: {str(e)}")