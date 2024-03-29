import requests
from bs4 import BeautifulSoup
import re


class GamerSky():
    def __init__(self, url):
        self.url = url
        id = self.url.split('/')[-1]
        # 默认输入为 PC 链接，需要转为移动版链接
        mobile_url = 'https://wap.gamersky.com/news/Content-' + id
        self.mobile_url = mobile_url
        self.headers = {
            'user-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Edg/81.0.416.77',
        }

    def getPageList(self) -> list:
        def pcUrlToMobileUrl(url: str) -> str:
            id = url.split('/')[-1]
            return 'https://wap.gamersky.com/news/Content-' + id

        pc_soup = BeautifulSoup(
            str(requests.get(self.url, headers=self.headers).content,
                encoding="utf8"), 'lxml')
        page = pc_soup.find("div", {"class": "page_css"})
        page_list = []
        try:
            for i in page.contents:
                if "http" in str(i) and self.url not in str(i):
                    page_list.append(pcUrlToMobileUrl(i['href']))
            del page_list[-1]
        except AttributeError:
            pass

        return page_list

    def getContent(self) -> str:
        def delString(string: str) -> str:
            return re.sub("相关资讯请关注.*", '', string, count=0, flags=0)

        page_list = self.getPageList()
        page_list.insert(0, self.mobile_url)
        content = ''
        for i in page_list:
            r = requests.get(i, headers=self.headers)
            soup = BeautifulSoup(str(r.content, encoding="utf8"), 'lxml')
            need_del = soup.find("div", {"class": "gs_bot_author"})
            need_del.extract()
            need_del = soup.find("span", {"id": "pe100_page_contentpage"})
            need_del.extract()
            html = soup.find("div", {"class": "gsAreaContext"})
            content = content + str(html)
        return delString(content)


# def writeFile(content, mode):
#     f = open('./test.html', mode, encoding='utf-8')
#     f.write(str(content))
#     f.close()

# url = 'https://ol.gamersky.com/news/202011/1339382.shtml'
# writeFile(GamerSky(url=url).getContent(), 'w')
