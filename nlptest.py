import jieba
import logging
import json
import matplotlib.pyplot as plt
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer
#连接数据库
def getCon():
   # db = pymysql.connect(host="localhost", user="root", password="0530", database="laws", port=3306, charset='utf8')
    db = pymysql.connect(host="sh-cynosdbmysql-grp-3ngsmilu.sql.tencentcdb.com", user="Dison_readwrite", password="Dison@2022", database="law_case_source", port=22296, charset='utf8')
    # course = db.cursor()

    # sql = 'select * from hualu '
    # course.execute(sql)
    # res = course.fetchone()
    # print(res)
    return db

def SetContent(filepath):
    with open(filepath,'r',encoding='utf8') as f:
        jd = json.load(f)
        titlels=[]
        for i in jd:
            titlels.append(jd[i]['title'])
        return titlels
#  设置停用词使用本地文件路径
def SetStopWords(filepath):
    logging.info("start SetStopWords")
    stopword_list = []
    with open(filepath, 'r+', encoding='utf8') as f:
        for word in f.readlines():
            if len(word) > 0 and word != '\n\t':
                stopword_list.append(word)
    return stopword_list
###使用停用词过滤 返回Keywords已经keywords.count
def GetKeyWords(content, stopword_list):
    logging.info("start GetKeyWords")
    wordcount = {}
    # print(content)
    for i in content:
        # for j in i:
        #     print(j)
            for word in jieba.cut(i):
                if len(word) > 1 and word not in stopword_list:
                    wordcount[word] = wordcount.get(word, 0) + 1
        #return wordcount
    return sorted(wordcount.items(), key=lambda x: x[1], reverse=True)
def wordseg(str):
    logging.info("start wordseg")
    spf = 'cn_stopwords.txt'
    sp = SetStopWords(spf)
    keys = []
    for i in str:
        #for j in i:i
            for word in jieba.cut(i):
                if len(word) > 1 and word not in sp:
                    keys.append(word)
                    return keys
#从数据库获取fullcontent
def GetFactFromDb(db,start,end):
    res=[]
    facts = []
    course=db.cursor()
    for i in range(start,end):
        sql="select Facts from weikecase_v1 where id={}".format(i)
        course.execute(sql)
        temp=course.fetchall()
        res.append(temp)
    db.close()
    for i in range(len(res)):
        print(res[i][0][0])
        facts.append(res[i][0][0])
    return facts
##将关键字存取到本地文件
def KeyWordstofile(filepath, keywords):
    logging.info("start KeyWordstofile")
    fw = open(filepath, 'w',encoding='utf8')
    for line in keywords:
        for a in line:
            fw.write(str(a))
            fw.write("\t")
        fw.write('\n')
    fw.close()
# 使用传入的keywords 字典生成图表保存到本地,
def generateGraph(topkeywords, imgpaht):
    logging.info("start generateGraph")
    xwords = []
    ycount = []
    for i, j in topkeywords:
        xwords.append(i)
        ycount.append(j)
    fig = plt.figure(figsize=(50, 20))
    plt.bar(xwords, ycount, 0.9, color='green')
    plt.xticks(rotation=60)
    plt.xlabel(u"keywords")
    plt.ylabel(u"count")
    plt.title(u"100关键词统计图")
    plt.savefig(imgpaht)
    plt.show()

if __name__ == '__main__':
    db=getCon()
    facts =GetFactFromDb(db,51,152)
    #print(tl)
    swfp='cn_stopwords.txt'
    #print(wordseg(facts))
    fk=GetKeyWords(facts,swfp)
    print(len(fk))
    print(fk)
    #KeyWordstofile('fkwords.txt',fk)

    #generateGraph(fk[:100],'test.jpg')
    #print(GetKeyWords(dec,swfp))
    #cutlst=wordseg(facts)
    # print(cutlst)
    # vectorizer = TfidfVectorizer()
    # # cutWordList是文章分词后得到的列表，tf_matrix即是得到的文章或者句子的向量
    # tf_matrix = vectorizer.fit_transform(cutlst).toarray()
    # print( vectorizer.get_feature_names_out())
    # print(tf_matrix)


