__author__ = 'Xinchanghao'
#encoding:utf-8

import http
import urllib
import urllib.request
import http.cookies
import http.cookiejar
import pymysql
from bs4 import BeautifulSoup


class Spider:
    def __init__(self):
         self.URL='http://www.banyuetan.org/chcontent/zx/shxw/index.shtml'
         self.enable=''
         self.charaterset='utf-8'
         self.cookie = http.cookiejar.LWPCookieJar()
         self.headers = {
             'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
             'Accept-Encoding': "gzip, deflate",
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'cookie': self.cookie,
             'Host':'www.banyuetan.org',
             #'Referer':"http://www.banyuetan.org/chcontent/zx/shxw/index_425.shtml",
             'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3067.6 Safari/537.36",
         }
         self.hander = urllib.request.HTTPCookieProcessor(self.cookie)
         self.opener = urllib.request.build_opener(self.hander)

    #解析目标html
    def parsehtml(self,response):
        if response.getcode():
            soup = BeautifulSoup(response, 'html.parser', from_encoding='utf-8')
            div = soup.find('div', class_="content_con_list")
            if div:
                head = div.find("h1").get_text().strip()
                time = div.find("h2").find("span").find_all("b")[0].get_text()
                if div.find("h2").find("span").find_all("b")[1].find(has_no_author):
                    author = ""
                    origin = div.find("h2").find("span").find_all("b")[1].get_text()
                    editor = div.find("h2").find("span").find_all("b")[2].get_text()
                else:
                    author = div.find("h2").find("span").find_all("b")[1].get_text()
                    origin = div.find("h2").find("span").find_all("b")[2].get_text()
                    editor = div.find("h2").find("span").find_all("b")[3].get_text()
                text = soup.find('div', class_="text").find_all("b")
                words = ""
                for word in text:
                    words += word.get_text().strip()+"|"
                words = words.replace(' ', '')
                self.saveinfo(head,time,author,origin,editor,words)
            else:
                return

    def findlink(self):
        for i in range(2,425):
            url = "http://www.banyuetan.org/chcontent/zx/shxw/index_"+repr(i)+".shtml"
            response = self.openlink(url)
            print(str(response.getcode())+"第"+str(i)+"页")
            if response.getcode():
                    soup = BeautifulSoup(response,'html.parser',from_encoding='utf-8')
                    div = soup.find('div', class_="list_cont_li")
                    links = div.find("ul").find_all(has_no_style)
                    #print(links);
                    for l in links:
                        linknode = l.find_all("a")
                        for link in linknode:
                            link ="http://www.banyuetan.org"+link.get("href")
                            #print(link);
                            response2 = self.openlink(link)
                            response = self.parsehtml(response2)
            else:
                continue

    #插入数据至数据库
    def saveinfo(self,head,times,author,origin,editor,words):
        # if isinstance(words, str):
        #     print("the type of bbb is string")
        try:
            conn = pymysql.connect(host='localhost', user='root', passwd='', db='spider', port=3306,charset='utf8')
            cur = conn.cursor()  # 获取一个游标
            # cur.execute("SELECT * FROM word")
            cur.execute('INSERT INTO word(head, times, author, origin, editor, words) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")'%(head,times,author,origin,editor,words))
            cur.fetchall()
            conn.commit()
            print("插入数据库成功" + times)
            cur.close()  # 关闭游标
            conn.close()  # 释放数据库资源
        except  Exception:
            print("插入数据库失败" + times)

    #打开网页链接,等待响应
    def openlink(self,link):
        maxTryNum = 10
        for tries in range(maxTryNum):
            try:
                req = urllib.request.Request(link, headers = self.headers)
                response = urllib.request.urlopen(link)
                return response
            except:
                if tries < (maxTryNum - 1):
                    continue
                else:
                    print("Has tried %d times to access url %s, all failed!", maxTryNum, link)
                    break

#没有style属性的节点
def has_no_style(tag):
        return not tag.has_attr('style')

#没有作者的节点
def has_no_author(tag):
        return not tag.find('span')

#关键词
def has_word(tag):
        return  tag.find('b')


if __name__ == '__main__':

    xch = Spider()
    xch.findlink()
