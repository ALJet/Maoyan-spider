import os

import requests
import re

from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from bs4 import BeautifulSoup
from lxml import etree


class maoyan():

    def __init__(self):
        self.DOWNLOAD_FOLDER = 'woffs/'

        self.url = 'https://maoyan.com/board/1'

        self.code_num = ({})

        self.header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': '__mta=142048781.1603438046157.1603677218765.1603677357711.7; uuid_n_v=v1; uuid=80CD19E0136211EBA552ABBE67708AC9893773B6C63C46E5B052FB6B81674941; _lxsdk_cuid=17549bd2d7cc8-01a078b250478d-3c634103-1fa400-17549bd2d7cc8; _lxsdk=80CD19E0136211EBA552ABBE67708AC9893773B6C63C46E5B052FB6B81674941; _csrf=838a725af889d425d8cafdc4b37dc5a6bc96bc7fc6895d9bfcd1e1b506b47125; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1603259936,1603438046,1603676465,1603677204; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; __mta=142048781.1603438046157.1603438046157.1603677204178.2; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1603677357; _lxsdk_s=1756290e5b7-fbf-7b6-5af%7C%7C8',
            'Host': 'maoyan.com',
            'Referer': 'https: //maoyan.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',

        }

    def get_info(self):
        response = requests.get(url=self.url, headers=self.header)
        if response.status_code == 200:
            # print('成功登陆到url地址')
            self.parse_url(response)
        else:
            print('无法登录url地址,状态码： %s' % response.status_code)

    def parse_url(self, response):
        html = response.text

        font_file_name = re.findall('//vfile.meituan.net/colorstone/(.*?).woff', html)
        # print(font_file_name)
        font_file_name = font_file_name[0] + '.woff'
        url = 'http://vfile.meituan.net/colorstone/' + font_file_name
        self.download_woff_file(font_file_name)
        self.parse_woff_file(font_file_name)

    def download_woff_file(self, font_file_name):
        if self.woff_is_exist(font_file_name):
            self.parse_num()
        else:
            font_url = 'http://vfile.meituan.net/colorstone/' + font_file_name
            self.download_font_file(font_url, font_file_name)

    def download_font_file(self, url, font_file_name):
        font_woff = requests.get(url, stream=True)
        with open(self.DOWNLOAD_FOLDER + font_file_name, 'wb') as w:
            for bunk in font_woff:
                w.write(bunk)

    def woff_is_exist(self, font_file_name):
        if os.path.exists(self.DOWNLOAD_FOLDER + font_file_name):
            return True
        #我觉得删除DOWNLOAD_FOLDER下面的所有文件 太重要了 这样不会重复 数据才不会出错(删除这里 执行的话 可能会无法执行 必须切换到windows 的cmd中 而且用管理员打开------python maoyan.py)
        # os.remove(self.DOWNLOAD_FOLDER)
        return False

    '''读取到woff文件 把每一个code里面的信息画成一张对应的图片（保存名称为code 名称） 例如:uniE303 == 8.png
    把他呈现出来 接下里用识别出里面的数字 
    '''

    def parse_woff_file(self, font_file_name):
        font = TTFont(self.DOWNLOAD_FOLDER + font_file_name)
        font.saveXML(self.DOWNLOAD_FOLDER + 'cur.xml')
        width = 600
        height = 720

        uni_list = font.getGlyphOrder()[2:]
        for i in uni_list:
            coordinates = []
            for j in font['glyf'][i].coordinates:
                coordinates.append(j)
            im = Image.new("RGB", (width, height), "white")
            id = ImageDraw.Draw(im)
            id.polygon(coordinates,
                       fill=(0, 0, 0))
            im = im.transpose(Image.ROTATE_180)
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
            im = im.resize((60, 60))
            im = im.convert('L')
            im.save(self.DOWNLOAD_FOLDER + str(i) + '.png')

    '''把图片的的数字识别出来 要使用到 tensorflow2的识别 放到对应的字典中 
    例如 [uniE303 = 8]
    '''

    def parse_num(self):
        print('待续')

    '''
    解析html 得到网页的数据
    '''

    def parse_html(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        movies = soup.select('.board-wrapper')
        movie_list = movies[0].select('dd')
        for i in range(len(movie_list)):
            movie_name = movie_list[i].select('.movie-item-info')[0].select('.name')[0].text
            movie_star = movie_list[i].select('.star')[0].text[3:]
            movie_date = movie_list[i].select('.releasetime')[0].text
            real_money = movie_list[i].select('.realtime')[0].select('.stonefont')[0].text
            real_unit = movie_list[i].select('.realtime')[0].text[-2]
            total_money = movie_list[i].select('.total-boxoffice')[0].select('.stonefont')[0].text
            total_unit = movie_list[i].select('.total-boxoffice')[0].text[-2]

            print('电影: ', movie_name)
            print('主演: ', movie_star)
            print('上映时间: ', movie_date)
            print()
            # print('实时票房: ', self.convert_boxoffice(real_money), real_unit)
            # print('总票房: ', self.convert_boxoffice(total_money), total_unit)


if __name__ == '__main__':
    my = maoyan()
    my.get_info()
