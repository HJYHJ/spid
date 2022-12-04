import pymysql
import json
import emoji


# 获取数据库连接
def getDbCon():
    #db = pymysql.connect(host="localhost", user="root", password="0530", database="laws", port=3306, charset='utf8')
    db = pymysql.connect(host="sh-cynosdbmysql-grp-3ngsmilu.sql.tencentcdb.com", user="Dison_readwrite",password="Dison@2022", database="law_case_source", port=22296, charset='utf8')
    return db


# 获取json文件里面的数据
def GetDatafromJson(filenpath):
    with open(filenpath, 'r', encoding='utf-8')as f:
        js = json.load(f)
    return js


# 设置文件路径，方便批量插入
def SetFilePath(filename, star, end):
    filenamelist = []
    for i in range(star, end + 1):
        filenamelist.append(filename + str(i) + '.json')
    return filenamelist


# 插入到华律表中
def insertDataToHualu(js, db):
    course = db.cursor()
    for i in js:
        title = js[i]['title'][0]

        an = js[i]['answernum']

        answer = js[i]['answer']

        sql = r'INSERT INTO hualu(title,answerNum,answer)values("{}","{}","{}")'.format(title, an, emoji.demojize(
            str(answer).replace("\"", '')))
        #print(sql)
        course.execute(sql)
    db.commit()
    db.close()


def insertDataToWk(js, db):
    course = db.cursor()
    for i in js:
        title = js[i]['title']

        court = js[i]['法院']

        case_no = js[i]['案号']

        date = js[i]['date']

        anyou = js[i]['案由']

        laws = js[i]['law']

        fulltext = js[i]['fulltext']
        fulltext = str(fulltext).replace("\"", '')

        sql = r'INSERT INTO weikecase(title,court,caseNo,date,category,legalTerms,fullContent)values( "{}","{}","{}","{}","{}","{}","{}")'.format(
            title, court, case_no, date, anyou, laws, fulltext)

        course.execute(sql)
    db.commit()
    db.close()


# 获取所有的全文from数据库
def GetAllFullcontentFromDb(db):
    course = db.cursor()
    sql = "select fullContent from weikeCase_v1"
    course.execute(sql)
    Fullcontent = course.fetchall()
    return Fullcontent


# 处理全文中的数据，分解fullcontent 为facts，Dec,exec
def delFullContent(fullContent):
    StringFullContent = fullContent[0][0]

    lsFullContent = StringFullContent.split('\n')

    tempofFacts = None
    Decision = None
    exection = None
    for i in range(len(lsFullContent)):

        if '裁定如下' in lsFullContent[i]:
            tempofFacts = lsFullContent[:i]
            Decision = lsFullContent[i]
            exection = lsFullContent[i + 1:]
            break
    facts = []
    j = 0
    #如果tempofFacts不为NOne
    if tempofFacts:
        for i in tempofFacts:
            if not facts_is_available(i):
                facts = tempofFacts[j:]
                break
            j = j + 1
    return facts, Decision, exection

#
def facts_is_available(partOfFacts):
    #print('llllllllllllllllllllllllllllllllllllllllllllllllll', len(partOfFacts))
    stepwrods=['人:', '人：','申请执行人','被执行人', '法定代表人','负责人','统一信用社','代理人','经营者']
    if len(partOfFacts) < 100:
        for i in stepwrods:
            if i in partOfFacts:
                print("匹配到无效句段")
                print(partOfFacts)
                return True
    else:
        return False

#
def insertDataToWk_v1(db, start, end):
    course = db.cursor()
    for i in range(start, end):
        sql = "select fullContent from weikeCase_v1 where id ={}".format(i)
        course.execute(sql)
        fullContent = course.fetchall()
        print("=================================")
        print(fullContent)
        #如果 fullcontent不为空
        if len(fullContent)>0:
            fact, des, exec = delFullContent(fullContent)
            print("facts=========")
            print(fact)
            print("Decision=========")
            print(des)
            print("exection=========")
            print(exec)
            updatesql = 'UPDATE weikeCase_v1 set Facts="{}",Decision="{}",Execution="{}" where id="{}"'.format(fact, des,
                                                                                                               exec, i)
            try:
                course.execute(updatesql)
            except:
                db.rollback()
            finally:

                db.commit()
        else:
            pass
    db.close()


if __name__ == '__main__':
    db = getDbCon()

    insertDataToWk_v1(db, 6261, 6377)
