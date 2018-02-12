import requests
import PyPDF2
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import shutil
import multiprocessing
from time import time

# TODO Удаление всех рабочик папок


class BiblioDownload:

    def __init__(self):

        # Введите необходимые параметры
        login = 'YOUR_LOGIN'
        password = 'YOUR_PASSWORD'
        book = 'BOOK_NUMBER'
        page_start = 1
        page_stop = 10


        url = 'https://biblio-online.ru/viewer/getPage/'
        url_viever = 'https://biblio-online.ru/viewer/'
        url_login = 'https://biblio-online.ru/login'
        self.dir_svg = 'svg/'
        self.dir_pdf = 'pdf/'
        book += '/'
        login_data = {'email': login,
                      'password': password
                      }
        self.page_start = page_start
        self.page_stop = page_stop
        self.cpu = multiprocessing.cpu_count()
        self.all_data = [page_start,
                         page_stop,
                         book,
                         url,
                         url_viever,
                         url_login,
                         self.dir_svg,
                         self.dir_pdf,
                         login_data,
                         self.cpu]

    def main_body(self):

        if self.page_start < 1:
            print('Некорректная первая страница')
            return
        if self.page_stop < self.page_start:
            print('Некорректная последняя страница')
            return
        os.mkdir('pdf')
        os.mkdir('svg')
        allProc = []
        files = ['page' + str(x) + '.pdf' for x in range(self.all_data[0], self.all_data[1]+1)]
        print('Процессов создано: {}'.format(self.cpu))
        time_start = time()
        for i in range(self.cpu):
            p = multiprocessing.Process(target=self.downloader, args=(self.all_data, i))
            allProc.append(p)
            p.start()
        for i in allProc:
            i.join()

        time_stop = time()
        time_res = time_stop - time_start
        time_res_min = int(time_res//60)
        print('\nСкачено {0} страниц, используя {1} cpu,'
              ' за {2} минут {3} секунд.\n'.format(self.page_stop+1-self.page_start,
                                                   self.cpu,
                                                   time_res_min,
                                                   round(time_res-(time_res_min*60))))
        print('Создаю общую книигу.')
        merger = PyPDF2.PdfFileMerger()
        for filename in files:
            merger.append(fileobj=open(self.dir_pdf + filename, 'rb'))

        merger.write(open(os.path.join('book.pdf'), 'wb'))
        merger.close()

        shutil.rmtree(self.dir_svg, ignore_errors=True)
        shutil.rmtree(self.dir_pdf, ignore_errors=True)
        return

    def downloader(self, data, num):
        page_start = data[0]
        page_stop = data[1]
        book = data[2]
        url = data[3]
        url_viever = data[4]
        url_login = data[5]
        dir_svg = data[6]
        dir_pdf = data[7]
        login_data = data[8]
        cpu = data[9]

        with requests.session() as ses:
            post = ses.post(url_login, data=login_data)
        print('Получение доступа к Viewer.')
        r = ses.get(url_viever + book)
        print('Доступ получен.')
        counter = 0
        for i in range(page_start + num, page_stop + 1, cpu):
            if counter >= 50:
                print('Получение доступа к Viewer.')
                r = ses.get(url_viever + book)
                print('Доступ получен.')
                counter = 0
            print('Скачиваю страницу: ', i)
            counter += 1
            r = ses.get(url + book + str(i))
            open(dir_svg + 'page' + str(i) + '.svg', 'wb').write(r.content)
            drawing = svg2rlg(dir_svg + 'page' + str(i) + '.svg')
            renderPDF.drawToFile(drawing, dir_pdf + 'page' + str(i) + '.pdf')


if __name__ == '__main__':
    run = BiblioDownload()
    run.main_body()
