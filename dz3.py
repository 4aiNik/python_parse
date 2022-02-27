import pandas as pd
from pymongo import MongoClient
from pymongo.errors import *
import os.path


class Dz3:

    def start(self):
        client = MongoClient('localhost', 27017)
        db = client['dz_database']
        products = db.products
        file_path = 'dz2.csv'
        if not os.path.exists(file_path):
            print('Нет файла')
            return

        # откуда берется файл dz2.csv см. д/з №2
        data = pd.read_csv('dz2.csv')
        if data.empty:
            print('Нет данных')
            return

        self.data_insert(products, data)
        self.show_current_data(products)

    def data_insert(self, table_name, data):
        for item in data.values:
            row = dict(zip(data.columns.values, item))
            del row['Unnamed: 0']
            index = {}
            index['_id'] = row['name']
            row = index | row
            try:
                table_name.insert_one(row)
            except DuplicateKeyError as e:
                print(row['_id'] + ' дублирующийся ключ')

    def show_current_data(self, table_name):
        low_limit = input('Ввод нижнего значения рейтинга / качества: ')
        try:
            float(low_limit)
        except ValueError:
            print('Введено не корректное значение')
            return

        low_limit = float(low_limit)
        for item in table_name.find({'$or': [{'points': {'$gte': low_limit}}, {'Качество': {'$gte': low_limit}}]}):
            print(item)


parser = Dz3()
parser.start()
