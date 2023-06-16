# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document
import requests
import random
import json
from hashlib import md5
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
import traceback
import re

try:
    f = open('config.json', encoding='utf8')
    config = json.load(f)
    f.close()
except Exception as e:
    print(traceback.format_exc())
    print(e)
    input('程序出错：请确保在同文件夹内存在config.json文件\r\n\r\n')

def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()
# 返回字典数组，读取格式为return[i]['dst']
def baidutrs(appid,appkey,from_lang,to_lang,query):
    # Generate salt and sign
    url='https://fanyi-api.baidu.com/api/trans/vip/translate'
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)
    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    return result
def caiyuntrs(token,direction,source):
    url = "http://api.interpreter.caiyunai.com/v1/translator"

    # WARNING, this token is a test token for new developers,
    # and it should be replaced by your token

    payload = {
        "source": source, #目标语言
        "trans_type": direction, #从什么到什么
        "request_id": "demo",
        "detect": True,
    }

    headers = {
        "content-type": "application/json",
        "x-authorization": "token " + token,
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    return response.json()
def xiaoniutrs(sentence, src_lan, tgt_lan, dictNo,apikey):
    url = 'http://api.niutrans.com/NiuTransServer/translation?'
    if dictNo:
        data = {"from": src_lan, "to": tgt_lan, "apikey": apikey, "src_text": sentence,'dictNo':dictNo}
    else:
        data = {"from": src_lan, "to": tgt_lan, "apikey": apikey, "src_text": sentence}
    data_en = urllib.parse.urlencode(data)
    req = url + "&" + data_en
    res = urllib.request.urlopen(req)
    res = res.read()
    res_dict = json.loads(res)
    # if "tgt_text" in res_dict:
    #     result = res_dict['tgt_text']
    # else:
    #     result = res
    return res_dict
# 处理字典，按照规则对译文做替换
def dicreplace(dicname,data):
    # key为字典译文，untrs为原文
    dicname=readjson(dicname)
    for key in dicname:
        for untrs in data.keys():
            # 寻找包含字典译文的字符行
            if key in data[untrs]:
                # 遍历此译文下的字典
                for replcetrs in dicname[key].keys():
                    # 如果没有设置字典原文或字典原文包含在原文中，进行替换
                    if dicname[key][replcetrs]=='' or  dicname[key][replcetrs] in untrs:
                        data[untrs]=data[untrs].replace(key,replcetrs)
    return data
# 如果字符串含中文，返回True
def iszh(s):
    if re.search(r'[\u4e00-\u9fa5]', s):
        return True
    else:
        return False
# 对应语种为True，则当字符串中不存在对应语种字符时，返回False
def cleaner(s,ja=config['ja'],en=config['en']):
    # 如果不存在日语假名，返回False
    if ja:
        if not re.search(r'[\u3040-\u309F\u30A0-\u30FF]',s):return False
    # 英文（任意字母）
    if en:
        if not re.search(r'[a-zA-Z]', s): return False
    return True
# 读取json为dict
def readjson(name):
    try:
        with open(name, encoding='utf8') as f1:
            data = json.load(f1)
        return data
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        input(f'程序出错：请确保在同文件夹内存在{name}文件\r\n或存在此文件但文件格式不符合json格式\r\n')
#将数据导出为名为name的文件
def tojson(data,name):
    out=json.dumps(data,indent=4,ensure_ascii=False)
    with open(name, 'w', encoding='utf8') as f1:
        print(out, file=f1)
    return True
#百度翻译
def baidu(data,sortedkeys,QPS,NPQ,appid, appkey, from_lang, to_lang,limits,used):
    q = ''
    error = {}
    l = len(data)
    t = []
    count = 0
    t.append(time.process_time())
    qt = 1 / QPS    #请求时间间隔
    usage=0 #记录消耗
    gototrs=False   #是否进入翻译
    temp=0  #临时字符串
    copykeys=sortedkeys.copy()
    forlen = len(copykeys) # 循环的长度
    for i in range(0,forlen):
        key=copykeys[i].replace('\r',spr[0]).replace('\n',spr[1])
        #如果temp不是0，把存储内容加入q中，temp归0
        if temp:
            q+=temp
            temp=0
        # 计算q的预计总长度
        lenth=len((q + key + '\n').encode())
        # 在q的预计总长度小于等于NPQ或是最后一行文本或q是空的时，将文本添加进q中
        if lenth<=NPQ or i == forlen - 1 or len(q)==0:
            q += key + '\n'
        # 否则，暂存这一行文本，并进入翻译
        else:
            temp = key+ '\n'
            gototrs=True
        # 如果是最后一行，也进入翻译
        if gototrs or i == forlen - 1:
            gototrs=False
            usage+=len(q.replace('\n','').encode())
            q = q.rstrip('\n')  # 去掉最后一个换行符
            count += 1
            t.append(time.process_time())
            tt = t[count] - t[count - 1]
            if tt < qt:
                time.sleep(qt - tt)
                count += 1
                t.append(time.process_time())
            res = baidutrs(appid, appkey, from_lang, to_lang, q)
            trsres = res.get('trans_result', 0)
            if trsres:
                for j in trsres:
                    try:
                        realkey=j['src'].replace(spr[1], '\n').replace(spr[0],'\r')
                        data[realkey]=j['dst'].replace(spr[1], '\n').replace(spr[0],'\r')
                        sortedkeys.remove(realkey)
                    except Exception as e:
                        print(traceback.format_exc())
                        print(e)
                        error.update(j)
                print('翻译中：{}/{}......\r\n'.format(l-forlen+i, l))
            else:
                print('出错,请前往翻译引擎官网自行对照原因：\r\n', res,'自动切换至下一个翻译引擎（如果有的话），对应消耗量会依次增加\r\n')
                break
            q = ''
        # 如果本次翻译会使下一次翻译超过限制，并且还没有翻译完，中断翻译
        if used + usage +NPQ>= limits and i != forlen - 1:
            break
    return data,sortedkeys,error,usage
#彩云翻译
def caiyun(data,sortedkeys,token, direction,NPQ,limits,used):
    q = []
    count = ''
    error = {}
    l = len(data)
    usage=0
    temp=0
    gototrs=False
    copykeys = sortedkeys.copy()
    forlen=len(copykeys)
    for i in range(0, forlen):
        key = copykeys[i].replace('\r',spr[0]).replace('\n',spr[1])
        # 如果temp不是0，把存储内容加入q中，temp归0
        if temp:
            q.append(temp)
            count += temp
            temp = 0
        # 记录字符长度，如果超过NPQ，字符串存在temp中,如果是最后一行字符串刚好超过NPQ限制，也进行翻译
        #因为设置了从长倒短的顺序翻译，所以即使超过限制也不会超出很多，而在limits处的判断有留出一定余量，所以是安全的
        lenth = len(count+key)
        if lenth <= NPQ or i == forlen - 1 or len(q)==0:
            q.append(key)
            count += key
        else:
            temp = key
            gototrs = True
        if gototrs or i == forlen - 1:
            gototrs=False
            usage+=len(count)
            res = caiyuntrs(token, direction, q)
            dst = res.get('target', 0)
            if dst:
                try:
                    for j in range(0,len(dst)):
                        realkey=q[j].replace(spr[1], '\n').replace(spr[0],'\r')
                        data[realkey]=dst[j].replace(spr[1], '\n').replace(spr[0],'\r')
                        sortedkeys.remove(realkey)
                except Exception as e:
                    print(traceback.format_exc())
                    print(e)
                    error.update(j)
                print('翻译中：{}/{}......\r\n'.format(l-forlen+i, l))
            else:
                print('出错,请前往翻译引擎官网自行对照原因：\n', res,'自动切换至下一个翻译引擎（如果有的话），对应消耗量会依次增加\r\n')
                break
            q = []
            count = ''
        if used + usage +NPQ>= limits and i != forlen - 1:
            break
    return data,sortedkeys,error,usage
#小牛翻译
def xiaoniu(data,sortedkeys,QPS,NPQ,from_lang, to_lang, dictNo, apikey,limits,used):
    q = ''
    error = {}
    l = len(data)
    t = []
    count = 0
    t.append(time.process_time())
    qt = 1 / QPS
    usage=0
    temp=0
    gototrs=False
    copykeys = sortedkeys.copy()
    forlen=len(copykeys)
    for i in range(0, forlen):
        key = copykeys[i].replace('\r',spr[0]).replace('\n',spr[1])
        #如果temp不是0，把存储内容加入q中，temp归0
        if temp:
            q+=temp
            temp=0
        # 记录字符长度，如果超过NPQ，字符串存在temp中
        lenth=len((q+key + '\n').encode())
        if lenth<=NPQ or i == forlen - 1 or len(q)==0:
            q += key + '\n'
        else:
            temp = key+ '\n'
            gototrs=True
        if gototrs or i == forlen - 1:
            gototrs=False
            usage+=len(q.replace('\n',''))
            count += 1
            t.append(time.process_time())
            tt = t[count] - t[count - 1]
            if tt < qt:
                time.sleep(qt - tt)
                count += 1
                t.append(time.process_time())
            res = xiaoniutrs(q, from_lang, to_lang, dictNo, apikey)
            dst = res.get('tgt_text', 0)
            if dst:
                q = q.rstrip('\n').split('\n')
                dst=dst.rstrip('\n').split('\n')
                try:
                    for j in range(0,len(q)):
                        realkey=q[j].replace(spr[1], '\n').replace(spr[0],'\r')
                        data[realkey]=dst[j].replace(spr[1], '\n').replace(spr[0],'\r')
                        sortedkeys.remove(realkey)
                except Exception as e:
                    print(traceback.format_exc())
                    print(e)
                    error.update(j)
                print('翻译中：{}/{}......\r\n'.format(l-forlen+i, l))
            else:
                print('出错,请前往翻译引擎官网自行对照原因：\n', res,'自动切换至下一个翻译引擎（如果有的话），对应消耗量会依次增加\r\n')
                break
            q = ''
        if used + usage+NPQ >= limits and i != forlen - 1:
            break
    return data, sortedkeys, error,usage
#计算引擎余量，文本排序，统计字符数，翻译,运行正常返回target，ib，error或True（n的情况），出bug返回False
def mytrs(data,enginelist):
    #计算所有引擎剩余字符量，剔除无余量引擎
    leftusage=[]
    total_left=0
    for i in enginelist.copy():
        left=config[i]['limits']-config[i]['usage']
        useabelleft=left-config[i]['NPQ']
        if useabelleft<0:enginelist.remove(i)   #如果字符余量不足一次请求，不使用这个引擎
        else:
            leftusage.append(useabelleft)
            total_left+=useabelleft
    #按文本从长到短排序,长文本优先翻译
    sortedkeys=sorted(data.keys(),key=lambda x:len(x),reverse = True)
    #统计字符数
    allstring=''
    for key in sortedkeys:
        allstring+=data[key]
    total_usage = len(allstring)
    while(1):
        if total_left<=total_usage:
            print('剩余总字符量{}百万少于本次翻译需要字符量{}百万\r\n未翻译部分会单独保存为untrsed.json\r\n'.format(total_left/1000000,total_usage/1000000))
        needusage=[]
        sum=0
        for i in leftusage:
            sum+=i
            if sum >= total_usage:
                sum-=i
                x=total_usage-sum
                needusage.append(x)
                sum+=x
                break
            needusage.append(i)
        a=input('本次翻译预计依次消耗{}引擎{}字符，共计{}百万字符，是(y)否(n)进行翻译？\r\n实际每个引擎消耗量可能会略高于此数值，但不会超出字符限制，一个文件总消耗量是固定的\r\n'.format(enginelist[:len(needusage)],needusage,sum/1000000))
        if a=='y' or a=='n':break
    if a == 'y':
        for engine in enginelist:
            # 以最大字符量为间隔创建q,并翻译
            try:
                if 'baidu' in engine:
                    (data,sortedkeys,error,usage)=baidu(data,sortedkeys,config[engine]['QPS'],config[engine]['NPQ'],config[engine]['appid'],
                                                  config[engine]['appkey'], config[engine]['from_lang'], config[engine]['to_lang']
                                                  ,config[engine]['limits'],config[engine]['usage'])
                elif 'caiyun' in engine:
                    (data,sortedkeys,error,usage)=caiyun(data,sortedkeys, config[engine]['token'], config[engine]['direction'], config[engine]['NPQ']
                                                   ,config[engine]['limits'],config[engine]['usage'])
                elif 'xiaoniu' in engine:
                    (data,sortedkeys,error,usage)=xiaoniu(data,sortedkeys,config[engine]['QPS'],config[engine]['NPQ'],config[engine]['from_lang'],
                                                    config[engine]['to_lang'], config[engine]['dictNo'], config[engine]['apikey']
                                                    ,config[engine]['limits'],config[engine]['usage'])
                config[engine]['usage'] += usage
                dicname=config[engine]['dic']
                if dicname:
                    print('正在应用字典，请稍后\r\n')
                    data=dicreplace(dicname,data)
            except Exception as e:
                print(traceback.format_exc())
                print(e)
                print('请确保配置文件config.json格式正确，如果你确定配置文件没问题，请上报bug')
                tojson(data, 'TrsData.bin')
                print('已将翻译数据保存在TrsData.bin内\r\n\r\n')
                return False
            if len(sortedkeys)==0:break
        #翻译完成，进入最终处理
        return data,sortedkeys,error
    else:return True
# 查找异常文本
def findrep(data):
    src_rep = config['src_rep']
    dst_rep = config['dst_rep']
    repeatd = {}
    for key in data.keys():
        o=True
        for char in data[key]:
            # 如果译文中有连续dst_rep个重复字符，并且原文和译文不相同，标记为异常
            if data[key].count(char)>=dst_rep and char*dst_rep in data[key] and data[key]!=key:
                for chars in key:
                    # 如果原文有src_rep个重复字符，就说明译文重复是正常的
                    if key.count(chars)>=src_rep and chars*src_rep in key:
                        o=False
                if o:# 如果文本异常，添加进dict
                    repeatd[key]=data[key]
    return repeatd

# 检索翻译结果中是否有连续大量重复字符，如有，导出这些并尝试自动使用backupengine翻译
def retrs(data,backupengine):
    for engine in backupengine:
        print(f'即将开始使用{engine}重新翻译异常文本\r\n')
        repeat=findrep(data)
        try:
            repeat=mytrs(repeat,[engine])[0]
        # 报错和不翻译的情况，返回False
        except:
            print('重翻译出错，将保存原本的翻译数据\r\n')
            return False
        if type(repeat)==bool:return False
        for key in repeat:
            data[key]=repeat[key]
    repeat = findrep(data)
    if len(repeat):
        print(f'检测到仍有异常译文，已将异常译文保存为repeat.json\r\n')
        out = json.dumps(repeat, indent=4, ensure_ascii=False)
        with open('repeat.json', 'w', encoding='utf8') as f1:
            print(out, file=f1)
    return data


# 读取配置文件
try:
    spr = config['spr'] #换行符的替换符
    enginelist=config['enginelist']
    backupengine=config['backupengine']
    #获取上一次记录的时间和系统时间，若系统时间与记录时间隔了月份，将所有在enginelist内的引擎的字符消耗重置归0
    recordyear=config['recordtime']['year']
    recordmonth=config['recordtime']['month']
    today=datetime.today()
    if today.year*12+today.month-(recordyear*12+recordmonth)>=1:
        for i in enginelist:
            config[i]['usage']=0
        for i in backupengine:
            config[i]['usage']=0
except Exception as e:
    print(traceback.format_exc())
    print(e)
    input('请确保config.json格式正确')

#读取ManualTransFile.json并删除无用字符串
data=readjson('ManualTransFile.json')
if config['cleaner']:
    print('剔除无用字符串中，请稍后......\r\n')
    for key in data.keys():
        if not cleaner(key):del data[key]
# 第一次翻译
try:
    data,sortedkeys,error=mytrs(data,enginelist)
except:input()
# 再翻译
res=retrs(data,backupengine)
# 返回结果不为False，再覆盖target
if type(res)!=bool:
    data=res
#如果完整翻译了整个文件，直接导出
if len(sortedkeys)==0:
    tojson(data, 'TrsData.bin')
    print('翻译完成，已保存为TrsData.bin\r\n\r\n')
#如果没有完整翻译，将已翻译部分导出为TrsData.bin，未翻译部分导出为untrsed.json
else:
    # 删除掉所有未翻译的行
    untrsdic = {}
    for key in sortedkeys:
        del data[key]
        untrsdic[key]=key
    tojson(data,'TrsData.bin')
    print('翻译全部未完成，将已翻译部分保存为TrsData.bin\r\n')
    tojson(untrsdic, 'untrsed.json')
    print('翻译全部未完成，将未翻译部分保存为untrsed.json\r\n\r\n')
if len(error):
    print('已将翻译失败部分保存为error.json\r\n')
    error_o = json.dumps(error, indent=4, ensure_ascii=False)
    with open('error.json','w',encoding='utf8') as ff:
        print(error_o,file=ff)
#更新config
config['recordtime']['year']=today.year
config['recordtime']['month'] = today.month
tojson(config,'config.json')
input()


