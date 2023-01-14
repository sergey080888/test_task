import time
import os
import shutil
from red import ParserRed
# from yellow import ParserYellow

url_1 = 'https://www.interpol.int/How-we-work/Notices/View-Red-Notices'
url_2 = 'https://www.interpol.int/How-we-work/Notices/View-Yellow-Notices'
HEADERS = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/53.0.2785.143 Safari/537.36'
    }

if __name__ == '__main__':
    start = time.time()
    if os.path.isdir('red_notice'):
        shutil.rmtree('red_notice')
    a = ParserRed(url_1, HEADERS)
    end = time.time()
    print(f'Время загрузки {round(((end-start)/60),2)}мин')
    # start = time.time()
    # if os.path.isdir('yellow_notice'):
    #     shutil.rmtree('yellow_notice')
    # b = ParserYellow(url_2, HEADERS)
    # end = time.time()
    # print(f'Время загрузки {round(((end-start)/60),2)}мин')

    # start = time.time()
    #
    # c = ParserRed(url_1, HEADERS).finding_withoutage_country()
    # end = time.time()
    # print(f'Время загрузки {round(((end-start)/60),2)}мин')
