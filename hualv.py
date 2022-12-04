import json

import requests
from lxml import etree
import time


# 爬取网页生成etree
def getconForHtml(html):
    url = html
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }
    response = requests.get(url=url, headers=header)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    concent = response.text

    htmlByEtree = etree.HTML(concent)
    if response.status_code == 200:
        print("成功连接")
    else:
        print("连接出错")

    return htmlByEtree


# 获取跟多的页面#翻页
def getMorePage(urlpre, urlsuf, start, end):
    urls = []
    for i in range(start, end):
        urls.append(urlpre + str(i) + urlsuf)
    return urls


# 获取需要爬取案例的url
def getSampleUrl(html):

    return html.xpath('//div[@class="tab-item"]/div/ul/li/p/a/@href')


# 对url进行处理,去除多余的部分
def delurl(urllist):
    url = []
    for i in urllist:
        url.append(i[10:])
    return url


# 获取案例
def getSample(url):
    time.sleep(3)

    pre = 'https://www.66law.cn/question/'
    realurl = pre + '' + url


    html = getconForHtml(realurl)

    title = html.xpath('/html/body/div[3]/div[3]/div[1]/div[1]/p[1]/text()')

    answernum = html.xpath('/html/body/div[3]/div[3]/div[1]/div[2]/div[1]/div/span[2]/text()')

    lawers = html.xpath('//ul[@class="reply-list reply-list2"]/li/div/p/a/text()')

    al = []
    hpl = []
    telel = []
    for i in range(len(lawers)):
        helpedPeople = html.xpath('/html/body/div[3]/div[3]/div[1]/div[2]/div[1]/ul/li[' + str(i + 1) + ']/div[1]/p[2]/text()')
        hpl.append(helpedPeople)
        tele = html.xpath('/html/body/div[3]/div[3]/div[1]/div[2]/div[1]/ul/li[' + str(i + 1) + ']/div[1]/p[3]/text()')
        telel.append(tele)
        answer = html.xpath('//ul[@class="reply-list reply-list2"]/li/p[@class="b"] ')[i].xpath("string(.)")
        al.append(answer)

    date = html.xpath('//ul[@class="reply-list reply-list2"]/li/p[@class="s-cb f12 mt15"]/text()')

    msg = {
        'title': title,
        'answernum': answernum
    }
    ansls = []

    for i in range(0, len(lawers)):
        try:
            hp = hpl[i][0]
        except:
            hp = "暂无"
        try:
            tele = telel[i][0]
        except:
            tele = '暂无'
        try:
            datet = date[i]
        except:
            datet = '暂无'
        ansls.append(lawers[i] + " " + hp + ' ' + tele + ' ' + al[i] + ' ' + datet)

    msg['answer'] = ansls
    print(msg)
    return msg


# 获取批量的案例
def getlistSample(urllist):
    listmsg = {}
    for i in range(1, len(urllist)):
        listmsg[i] = getSample(urllist[i])
    return listmsg


# 保存获取的url
def SaveUrlToLocal(urllist, filename):
    with open(filename, 'a', encoding='utf8') as f:
        for i in urllist:
            f.write(i)
            f.write(' ')
        f.close()


# 读取保存到本地的url
def loadUrlFromLocal(filename):
    with open(filename, 'r', encoding='utf8') as f:
        urls = f.read()

        f.close()
        return urls.split(' ')[:-1]


# 将爬取的数据保存到本地
# 生成一个json格式的文件
def saveJsonToLocal(msg, filepath):
    with open(filepath, 'w') as f:
        json.dump(msg, f)
    f.close()


# main
if __name__ == '__main__':
    # 打开网页
    url = 'https://www.66law.cn/question/laodongjiufen/'
    html = getconForHtml(url)
    # 获取要爬取4页的url
    urlpre = 'https://www.66law.cn/question/laodongjiufen/list_'
    urlsuf = '.aspx'
    ul = getMorePage(urlpre, urlsuf, 800, 850)
    # 对每个url进行案例url手机爬取
    for i in ul:
        html = getconForHtml(i)
        time.sleep(2)
        urllist = getSampleUrl(html)
        realUrl = delurl(urllist)
        # url存到本地
        SaveUrlToLocal(realUrl, "url8.txt")
    # #读取url
    urls = loadUrlFromLocal('url8.txt')
    print(len(urls))
    print(urls)
    # # # #根据案例url，获取案例数据
    getlistMsg = getlistSample(urls)
    print(getlistMsg)
    saveJsonToLocal(getlistMsg, 'hualv800_850.json')
    # # # with open('wkSample1188.json', 'r', encoding='utf8')as f:
    # # #     print(json.load(f))
