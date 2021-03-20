"""Модуль производит парсер сайта регард, раздел видеокард и отправляет все новые позиции на почту
Для настройки фильтров можете выбрать необходимые фильтры на сайте и вставить в переменную FIRST_PARSING_PAGE"""
import re
import logging
import requests
from bs4 import BeautifulSoup
from pony.orm import db_session
from models import RegardURL
from send_messang import send_massage
from fake_useragent import UserAgent
import time


USER_AGENT = UserAgent().chrome
MAIN_URL = "https://www.regard.ru"
FIRST_PARSING_PAGE = 'https://www.regard.ru/catalog/filter/?id=NDAwMDsyLDMwMDAwLTYwMDAwLA=='

class Parser:
    def __init__(self, first_parsing_page):
        self.main_url = first_parsing_page

    def run(self):
        while True:
            self.parsing()
            time.sleep(30)

    @db_session
    def parsing(self):
        responce = requests.get(self.main_url, headers={'user-agent': USER_AGENT})
        html_doc = BeautifulSoup(responce.content, features="html.parser")
        video_cards_info = html_doc.find_all("div", {"class": "block"})
        self.parsing_page(video_cards_info=video_cards_info)


    def parsing_page(self, video_cards_info):
        for video_card_info in video_cards_info:
            teg_a = video_card_info.find("a")
            teg_price = video_card_info.find("div", {"class": "price"})
            price = teg_price.text
            price = re.findall(f'\d+', price)
            price = price[0] + price[1]
            teg_img = teg_a.find('img')
            name = teg_img.get("alt")
            href = teg_a.get("href")
            url = MAIN_URL + href
            video_card_in_bd = RegardURL.get(url=url)
            if not video_card_in_bd:
                self.send_mail(url, name, price)
                RegardURL(url=url, name=name, price=price)

    def send_mail(self, url, name, price):
        massage = f"NEW {name}, по цене {price}, адрес {url}"
        topic_name = f'{name} - {price}'
        send_massage(massage, topic_name)
        log.info(f'отправлено сообщение {massage}')

    def chek_next_page(self, html_doc):
        info_page = html_doc.find("div", {"class": "PaginationWidget__wrapper-pagination"})
        teg_a = None
        if info_page:
            teg_a = info_page.find("a", {"class": "PaginationWidget__arrow PaginationWidget__arrow_right"})
        if teg_a:
            self.next_page = "p=" + teg_a.get('data-page')
            print(self.next_page)
        else:
            self.next_page = "p=1"


log = logging.getLogger('log_parsing')
def logging_configurate():
    file_handler = logging.FileHandler(filename="log_messege.txt", encoding="utf-8", mode="a")
    formater_for_file_write = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%d-%m-%Y %H:%M")
    file_handler.setFormatter(formater_for_file_write)
    file_handler.setLevel(logging.INFO)
    log.addHandler(file_handler)
    log.setLevel(logging.INFO)


if __name__ == "__main__":
    logging_configurate()
    parser = Parser(FIRST_PARSING_PAGE)
    parser.run()
