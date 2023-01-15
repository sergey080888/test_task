import threading
import os
import requests
import json
import bs4


class ParserRed:
    super_count = 0
    countries_dict = {}
    big_wanted_list = []
    super_param = []
    param_list = []

    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.get_total()
        self.making_country_dict()
        self.param_maker()
        self.make_dir()
        # self.finding_withoutage_country()
        # self.make_json()
        withoutage_thr = threading.Thread(target=self.finding_withoutage_country)
        withoutage_thr.start()
        make_json_thr = threading.Thread(target=self.make_json)
        make_json_thr.start()
        withoutage_thr.join()
        make_json_thr.join()

    def finding_withoutage_country(self):
        url = "https://ws-public.interpol.int/notices/v1/red"
        withoutage_person_list_countries = []
        params_2 = {'ageMin': 0}
        for country in self.countries_dict:
            params = {'arrestWarrantCountryId': country, 'resultPerPage': 160}
            response = requests.get(url, params=params, headers=self.headers)
            response_2 = requests.get(url, params=params_2 | params, headers=self.headers)
            if response.json()['total'] != response_2.json()['total']:
                withoutage_person_list_countries.append(response_2.json()["query"]['arrestWarrantCountryId'])
        print(f'Страны в которых не отображается возраст--> {withoutage_person_list_countries}')
        # формирование потоков
        thread_list1 = []
        for withoutage_country in withoutage_person_list_countries:
            withoutage_country = threading.Thread(target=self.finding_withoutage_person, args=(url, withoutage_country,
                                                                                               self.headers, params_2,))
            withoutage_country.start()
            thread_list1.append(withoutage_country)

        for withoutage_country in thread_list1:
            withoutage_country.join()

    def finding_withoutage_person(self, url, withoutage_country, headers, params_2):
        magic_symbols = []
        for symb in self.param_list:
            params = {'name': symb['name'], 'sexId': 'M', 'arrestWarrantCountryId': withoutage_country,
                      "resultPerPage": 200}
            response = requests.get(url, params=params, headers=headers)
            response_2 = requests.get(url, params=params_2 | params, headers=headers)
            if response.json()['total'] != response_2.json()['total']:
                magic_symbols.append(response_2.json()["query"]['name'])
        print(f'символы-->{magic_symbols}')       # #     ->['i', 'a', 'd', 'h', 'v']
        withoutage_person_list_countries_2 = []
        withoutage_person_list_countries_3 = []
        for symb in magic_symbols:
            print(symb)
            params = {'name': symb, 'sexId': 'M', 'arrestWarrantCountryId': withoutage_country, "resultPerPage": 200}
            response = requests.get(url, params=params, headers=headers)
            for c in response.json()['_embedded']['notices']:
                withoutage_person_list_countries_3.append(c)
            # print(withoutage_person_list_countries_3)
            response_2 = requests.get(url, params=params_2 | params, headers=headers)
            for c in response_2.json()['_embedded']['notices']:
                withoutage_person_list_countries_2.append(c)
        for dict_ in withoutage_person_list_countries_2:
            if dict_ in withoutage_person_list_countries_3:
                withoutage_person_list_countries_3.remove(dict_)
        print(withoutage_person_list_countries_3)
        for red_notice in withoutage_person_list_countries_3:
            file_name = f'{red_notice["entity_id"].replace("/", "_")}.json'
            directory = 'red_notice'
            sub_dir = self.countries_dict[withoutage_country]
            file_url = os.path.join(os.getcwd(), directory, sub_dir, file_name)
            if not os.path.isfile(file_url):
                with open(file_url, 'w') as f:
                    json.dump(red_notice, f)
                    self.super_count += 1

    def text_parsing(self):
        response = requests.get(self.url, self.headers)
        text = response.text
        soup = bs4.BeautifulSoup(text, features="html.parser")
        print('text_parsing')
        return soup

    def get_total(self):
        url = "https://ws-public.interpol.int/notices/v1/red"
        response = requests.get(url, headers=self.headers)
        print(f'Необходимо загрузить {response.json()["total"]}')
        return

# словарь со странами
    def making_country_dict(self):
        id_ = "arrestWarrantCountryId"
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
        name_dir = "red_notice"
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
        for red_notice in list_:
            file_name = f'{red_notice["entity_id"].replace("/", "_")}.json'
            directory = 'red_notice'
            sub_dir = self.countries_dict[id_]
            file_url = os.path.join(os.getcwd(), directory, sub_dir, file_name)
            if not os.path.isfile(file_url):
                with open(file_url, 'w') as f:
                    json.dump(red_notice, f)
                    self.super_count += 1

    def make_json(self):
        for country_id in self.countries_dict:
            url = f"https://ws-public.interpol.int/notices/v1/red?&arrestWarrantCountryId={country_id}" \
                   f"&resultPerPage=161"
            response = requests.get(url, headers=self.headers)
            if response.json()['total'] == 0:
                continue
            if response.json()['total'] <= 160:
                self.json_saving(response, country_id)
            else:
                self.big_wanted_list.append(response.json()['query']['arrestWarrantCountryId'])
        thread_list = []
        for thr in self.big_wanted_list:
            thr = threading.Thread(target=self.big_json, args=(thr,))
            thr.start()
            thread_list.append(thr)
        for thr in thread_list:
            thr.join()
        print(f'Загрузка обьектов {self.super_count} шт. заверешена')
        return

    def big_json(self, country_id):
        print(f'Загружаютя файлы из {self.countries_dict[country_id]}')
        url = "https://ws-public.interpol.int/notices/v1/red"
        params = {'ageMin': 0, 'ageMax': 120, 'arrestWarrantCountryId': country_id, 'resultPerPage': 160}
        params_2 = {'sexId': 'U'}
        response = requests.get(url, params=params_2 | params, headers=self.headers)
        self.json_saving(response, country_id)
        self.age_range(country_id, params, url, 18, 100)

    def age_range(self, country_id, params, url, a, b):
        sexidlist = ['F', 'M']
        for sexid in sexidlist:
            for age in range(a, b):
                params_3 = {'sexId': sexid, 'ageMin': age, 'ageMax': age}
                response = requests.get(url, params=params | params_3, headers=self.headers)
                if response.json()['total'] == 0:
                    continue
                if response.json()['total'] > 160:
                    for param_name in self.param_list:
                        response = requests.get(url, params=((params | params_3) | param_name), headers=self.headers)
                        if response.json()['total'] > 160:
                            for param_symbol in self.param_list:
                                params_5 = {'forename': param_symbol['name']}
                                response = requests.get(url, params=(((params | params_3) | param_name) | params_5),
                                                        headers=self.headers)
                                print(f'{sexid}{response.json()["query"]}')
                                self.json_saving(response, country_id)
                        else:
                            self.json_saving(response, country_id)
                else:
                    self.json_saving(response, country_id)
        return
    #
    # param_list = [
    #     {'page': 1, 'resultPerPage': 160, 'ageMin': 32, 'ageMax': 32, 'sexId': 'M', 'arrestWarrantCountryId': 'RU'},
    #     {'page': 1, 'resultPerPage': 160, 'ageMin': 33, 'ageMax': 33, 'sexId': 'M', 'arrestWarrantCountryId': 'RU'}]
