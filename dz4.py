import re
import requests
from pymongo import MongoClient
from pymongo.errors import *
from lxml import html


class Dz4:
    def start(self):
        news_data = self.get_news()
        if not news_data:
            print('Не получены новости')
            return

        client = MongoClient('localhost', 27017)
        db = client['dz_database']
        news = db.news
        self.data_insert(news, news_data)

    def data_insert(self, table_name, data):
        for row in data:
            index = {'_id': row['title']}
            row = index | row
            try:
                table_name.insert_one(row)
            except DuplicateKeyError as e:
                print(row['_id'] + ' дублирующийся ключ')

    def get_news(self):
        results = []
        start_url = 'https://lenta.ru/'
        headers = {
            'Host': 'lenta.ru',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
        response = requests.get(start_url, headers=headers)
        if response.status_code != 200:
            print('Источник недоступен')
            return results

        root = html.fromstring(response.text)
        cards = root.xpath("//a[contains(@class, 'card-mini')]")
        if not cards:
            return results

        for card in cards:
            title = card.xpath(".//span[contains(@class, 'card-mini__title')]/text()")
            if not title:
                continue

            title = title[0].strip()
            href = card.xpath(".//@href")
            if not href:
                continue

            href = href[0].strip()
            pos = href.find('https')
            if pos == -1:
                href = 'https://lenta.ru' + href

            date = ''
            datematch = re.search(r'(?:(\d{4})\/(\d{2})\/(\d{2}))', href)
            if datematch:
                date = datematch[1] + '-' + datematch[2] + '-' + datematch[3]

            datematch1 = re.search(r'(?:(\d{2})-(\d{2})-(\d{4}))', href)
            if date == '' and datematch1:
                date = datematch1[3] + '-' + datematch1[2] + '-' + datematch1[1]

            news = {
                'source': start_url,
                'title': title,
                'href': href,
                'date': date,
            }

            results.append(news)

        return results


parser = Dz4()
parser.start()
