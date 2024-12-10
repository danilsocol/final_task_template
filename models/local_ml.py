import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from models.message import ChatMessage
from typing import List, Optional
import logging
import gc
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field
import asyncio
from fastapi import HTTPException
from tqdm import tqdm

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 500
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

    def generate_response(self, messages: List[ChatMessage]) -> str:
        if not self._is_initialized:
            logger.error("Попытка использовать неинициализированную модель")
            raise RuntimeError("Модель не инициализирована")

        try:
            # Получаем длину входного контекста
            inputs = self.tokenizer.apply_chat_template(
                messages,
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
                    no_repeat_ngram_size=3
                )
                logger.info("Генерация завершена")
            
            # Декодируем только новые токены, отбрасывая входной контекст
            response = self.tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
            logger.info(f"Новый ответ от модели: {response}")
            
            return response.strip()

            
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