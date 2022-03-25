from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import math
from pymongo import MongoClient
from pymongo.errors import *


class Dz5:
    def start(self):
        data = self.get_source_data()
        if not data:
            print('Не получены товары')
            return

        client = MongoClient('localhost', 27017)
        db = client['dz_database']
        mvideo_products = db.mvideo_products
        self.data_insert(mvideo_products, data)

    def data_insert(self, table_name, data):
        for row in data:
            index = {'_id': row['product']}
            row = index | row
            try:
                table_name.insert_one(row)
            except DuplicateKeyError as e:
                print(row['_id'] + ' дублирующийся ключ')

    def get_source_data(self):
        results = []
        start_url = 'https://www.mvideo.ru/'
        driver = webdriver.Chrome(executable_path='./chromedriver.exe')
        driver.get(start_url)

        button_selector = 'main.layout__content mvid-shelf-group.ng-star-inserted ' \
                          'mvid-switch-shelf-tab-selector.ng-star-inserted div.mvid-carousel-inner button '
        elems = driver.find_elements(By.CSS_SELECTOR, button_selector)
        if not elems:
            page_height = driver.execute_script('return document.body.scrollHeight')
            window_height = driver.execute_script('return document.documentElement.clientHeight')
            chunk_page = math.ceil(page_height / window_height)
            scroll_height = 0
            for i in range(chunk_page):
                scroll_height += window_height
                driver.execute_script('window.scroll(0, ' + str(scroll_height) + ')')
                time.sleep(5)
                elems = driver.find_elements(By.CSS_SELECTOR, button_selector)
                if elems and len(elems) > 1:
                    break

        if len(elems) < 1:
            print('Не найден элемент на странице')
            return results

        elems[1].click()
        time.sleep(5)
        cards = driver.find_elements(By.CSS_SELECTOR,
                                     'mvid-carousel.carusel mvid-product-cards-group div.product-mini-card__name')
        if not cards:
            print('Не найдены элементы товаров на странице')
            return results

        for card in cards:
            value = str(card.text)
            if value:
                single_data = {
                    'product': value,
                }

                results.append(single_data)

        driver.quit()
        return results


parser = Dz5()
parser.start()
