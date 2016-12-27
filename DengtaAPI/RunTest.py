#encoding=utf8
'''
Created on 2015-12-14

@author: johnson
'''

import sys,os,shutil
import random
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr,COMMASPACE
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from Common import DT_Common,model,DT_Excel,DT_HttpBase


GlobalData=model.GData()

def InitEnv():
    GlobalData.path = sys.path[0]
    GlobalData.sep = os.path.sep
    GlobalData.host =DT_Common.getIniFile("Host","masterHost")
    GlobalData.newsHost=DT_Common.getIniFile("Host","newsHost")
    GlobalData.port = DT_Common.getIniFile("Host","Port")



    now_time=DT_Common.getTime(0)

    #创建report文件
    if not os.path.exists(GlobalData.path + GlobalData.sep +"report" ):
        os.mkdir(GlobalData.path + GlobalData.sep +"report" )

    report_path=GlobalData.path + GlobalData.sep +"report"+ GlobalData.sep +"report_"+now_time+".xls"
    shutil.copy(GlobalData.path + GlobalData.sep +"Data"+ GlobalData.sep +"api.xls",report_path)
    log_path =GlobalData.path + GlobalData.sep +"report"+ GlobalData.sep +"log_"+now_time+".txt"

    GlobalData.reportFile = report_path
    GlobalData.log = log_path
    logObj=DT_Common.logToFile(log_path)
    return  (report_path,logObj)

def GetTestApi(file):

    colNameList=["CaseName","DataType","ReqType","ReqUrl","ReqPara"]
    reqData = DT_Excel.getColumnDataByName(file,colNameList)

    return reqData

def GetTestData(file,runType):

    colNameList=["HuShen","GangGu","MeiGu","HS-ZhiShu","GG-ZhiShu","MG-ZhiShu","BanKuai","XinSanBan","JiJin"]
    testData = DT_Excel.getColumnDataByName(file,colNameList)

    data={}
    if runType == "small" :
        for k in testData:
            temp=[]
            randomInt = random.randint(0,len(testData[k])-1)
            # print("randomInt:"+str(randomInt)+";len "+ k +":"+str(len(testData[k])))
            temp.append(testData[k][randomInt])
            data[k]=temp
    else:
        data=testData

    data["Common"]=data["HuShen"]
    return data

def sendEmail(Memail):
    '''

    :param f: 附件路径
    :param to_addr:发给的人 []
    :return:
    '''
    from_addr = Memail.mail_user
    password = Memail.mail_pass
    to_addr =Memail.to_addr
    smtp_server = Memail.mail_host

    msg = MIMEMultipart()

    # msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
    msg['From'] = from_addr
    msg['To'] = COMMASPACE.join(to_addr)


    if os.path.exists(Memail.log):
        f=open(Memail.log,"r")
        strBody = f.read()
        f.close()
        strResult="Fail"
    else:
        strBody = "测试通过，详情见附件！"
        strResult="Pass"
        to_addr=["sy5259@163.com"]

    title = Memail.headerMsg + " "+strResult + DT_Common.getTime(1)
    msg['Subject'] = Header(title,'utf-8').encode()

    # strBody ="aa"
    strBody=strBody+"\n"+Memail.exc_sum_time
    msg.attach(MIMEText(strBody, 'plain', 'utf-8'))
    part = MIMEApplication(open(Memail.report, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(Memail.report))
    msg.attach(part)

    # server = smtplib.SMTP_SSL(smtp_server, Memail.port)
    # server.set_debuglevel(1)
    # server.login(from_addr, password)
    # server.sendmail(from_addr, Memail.to_addr, msg.as_string())
    # server.quit()
    smtp = smtplib.SMTP()
    smtp.connect(smtp_server)
#    smtp.connect('smtp.163.com')
    smtp.login(from_addr,password)
    smtp.sendmail(from_addr,to_addr, msg.as_string())
    smtp.quit()

# #检查请求返回是否正常
# def analyzeResponse(result):
#     result = True
#     if result["iRet"] == 0:
#         return "Pass"
#     else:
#         return "Fail"

# # 检查返回值是否正确
# def analyzeResponse(expectValue, responseValue):
#     result = True
#
#
#     if result:
#         return "Pass"
#     else:
#         return "Fail"

#执行测试脚本
def runTest(runType):
    #null
    (report_path,logObj)= InitEnv()
    testApi = GetTestApi(report_path)
    testData = GetTestData(GlobalData.path + GlobalData.sep +"Data"+ GlobalData.sep +"data.xls",runType)


    print(DT_Common.getTime(1))
    httpObj =DT_HttpBase.ConfigHttp(GlobalData)
    resultStatusList=[]
    resultTimeList=[]
    exc_sum_time=0
    resultFlag=True

    for i in range(0, len(testApi["ReqUrl"])):
        reqUrl = testApi["ReqUrl"][i] + "?" + testApi["ReqPara"][i]
        reqDataList=testData[testApi["DataType"][i]]                  #list

        if testApi["ReqUrl"][i] =="getNews":
            host=GlobalData.newsHost
        else:
            host=GlobalData.host

        for reqData in reqDataList:
            if "DTCODE" in reqUrl:
                reqUrl=reqUrl.replace("DTCODE",reqData)


            if GlobalData.port != "":
                reqUrl = "http://" + host + ":" +GlobalData.port + "/" + reqUrl
            else:
                reqUrl = "http://" + host + "/" + reqUrl

            if testApi["ReqType"][i] == "GET":
                reqResult = httpObj.get(reqUrl)
            elif testApi["ReqType"][i] == "POST":
                postUrl=reqUrl.split("&")
                reqResult = httpObj.post(postUrl[0],data=postUrl[1])

            int_exc_time=int(reqResult["exc_time"]/1000)
            exc_sum_time=exc_sum_time+int_exc_time
            exc_time=str(int_exc_time)+"ms"
            resultTimeList.append(exc_time)
            if reqResult["status_code"] == 200:
                if reqResult["ret"] == 0:
                    resultStatusList.append("Pass")
                    # actualResult = reqResult["content"]
                    actualResult = "Pass"
                else:
                    resultFlag=False

                    resultStatusList.append("Fail")
                    actualResult=reqResult["ErrorMsg"]
                    # print(type(testApi["CaseName"][i]))
                    # print(reqResult["ErrorMsg"])
                    # print(exc_time)
                    # print(reqUrl)
                    logObj.record(testApi["CaseName"][i]+" "+reqResult["ErrorMsg"]+" "+exc_time+" "+reqUrl)
            else:
                resultFlag = False
                resultStatusList.append("Fail")
                actualResult=reqResult["status_code"]
                print(testApi["CaseName"][i]+" "+str(reqResult["status_code"])+" "+exc_time+" "+reqUrl)
                logObj.record(testApi["CaseName"][i]+" "+str(reqResult["status_code"])+" "+exc_time+" "+reqUrl)
            DT_Excel.updateDataByColumnName(report_path, "actual result", i + 1, actualResult)
            DT_Excel.updateDataByColumnName(report_path, "actual URL", i + 1, reqUrl)
            DT_Excel.updateDataByColumnName(report_path, "exc time", i + 1,exc_time)

    if runType=="small":
        DT_Excel.updateColumnByColumnName(report_path,"result",resultStatusList)


    MemailType=model.emailData()
    Memail = DT_Common.read_email(MemailType)
    Memail.report=GlobalData.reportFile
    Memail.log=GlobalData.log
    Memail.exc_sum_time=str(exc_sum_time)+"ms"
    sendEmail(Memail)
    print(DT_Common.getTime(1))
    print("exc time:"+str(exc_sum_time)+"ms")

if __name__ == "__main__":
    if len(sys.argv)==1:
        runType="small"
    else:
        runType=sys.argv[1]
    runTest(runType)  #runType :small  full