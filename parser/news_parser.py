# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

from parser.browser_config import BrowserConfig
from parser.data_handler import DataHandler

class NewsParser:
    def __init__(self, max_pages=5):
        self.url = 'https://www.csu.ru/news/'
        self.page_number = 2
        self.max_pages = max_pages
        self.driver = webdriver.Chrome(options=BrowserConfig.get_chrome_options())
        self.driver.maximize_window()

    def __del__(self):
        self.driver.quit()

    def parse_news(self):
        try:
            news_data_list = self.get_full_news_content()
            return news_data_list
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
        finally:
            self.driver.quit()

    def get_news_from_page(self):
        print(f"Получение списка новостей со страницы {self.page_number-1}...")
        try:
            if self.page_number == 2:  # Только для первого захода. И ещё в ЧелГу 1 страница это 2 :)
                self.driver.get(self.url)
            
            wait = WebDriverWait(self.driver, 100)
            news_elements = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "nlist-full"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            news_items = soup.find_all('div', class_='nlist-full')

            news_links = []
            
            if not news_items:
                print("Не найдено новостей на странице, что-то пошло не так")
                self.driver.quit()
                raise SystemExit("Программа остановлена из-за отсутствия новостей")
            
            for item in tqdm(news_items):
                links = item.find_all('a')
                for link in links:
                    relative_link = link.get('href')
                    if relative_link and 'newsitem' in relative_link:
                        full_link = 'https://www.csu.ru' + relative_link
                        news_links.append(full_link)
            
            time.sleep(1.5)
            self.go_to_news_page()
            
            return news_links
        
        except Exception as e:
            print(f"Ошибка при получении новостей: {str(e)}")
            return []
        
    def go_to_news_page(self):
        self.page_number += 1
        if self.page_number == self.max_pages:
            print("Достигнуто максимальное количество страниц, скачивание последних новостей...")
            return False
        pagination_click = self.driver.find_element(By.XPATH, 
        f'/html/body/form/div[5]/div/div[7]/div/div[1]/div[3]/div/span/div[4]/div/div/table/tbody/tr/td/div/div/div[2]/div[1]/div/div/div[2]/table/tbody/tr/td/div[2]/a[{self.page_number}]')  
        pagination_click.click()
        time.sleep(1)

        return True
    
    def get_full_news_content(self):
        all_news_data = []
        
        while True:
            news_links = self.get_news_from_page()
            if not news_links or (self.max_pages is not None and self.page_number > self.max_pages):
                break
            
            # Сохраняем handle основной вкладки
            main_window = self.driver.current_window_handle
            
            for link in tqdm(news_links):
                try:
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.get(link)
                    time.sleep(2)
                    
                    news_xpath = '//*[@id="WebPartWPQ1"]/table/tbody/tr[2]/td'
                    
                    wait = WebDriverWait(self.driver, 10)
                    news_container = wait.until(
                        EC.presence_of_element_located((By.XPATH, news_xpath))
                    )
                
                    html_content = news_container.get_attribute('innerHTML')
                    soup = BeautifulSoup(html_content, 'lxml')
                    
                    # Извлекаем заголовок
                    title = soup.find('div', class_='news-rowfield news-header')
                    title_text = title.text.strip() if title else "Заголовок не найден"
                    # Извлекаем дату
                    date = soup.find('div', class_='news-rowfield news-date')
                    date_text = date.text.strip() if date else "Дата не найдена"
                    
                    # Извлекаем текст новости
                    content = soup.find('div', class_='news-rowfield p-leader')
                    content2 = soup.find('div', class_='news-rowfield p-content')
                    content_text = content.text.strip() if content else "Текст новости не найден "
                    content_text += content2.text.strip() if content2 else "Текст новости не найден"

                    # Извлекаем ссылку на изображение
                    relate_image = soup.find('div', class_='img-container')
                    relate_image_text = relate_image.find('img')['src'] if relate_image and relate_image.find('img') else "Изображение не найдено"
                    
                    news_data = {
                        'title': title_text,
                        'date': date_text,
                        'relate_image': relate_image_text,
                        'content': content_text,
                        'url': link 
                    }
                    
                    all_news_data.append(news_data)
                    
                except Exception as e:
                    print(f"Ошибка при получении текста новости: {str(e)}")
                    continue
                finally:
                    self.driver.close()
                    self.driver.switch_to.window(main_window)
                    time.sleep(1)
            
            # Сохраняем новости после обработки каждой страницы
            if all_news_data:
                DataHandler.save_to_json(all_news_data)
        
        return all_news_data


if __name__ == '__main__':
    print("Запуск парсера Новостей ЧелГУ")
    '''
    Что бы скачать 40 новостей, нужно указать max_pages=6, 60 новостей - max_pages=8 и так далее
    '''
    parser = NewsParser(max_pages=6)
    try:
        news_data_list = parser.parse_news()
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    finally:
        parser.driver.quit()

    

