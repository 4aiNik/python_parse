import json
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as BS


class Dz2:
    main_url = 'https://rskrf.ru'

    def start(self):
        main_links = self.get_main_products_types_links()
        if not main_links:
            print('Не получены ссылки на типы продуктов питания')
            return

        input_links_types = self.get_input_products_types(main_links)
        if not input_links_types:
            print('Не выбраны ссылки на типы продуктов питания')
            return

        all_products_data = self.get_all_products_data(input_links_types)
        if not all_products_data:
            print('Нет данных')
            return

        df = pd.DataFrame(all_products_data)
        df.to_csv('dz2.csv')
        print(df)

    def get_all_products_data(self, input_links_types):
        results = []
        for link_data in input_links_types.items():
            print('Получение ссылок для: ' + link_data[0])
            current_products = self.get_products_links(link_data[1])
            if not current_products:
                continue

            for product in current_products.items():
                print('Обработка страницы: ' + product[0])
                page_data = self.get_page_data(product[1])
                if not page_data:
                    continue

                for page_item in page_data:
                    results.append(page_item)

        return results

    def get_page_data(self, url):
        results = []
        time.sleep(2)
        headers = {
            'Host': 'rskrf.ru',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return results

        dom = BS(response.text, 'html.parser')
        pattern = re.compile(r"var\s*data\s*=\s*({.+?});", re.MULTILINE | re.DOTALL)
        script = dom.find('script', text=pattern)
        json_row = pattern.search(script.text).group(1)
        if not json_row:
            return results

        json_data = json.loads(json_row)
        if not json_data['items'] or not json_data['indicators']:
            return results

        indicators = json_data['indicators']
        for item in json_data['items']:
            if not 'name' in item or not 'points' in item or not 'indicator' in item:
                continue

            parameters = {}
            for indicator in item['indicator']:
                if not 'value' in indicator or not 'id' in indicator or str(indicator['id']) not in indicators.keys():
                    continue

                parameters[indicators[str(indicator['id'])].strip()] = float(indicator['value'])

            single_data = {
                'name': item['name'],
                'points': float(item['points']),
                'url': url
            }

            if parameters:
                for parameter_data in parameters.items():
                    single_data[parameter_data[0]] = parameter_data[1]

            results.append(single_data)
        return results

    def get_products_links(self, url):
        results = {}
        time.sleep(2)
        headers = {
            'Host': 'rskrf.ru',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return results

        dom = BS(response.text, 'html.parser')
        items = dom.find_all('div', {'class': 'category-item'})
        if not items:
            return results

        for item in items:
            href = item.find('a')
            if not href['href']:
                continue

            title = item.find('span', {'class': 'h5'}).find('span')
            if not title.string:
                continue

            results[title.string] = self.main_url + href['href']
        return results

    def get_main_products_types_links(self):
        results = {}
        start_url = self.main_url + '/ratings/produkty-pitaniya/'
        headers = {
            'Host': 'rskrf.ru',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
        response = requests.get(start_url, headers=headers)
        if response.status_code != 200:
            return results

        dom = BS(response.text, 'html.parser')
        items = dom.find_all('div', {'class': 'category-item'})
        if not items:
            return results

        for item in items:
            href = item.find('a')
            if not href['href']:
                continue

            title = item.find('span', {'class': 'h5'})
            if not title.string:
                continue

            results[title.string] = self.main_url + href['href']
        return results

    def get_input_products_types(self, main_links):
        results = {}
        print('Выбрать продукты питания из предложенных (через разделитель ";")')
        print(list(main_links))
        input_products = input('Ввод продуктов (через разделитель ";") : ')
        input_products = input_products.split(';')
        for product in input_products:
            if product in main_links:
                results[product] = main_links[product]

        return results


parser = Dz2()
parser.start()
