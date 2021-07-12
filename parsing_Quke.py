"""Модуль производит парсер сайта Quke, раздел видеокард и отправляет все новые позиции на почту
Для настройки фильтров можете выбрать необходимые фильтры на сайте и вставить в переменную FIRST_PARSING_PAGE"""
import logging
import requests
from bs4 import BeautifulSoup
from pony.orm import db_session
from models import QukeURL
from send_messang import send_massage
from fake_useragent import UserAgent
import time

USER_AGENT = UserAgent().chrome
MAIN_URL = "https://quke.ru/shop"
FIRST_PARSING_PAGE = 'https://quke.ru/shop/komplektuushie-dlya-pk/videokarty?availability=instock&pfrom=' \
                     '30000&pto=70000&c%5B491%5D%5Bfrom%5D=&c%5B491%5D%5Bto%5D=&c%5B492%5D%5Bfrom%5D=&c%5B' \
                     '492%5D%5Bto%5D=&c%5B493%5D%5Bfrom%5D=&c%5B493%5D%5Bto%5D=&order=desc-popular'


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
        video_cards_info = html_doc.find_all("div", {"class": "catalog2__content-col"})
        self.parsing_page(video_cards_info=video_cards_info)

    def parsing_page(self, video_cards_info):
        for video_card_info in video_cards_info:
            teg_a = video_card_info.find("a", {"class": "b-card2__buy add-to-cart"})
            price = teg_a.get("data-price")
            name = teg_a.get("data-title")
            href = teg_a.get("href")
            url = MAIN_URL + href
            video_card_in_bd = QukeURL.get(url=url)
            if not video_card_in_bd:
                self.send_mail(url, name, price)
                QukeURL(url=url, name=name, price=price)

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
