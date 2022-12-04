import logging
import sys
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json
from selenium.webdriver.support.select import Select
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from selenium.webdriver.chrome.service import Service
import os

log_format = '%(levelname)s %(asctime)s %(filename)s %(lineno)d %(message)s'
logging.basicConfig(filename="spiderlog.txt", format=log_format, level=logging.DEBUG)

getfailedCount = 0


# 打开浏览器
def openChrome(userpath):
    logging.info('start openChrome')
    opt = webdriver.ChromeOptions()
    opt.add_argument(userpath)
    s = Service('driver/chromedriver.exe')
    web = webdriver.Chrome(options=opt, service=s)

    return web


# 搜索关键字
def SearchKey(web, key):
    logging.info('start SearchKey')
    web.find_element(by='xpath', value='//*[@id="keyword"]').send_keys(key)
    web.find_element(by='xpath', value='//*[@id="keyword"]').send_keys(Keys.ENTER)
    time.sleep(1)
    web.find_element(by='xpath', value='//*[@id="columnSelectModelButton"]').click()
    time.sleep(1)

    web.find_element(by='xpath',
                     value='//*[@id="wkb-search-tools"]/div[1]/div[1]/dropdown/div/div/fullscreen/div/div/div/dropdown-menu/ul/dropdown-menu-item[2]').click()
    time.sleep(1)
    web.find_element(by='xpath', value='//*[@id="wkb-search-tools"]/div[2]/button-field/div/button').click()
    time.sleep(3)


#############################
# 获取案例
def GetSample(web, i):
    time.sleep(4)
    logging.info('start GetSample')

    global getfailedCount
    try:
        title = web.find_element(By.XPATH,
                                 value=f'/html/body/bold-app/b-judgment-documents/div/div[2]/div/div/div/div[2]/splitpane/div/div/div/div/b-no-data/div/div[1]/div/b-list-item-judgment-documents[{str(i)}]/div/div[2]/div[1]/div[1]/b-lock/a').text
        # print(title)
        court = web.find_element(By.XPATH,
                                 value='/html/body/bold-app/b-judgment-documents/div/div[2]/div/div/div/div[2]/splitpane/div/div/div/div/b-no-data/div/div[1]/div/b-list-item-judgment-documents[' + str(
                                     i) + ']/div/div[2]/div[2]/div[1]/div[1]').text
        # print(court)
        case_num = web.find_element(By.XPATH,
                                    value='/html/body/bold-app/b-judgment-documents/div/div[2]/div/div/div/div[2]/splitpane/div/div/div/div/b-no-data/div/div[1]/div/b-list-item-judgment-documents[' + str(
                                        i) + ']/div/div[2]/div[2]/div[1]/div[2]').text
        # print(case_num)
        deldate = web.find_element(By.XPATH,
                                   value='/html/body/bold-app/b-judgment-documents/div/div[2]/div/div/div/div[2]/splitpane/div/div/div/div/b-no-data/div/div[1]/div/b-list-item-judgment-documents[' + str(
                                       i) + ']/div/div[2]/div[2]/div[1]/div[3]').text
        # print(deldate)
        ##进入此页面
        web.find_element(By.XPATH,
                         value='/html/body/bold-app/b-judgment-documents/div/div[2]/div/div/div/div[2]/splitpane/div/div/div/div/b-no-data/div/div[1]/div/b-list-item-judgment-documents[' + str(
                             i) + ']/div/div[2]/div[1]/div[1]/b-lock/a').click()
        # print("in")
        # 页面切换
        switchToChilPage(web)

        anyou = web.find_element(By.XPATH,
                                 value='//*[@id="detail-page-container"]/div/div/div/splitpane/div/div/div/div/b-meta-note/div/div[2]/span').text
        # print(anyou)

        try:

            fulltext = web.find_element(By.XPATH, value='//*[@id="detail-content"]/div').text
            # print(fulltext)
        except:
            fulltext = "获取失败"
            getfailedCount = getfailedCount + 1

            if getfailedCount > 5:
                print("1")
                return 'error'
        law = re.findall('《(.*?)》', fulltext)
    except:

        return 'error'

    sample = {
        'title': title,
        '法院': court,
        '案号': case_num,
        'date': deldate,
        '案由': anyou,
        'law': law,
        'fulltext': fulltext
    }

    switchToParentlPage(web)
    time.sleep(1)
    return sample


def switchToChilPage(web):
    now_page = web.window_handles
    web.switch_to.window(now_page[1])
    time.sleep(5)


def switchToParentlPage(web):
    web.close()
    now_page = web.window_handles
    web.switch_to.window(now_page[0])


# 设置每页多少条
def SetPageCount(web, count):
    logging.info('start SetPageCount')

    selector = Select(web.find_element(by='xpath',
                                       value='/html/body/bold-app/b-judgment-documents/div/div[2]/div/div/div/div[2]/splitpane/div/div/div/div/b-no-data/div/div[2]/b-pagination-custom/pagination-bar/nav/pagination-bar-right/div/select-field/form-field/div/form-field-body/div/div/select'))
    selector.select_by_value(count)
    time.sleep(2)


# 获取多条案例
def getMoreSample(web, start, end):
    logging.info('start getMoreSample')

    samplelist = {}
    runtimeflag = 0

    for i in range(start, end + 1):
        # samplelist.append(GetSample(web,i))
        tempSample = GetSample(web, i)
        time.sleep(1)
        if tempSample != 'error':
            samplelist[i] = tempSample
        else:
            print('3')
            print('error')
            runtimeflag = 1
            break

    return samplelist, runtimeflag


# 翻页
def nextPage(web):
    logging.info('start nextPage')

    web.find_element(By.XPATH,
                     value='/html/body/bold-app/b-judgment-documents/div/div[2]/div/div/div/div[2]/splitpane/div/div/div/div/b-no-data/div/div[2]/b-pagination-custom/pagination-bar/nav/pagination-bar-right/div/pagination/ul/li[9]/a').click()
    time.sleep(2)


# 存取裁判文书全文到本地
def saveFulltextInloacl(fulltext, filepath):
    logging.info('start saveFulltextInloacl')

    with open(filepath, 'r', encoding='utf8') as f:
        f.write("#################################")
        f.write(fulltext)
        f.close()


# 获取当前窗口句柄
def getNowHandle(web):
    logging.info('start getNowHandle')

    indexhandle = web.current_window_handle
    return indexhandle


#####################
# 生成一个json格式的文件
def saveJsonToLocal(samples, filepath):
    logging.info('start saveToLocal')

    with open(filepath, 'w') as f:
        json.dump(samples, f)
    f.close()


# 发送邮件
def sendEmail(filepath, toaddrs):
    logging.info('start sendEmail')

    fromaddr = 'taomrblack@qq.com'
    password = 'elavcanawzyrcbci'

    # content = 'hello, this is email content.'

    zipFile = filepath
    zipApart = MIMEApplication(open(zipFile, 'rb').read())
    zipApart.add_header('Content-Disposition', 'attachment', filename=zipFile)

    m = MIMEMultipart()

    m.attach(zipApart)
    m['From'] = "Tao"  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    m['Subject'] = 'title'
    try:
        server = smtplib.SMTP('smtp.qq.com')
        server.login(fromaddr, password)
        server.sendmail(fromaddr, toaddrs, m.as_string())
        print('success')
        server.quit()
        return 'success'
    except smtplib.SMTPException as e:
        print('error:', e)
        return 'error'


def getDateForFilter(year):
    #
    yeartime = year * 10000
    # 获取当前时间 如20220923
    nowdate = time.strftime('%Y%m%d')
    # 数字化时间
    # numdate = time.strftime('%Y%m%d')
    olddate = int(nowdate) - yeartime
    od = str(olddate)[0:4] + '.' + str(olddate)[4:6] + '.' + str(olddate)[6:]

    # 网站取的时间为明天
    nowdate = int(nowdate) + 1
    # 根据网站需要的格式生成如2022.09.24
    nd = str(nowdate)[0:4] + '.' + str(nowdate)[4:6] + '.' + str(nowdate)[6:]

    return od, nd


# 打开民事
def setfilter_openCivil(web):
    web.find_element(By.XPATH, value='//*[@id="tree_causeOfActionǁ01000000000000民事ǁǂ"]/div/div[2]/a').click()
    time.sleep(1)


# 打开劳动争议父级
def setfilter_openlabour(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议ǁǂ"]/div/div[2]/a').click()
    time.sleep(1)


# 打开劳动争议
def setfilter_openlabour_dispute(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议ǁǂ"]/div/div[2]/a').click()
    time.sleep(1)


# 打开合同保险
def setfilter_openlabour_dispute_Contract(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010010000劳动合同纠纷ǁǂ"]/div/div[2]/a').click()
    time.sleep(1)


# 设置为追索劳动报酬 Recourse to labour remuneration
def setfilter_openlabour_dispute_Contract_RTLR(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010010000劳动合同纠纷/01060010010060追索劳动报酬纠纷ǁǂ"]/div/div[2]/a').click()
    time.sleep(1)
    num = web.find_element(By.XPATH,
                           value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010010000劳动合同纠纷/01060010010060追索劳动报酬纠纷ǁǂ"]/div/div[2]/div').text

    return num


# 打开确认劳务关系纠纷 Confirm labor relationship disputes
def setfilter_openlabour_dispute_Contract_CLRD(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010010000劳动合同纠纷/01060010010010确认劳动关系纠纷ǁǂ"]/div/div[2]/a').click()
    time.sleep(1)
    num = web.find_element(By.XPATH,
                           value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010010000劳动合同纠纷/01060010010010确认劳动关系纠纷ǁǂ"]/div/div[2]/div').text
    time.sleep(1)

    return num


# 打开劳务派遣纠纷 Labor dispatch contract disputes
def setfilter_openlabour_dispute_Contract_LDCD(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010010000劳动合同纠纷/01060010010040劳务派遣合同纠纷ǁǂ"]/div/div[2]/a').click()
    time.sleep(1)
    num = web.find_element(By.XPATH,
                           value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010010000劳动合同纠纷/01060010010040劳务派遣合同纠纷ǁǂ"]/div/div[2]/div').text
    time.sleep(1)

    return num


# 打开经济补偿纠纷 Severance Disputes
def setfilter_openlabour_dispute_Contract_SD(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010010000劳动合同纠纷/01060010010070经济补偿金纠纷ǁǂ"]/div/div[2]/a').click()
    time.sleep(2)
    num = web.find_element(By.XPATH,
                           value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010010000劳动合同纠纷/01060010010070经济补偿金纠纷ǁǂ"]/div/div[2]/div').text
    return num


# 打开社会保险
def setfilter_openlabour_dispute_social(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010020000社会保险纠纷ǁǂ"]/div/div[2]/a').click()
    time.sleep(1)


# 打开养老保险待遇纠纷 Disputes over pension insurance treatment
def setfilter_openlabour_dispute_social_DPIT(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010020000社会保险纠纷/01060010020020养老保险待遇纠纷ǁǂ"]/div/div[2]/a').click()
    time.sleep(2)
    num = web.find_element(By.XPATH,
                           value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010020000社会保险纠纷/01060010020020养老保险待遇纠纷ǁǂ"]/div/div[2]/div').text

    return num


# 工伤保险待遇纠纷 Work-related injury insurance treatment disputes
def setfilter_openlabour_dispute_social_WRID(web):
    web.find_element(By.XPATH,
                     value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010020000社会保险纠纷/01060010020030工伤保险待遇纠纷ǁǂ"]/div/div[2]/a').click()
    time.sleep(2)
    num = web.find_element(By.XPATH,
                           value='//*[@id="tree_causeOfActionǁ01000000000000民事/01060000000000劳动争议、人事争议/01060010000000劳动争议/01060010020000社会保险纠纷/01060010020030工伤保险待遇纠纷ǁǂ"]/div/div[2]/div').text
    return num


# 设置过滤条件
def setfilter(web, years):
    logging.info('start setfilter')

    # 选择基层
    web.find_element(By.XPATH, value='//*[@id="tree_courtLevelǁ4ǁǂ"]/div/div[2]/a').click()
    time.sleep(3)
    # 选择最近三年
    od, nd = getDateForFilter(years)

    web.find_element(By.XPATH,
                     value='//*[@id="tree_judgmentYearǁ[' + od + " TO " + nd + '}ǁjudgmentDateǁǂ"]/div/div[2]/a').click()
    time.sleep(3)
    # 选择50w元以下
    web.find_element(By.XPATH, value='//*[@id="tree_subjectFeeLevelǁ02ǁǂ"]/div/div[2]/a').click()
    time.sleep(3)
    # 选择案件受理费
    web.find_element(By.XPATH, value='//*[@id="tree_courtAcceptanceFeeLevelǁ02ǁǂ"]/div/div[2]/a').click()
    time.sleep(3)

    # 打开民事
    setfilter_openCivil(web)
    # 打开劳动争议1
    setfilter_openlabour(web)
    # 打开劳动争议2
    setfilter_openlabour_dispute(web)
    # 打开劳动合同保险
    setfilter_openlabour_dispute_Contract(web)
    # 追索劳动报酬纠纷
    num = setfilter_openlabour_dispute_Contract_RTLR(web)

    count = re.findall("\d+", num)[0]
    return int(count)
#设置开始页面
def setStartPage(start):
    for i in range(start):
        nextPage(web)
        time.sleep(4)
#生成保存文件名
def setfileName(int,file):
    return ''.join(file) + str(int) + '.json'
if __name__ == '__main__':
    us = os.path.expanduser('~')

    user = us.split('\\')[-1]
    # 设置本地用户
    userpath = r'--user-data-dir=C:\Users\{}\AppData\Local\Google\Chrome\User Data\Default'.format(user)
    # 打开浏览器
    web = openChrome(userpath)
    web.get("https://law.wkinfo.com.cn/")

    key = "劳动争议"
    # 查考关键字
    SearchKey(web, key)
    years = 3
    s = setfilter(web, years)
    print(s)
    print(type(s))
    # 设置每页条数
    SetPageCount(web, '25')
    # 获取总量
    laws = s
    # 如果每页50条，则需要翻页多ti次
    ti = math.ceil(laws / 25)
    #从181页开始
    start=181
    setStartPage(start)
    print('===============================', ti)
    for i in range(start, ti):
        start = 1
        end = 25
        # 调用获取多条案例方法，返回list为50条的json数组格式，当遇见异常时，flag为1
        samplelist, runtimeflag = getMoreSample(web, start, end)

        # 生成文件名字
        filename=setfileName(i,'追索劳动报酬纠纷')

        # 如果json数组不为空则存到本地
        if len(samplelist) > 1:
            print(filename)
            saveJsonToLocal(samplelist, filename)
        # 根据flag判断执行，当没出现异常时
        if runtimeflag == 0:
            # 将此页获取的25条json打包成文件发送到邮箱中
            sendEmail(filename, ['2923863607@qq.com'])
            sendEmail(filename, ['a8cake@hotmail.com'])
            print('得到一页')
        # 出现异常时
        else:
            print('出现问题')
            # 发送错误的消息到email
            sendEmail('error.txt', ['a8cake@hotmail.com'])
            sendEmail('spiderlog.txt', ['2923863607@qq.com'])
            sendEmail('spiderlog.txt', ['a8cake@hotmail.com'])
            # #终止程序
            sys.exit()
        # 运行无异常，翻页
        nextPage(web)
