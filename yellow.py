import threading
import os
import requests
import json
import bs4


class ParserYellow:
    super_count = 0
    countries_dict = {}
    big_wanted_list = []
    super_param = []
    param_list = []
    sexidlist = ['F', 'M', 'U']

    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.get_total()
        self.making_country_dict()
        self.param_maker()
        self.make_dir()
        self.make_json()

    def text_parsing(self):
        response = requests.get(self.url, self.headers)
        text = response.text
        soup = bs4.BeautifulSoup(text, features="html.parser")
        print('text_parsing')
        return soup

    def get_total(self):
        url = "https://ws-public.interpol.int/notices/v1/yellow"
        response = requests.get(url, headers=self.headers)
        print(f'Необходимо загрузить {response.json()["total"]}')
        return

# словарь со странами
    def making_country_dict(self):
        id_ = "nationality"
        countries = self.text_parsing().find(id=id_).find_all('option')
        for country in countries:
            self.countries_dict[(str(country)).partition('"')[2].partition('"')[0]] = country.text
        self.countries_dict.pop('')
        print(f'Словарь стран создан-->{self.countries_dict}')
        return

    def param_maker(self):
        latin_string = 'qwertyuiopasdfghjklzxcvbnm'
        for symbol in latin_string:
            param = {'name': symbol}
            self.param_list.append(param)
        return self.param_list

    # создание папки для сохранения
    def make_dir(self):
        name_dir = "yellow_notice"
        os.mkdir(name_dir)
        for country in self.countries_dict.values():
            dir_path = os.path.join(os.getcwd(), name_dir, country)
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)
        print('Директории созданы')
        return

    # сохранение в соответствующую папку
    def json_saving(self, response, id_):
        list_ = response.json()['_embedded']['notices']
        for yellow_notice in list_:
            file_name = f'{yellow_notice["entity_id"].replace("/", "_")}.json'
            directory = 'yellow_notice'
            sub_dir = self.countries_dict[id_]
            file_url = os.path.join(os.getcwd(), directory, sub_dir, file_name)
            if not os.path.isfile(file_url):
                with open(file_url, 'w') as f:
                    json.dump(yellow_notice, f)
                    self.super_count += 1

    def make_json(self):
        for sexid in self.sexidlist:
            for country_id in self.countries_dict:
                url = f"https://ws-public.interpol.int/notices/v1/yellow?&nationality={country_id}" \
                       f"&resultPerPage=161&sexId={sexid}"
                response = requests.get(url=url, headers=self.headers)
                if response.json()['total'] == 0:
                    continue
                if response.json()['total'] <= 160:
                    self.json_saving(response, country_id)
                else:
                    self.big_wanted_list.append(response.json()['query']['nationality'])
        print(f'self.big_wanted_list-->{self.big_wanted_list}')
        for nationality in set(self.big_wanted_list):
            self.big_json(nationality)
        print(f'Загрузка обьектов {self.super_count} шт. заверешена')
        return

    def big_json(self, country_id):
        print(f'Загружаютя файлы из {self.countries_dict[country_id]}')
        url = "https://ws-public.interpol.int/notices/v1/yellow"
        params = {'ageMin': 0, 'ageMax': 120, 'nationality': country_id, 'resultPerPage': 160}
        params_2 = {'sexId': 'U'}
        response = requests.get(url, params=params_2 | params, headers=self.headers)
        self.json_saving(response, country_id)
        self.age_range(country_id, params, url, 0, 115)

    def age_range(self, nationality_id, params, url, a, b):
        def range_(sexid, nationality_id, params, url, a, b):
            for age in range(a, b):
                params_3 = {'sexId': sexid, 'ageMin': age, 'ageMax': age}
                response = requests.get(url, params=params | params_3, headers=self.headers)
                if response.json()['total'] == 0:
                    continue
                self.json_saving(response, nationality_id)

        f1 = threading.Thread(target=range_, args=('F', nationality_id, params, url, a, b,))
        f1.start()
        m1 = threading.Thread(target=range_, args=('M', nationality_id, params, url, a, b,))
        m1.start()
        f1.join()
        m1.join()
        return
