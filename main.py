from pprint import pprint
import os
import requests, json
import bs4

url_1 = 'https://www.interpol.int/How-we-work/Notices/View-Red-Notices'
url_2 = 'https://www.interpol.int/How-we-work/Notices/View-Yellow-Notices'
HEADERS = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/53.0.2785.143 Safari/537.36'
    }


class Parser:
    super_count = 0
    countries_dict = {}

    def __init__(self, url, headers):
        # Динамические поля (переменные объекта)
        self.url = url
        self.headers = headers
        self.making_country_dict()

    def text_parsing(self):
        response = requests.get(self.url, self.headers)
        text = response.text
        soup = bs4.BeautifulSoup(text, features="html.parser")
        print('text_parsing')
        return soup

   # словарь со странами
    def making_country_dict(self):
        countries = self.text_parsing().find(id="arrestWarrantCountryId").find_all('option')
        # print(countries)
        for country in countries:
            self.countries_dict[(str(country)).partition('"')[2].partition('"')[0]] = country.text
        self.countries_dict.pop('')
        print('Словарь стран создан')
        return self.countries_dict

# # словарь национальностей#
#     def making_nationality_dict(self):
#         nationalities = self.text_parsing().find(id="nationality").find_all('option')
#         print(nationalities)
#         #
#         # nationalities_dict = {}
#         # for nationality in nationalities:
#         #     nationalities_dict[(str(nationality)).partition('"')[2].partition('"')[0]] = nationality.text
#         # nationalities_dict.pop('')
#         # return len(nationalities_dict)

    # создание папки для сохранения
    def make_dir(self):
        for country in self.countries_dict.values():
            dir_path = os.path.join(os.getcwd(), 'red_notice', country)
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
        self.make_dir()
        big_wanted_list = []
        for country_id in self.countries_dict:

            url = f"https://ws-public.interpol.int/notices/v1/red?&arrestWarrantCountryId={country_id}" \
                   f"&resultPerPage=1111111"

            response_ = requests.get(url, headers=self.headers)
            if response_.json()['total'] <= 160:
                wanted_list = response_.json()['_embedded']['notices']
                self.json_saving(wanted_list, country_id)
            else:
                big_wanted_list.append(response_.json()['query']['arrestWarrantCountryId'])
        return big_wanted_list

    def big_json(self):
        # ['AR', 'SV', 'IN', 'PK', 'RU', 'US']
        # a = ['AR', 'SV', 'IN', 'PK', 'RU', 'US']
        # for b in a:
        #     for i, country_id in enumerate(a):
        #         params = {'arrestWarrantCountryId': b, 'nationality': a[i - len(a) + 1], 'resultPerPage': 161}
        #         print(params)
        for i, country_id in enumerate(self.make_json()):
            params = {'arrestWarrantCountryId': country_id, 'nationality': self.make_json()[i-len(self.make_json())],
                      'resultPerPage': 161}
            response = requests.get("https://ws-public.interpol.int/notices/v1/red", params=params, headers=self.headers)
            self.super_count += 1
        print(f' Загружено {self.super_count}')
        return


if __name__ == '__main__':
    a = Parser(url_1, HEADERS).big_json()
    print(a)
