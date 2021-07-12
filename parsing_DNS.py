"""Модуль производит парсер сайта ситилинк, раздел видеокард и отправляет все новые позиции на почту
Для настройки фильтров можете выбрать необходимые фильтры на сайте и вставить в переменную DNS"""
from pony.orm import db_session
from selenium import webdriver
import os
from models import DNSModels
from send_messang import send_massage
from multiprocessing import Pool
import logging
import time

MAIN_URL = "https://www.dns-shop.ru/"
FIRST_PARSING_PAGE = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?p=1'
BASE_DIRE = os.path.dirname(os.path.abspath(__file__))
CHROME_DRIVER = os.path.join(BASE_DIRE, "chrome") + '\chromedriver.exe'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"\
             " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


class Parsing:
    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.option.add_argument("--disable-blink-features=AutomationControlled")
        self.option.add_argument("--headless")
        self.option.add_argument(f"user-agent={USER_AGENT}")
        self.page_count = int()
        self.items = []
        self.pages_url = []

    def run(self):
        while True:
            self.give_page_count()
            self.create_pages_url()
            p = Pool(self.page_count)
            p.map(self.give_info_with_page, self.pages_url)
            self.write_to_bd()
            time.sleep(120)

    def give_page_count(self):
        """Заполняет self.page_count количество страниц"""
        try:
            driver = webdriver.Chrome(executable_path=CHROME_DRIVER, options=self.option)
            driver.get(FIRST_PARSING_PAGE)
            driver.implicitly_wait(5)
            self.page_count = int(driver.find_elements_by_class_name('pagination-widget__page ')[-1].
                                  get_attribute('data-page-number'))
        except Exception as ex:
            print(ex)
        finally:
            driver.close()
            driver.quit()

    def create_pages_url(self):
        for number_page in range(1, self.page_count + 1):
            self.pages_url.append(FIRST_PARSING_PAGE[:-1] + str(number_page))

    def give_info_with_page(self, url=FIRST_PARSING_PAGE):
        try:
            driver = webdriver.Chrome(executable_path=CHROME_DRIVER, options=self.option)
            driver.get(url)
            driver.implicitly_wait(5)
            items = driver.find_elements_by_xpath("//div[@data-id='product']")
            for item in items:
                try:
                    name_item = item.find_element_by_class_name("catalog-product__name").text
                except:
                    name_item = "Нет имени"
                try:
                    href = item.find_element_by_class_name("catalog-product__name").get_attribute("href")
                except:
                    href = "Нет ссылки"
                try:
                    price_item = item.find_element_by_class_name("product-buy__price").text.replace(" ", '')[:-1]
                except:
                    price_item = "Нет цены"
                item_info = {"url": href,
                             "name": name_item,
                             "price": price_item}
                self.items.append(item_info)
        except Exception as ex:
            print(ex)
        finally:
            driver.close()
            driver.quit()

    @db_session
    def write_to_bd(self):
        for item in self.items:
            url = item["url"]
            name = item["name"]
            price = item["price"]
            item_in_db = DNSModels.get(url=url)
            if not item_in_db:
                self.send_mail(url, name, price)
                DNSModels(url=url, name=name, price=price)
            else:
                if item_in_db.price != price:
                    self.send_mail(url, name, price)
                    DNSModels(url=url, name=name, price=price)


    def send_mail(self, url, name, price):
        massage = f"NEW {name}, по цене {price}, адрес {url}"
        topic_name = f'{name} - {price}'
        send_massage(massage, topic_name)
        log.info(f'отправлено сообщение {massage}')


log = logging.getLogger("log_parsing")


def logging_configurate():
    file_handler = logging.FileHandler(filename="DNS_logging.txt", encoding="utf-8", mode="a")
    formater_for_file_write = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%d-%m-%Y %H:%M")
    file_handler.setFormatter(formater_for_file_write)
    file_handler.setLevel(logging.INFO)
    log.setLevel(logging.INFO)
    log.addHandler(file_handler)


if __name__ == "__main__":
    logging_configurate()
    parsing = Parsing()
    parsing.run()
