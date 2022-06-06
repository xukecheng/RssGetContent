import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


class GamerSky:
    def __init__(self, url):
        self.url = url
        id = self.url.split("/")[-1]
        # 默认输入为 PC 链接，需要转为移动版链接
        mobile_url = "https://wap.gamersky.com/news/Content-" + id
        self.mobile_url = mobile_url
        self.headers = {
            "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Edg/81.0.416.77",
        }

    def getPageList(self) -> list:
        def pcUrlToMobileUrl(url: str) -> str:
            id = url.split("/")[-1]
            return "https://wap.gamersky.com/news/Content-" + id

        pc_soup = BeautifulSoup(
            str(requests.get(self.url, headers=self.headers).content, encoding="utf8"),
            "lxml",
        )
        page = pc_soup.find("div", {"class": "page_css"})
        page_list = []
        try:
            for i in page.contents:
                if "http" in str(i) and self.url not in str(i):
                    page_list.append(pcUrlToMobileUrl(i["href"]))
            del page_list[-1]
        except AttributeError:
            pass

        return page_list

    def getContent(self) -> str:
        def delString(string: str) -> str:
            return re.sub("相关资讯请关注.*", "", string, count=0, flags=0)

        page_list = self.getPageList()
        page_list.insert(0, self.mobile_url)
        content = ""
        for i in page_list:
            r = requests.get(i, headers=self.headers)
            soup = BeautifulSoup(str(r.content, encoding="utf8"), "lxml")
            need_del = soup.find("div", {"class": "gs_bot_author"})
            need_del.extract()
            need_del = soup.find("span", {"id": "pe100_page_contentpage"})
            need_del.extract()
            html = soup.find("div", {"class": "gsAreaContext"})
            content = content + str(html)
        return delString(content)


class Notion:
    def __init__(self, url: str):
        self.url = url

    def getPageHtml(self) -> str:
        browserless_url = os.getenv("BROWSERLESS_URL")
        browserless_token = os.getenv("BROWSERLESS_TOKEN")
        r = requests.post(
            f"{browserless_url}/function?token={browserless_token}",
            data=json.dumps(
                {
                    "context": {"url": self.url},
                    "code": "module.exports=async({page,context:b})=>{const{url}=b;await page.goto(url,{waitUntil:'networkidle2'});const data=await page.evaluate(()=>{var html=document.getElementsByClassName('notion-page-content')[0].innerHTML;var frag=document.createElement('div');frag.innerHTML=html;var imglist=[].map.call(frag.querySelectorAll('img'),function(img){return img.src});return{html:frag.innerHTML,imglist}});return{data:data,type:'application/json'}};",
                }
            ),
            headers={"Content-Type": "application/json"},
        )

        if r.status_code != 200:
            return "error"

        need_del_dict = {
            "/image/https": "https://www.notion.so/image/https",
            'href="/': 'href="https://www.notion.so/',
            "/images/emoji": "https://www.notion.so/images/emoji",
        }
        pattern = re.compile(r"max-width.*?(?:;)")

        json_response = r.content.decode()
        json_dict = json.loads(json_response)

        content = json_dict["html"]
        need_del_list = pattern.findall(content)
        need_del_list = list(dict.fromkeys(need_del_list))
        need_del_list.remove("max-width: 100%;")
        for item in need_del_list:
            need_del_dict[item] = ""

        for key in need_del_dict:
            content = content.replace(key, need_del_dict[key])

        img_pattern = re.compile(
            r"https:\/\/www\.notion\.so\/image\/https.*?(?:;cache=v2)"
        )
        img_url_list = img_pattern.findall(content)

        for img_url in img_url_list:
            secret_id = os.getenv("SECRET_ID")
            secret_key = os.getenv("SECRET_KEY")
            region = os.getenv("REGION")
            bucket = os.getenv("BUCKET")
            base_url = os.getenv("CDNURL")

            token = None
            scheme = "https"

            config = CosConfig(
                Region=region,
                SecretId=secret_id,
                SecretKey=secret_key,
                Token=token,
                Scheme=scheme,
            )
            client = CosS3Client(config)

            r = requests.get(img_url.replace("amp;", ""))
            print(img_url.replace("amp;", ""))
            print(img_url.replace("amp;", ""))

            if r.headers["Content-Type"].find("image") == -1:
                continue

            file_name = (
                r.headers["Content-Type"]
                + "/"
                + str(int(time.time()))
                + "."
                + r.headers["Content-Type"].split("/")[-1]
            )

            file_url = f"{base_url}{file_name}"

            response = client.put_object(
                Bucket=bucket,
                Body=r.content,
                Key=file_name,
            )
            print(response)
            print(file_url)

            content = content.replace(img_url, file_url)

        return content


def writeFile(content, mode):
    f = open("./test.html", mode, encoding="utf-8")
    f.write(str(content))
    f.close()


url = "https://www.notion.so/pmthinking/Vol-20220529-d10f4b2859074e76bf38cb457b6cb5fc"
writeFile(Notion(url=url).getPageHtml(), "w")
