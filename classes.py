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
        self.make_json()

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
        # print(countries)
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
    def json_saving(self, list_, id_):
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
            if response.json()['total'] <= 160:
                wanted_list = response.json()['_embedded']['notices']
                # print(f'make_json- wanted_list-->{wanted_list}')
                self.json_saving(wanted_list, country_id)
            else:
                self.big_wanted_list.append(response.json()['query']['arrestWarrantCountryId'])
        # print(f'make_json --> {self.big_wanted_list}')
        # for country in self.big_wanted_list:
        #     self.big_json(country)
        #
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
        headers = self.headers
        params = {'ageMin': 0, 'ageMax': 120, 'arrestWarrantCountryId': country_id, 'resultPerPage': 160}
        params_2 = {'sexId': 'U'}
        response = requests.get(url, params=params_2 | params, headers=headers)
        wanted_list = response.json()['_embedded']['notices']
        self.json_saving(wanted_list, country_id)

        for age in range(18, 120):
            params_3 = {'sexId': 'F', 'ageMin': age, 'ageMax': age}
            params_4 = {'sexId': 'M', 'ageMin': age, 'ageMax': age}
            response = requests.get(url, params=params | params_3, headers=headers)
            if response.json()['total'] > 160:
                for param_name in self.param_list:
                    response = requests.get(url, params=(params | params_3) | param_name, headers=headers)
                    wanted_list = response.json()['_embedded']['notices']
                    self.json_saving(wanted_list, country_id)
            else:
                wanted_list = response.json()['_embedded']['notices']
                self.json_saving(wanted_list, country_id)

            response = requests.get(url, params=params | params_4, headers=headers)
            if response.json()['total'] > 160:
                for param_name in self.param_list:
                    response = requests.get(url, params=(params | params_4) | param_name, headers=headers)
                    wanted_list = response.json()['_embedded']['notices']
                    self.json_saving(wanted_list, country_id)
            else:
                wanted_list = response.json()['_embedded']['notices']
                self.json_saving(wanted_list, country_id)


            # url = f"https://ws-public.interpol.int/notices/v1/red?&arrestWarrantCountryId={country_id}" \
            #       f"&resultPerPage=161"
            #
            # response = requests.get(url, headers=self.headers)
            # if response.json()['total'] <= 160:
            #     wanted_list = response.json()['_embedded']['notices']
            #     # print(f'make_json- wanted_list-->{wanted_list}')
            #     self.json_saving(wanted_list, country_id)

        return self.super_param
    # def big_json(self, country_id):
    #     for age in range(18, 121):
    #         url = "https://ws-public.interpol.int/notices/v1/red"
    #         params = {'ageMin': age, 'ageMax': age, 'arrestWarrantCountryId': country_id, 'resultPerPage': 161}
    #         headers = self.headers
    #         wanted_list = requests.get(url, params=params, headers=headers).json()['_embedded']['notices']
    #         self.json_saving(wanted_list, country_id)
    #         print(wanted_list)
