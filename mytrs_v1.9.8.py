# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document
import requests
import random
import json
import pandas as pd
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
# 读取json为dataframe并重整化行列
def readjson(name):
    try:
        f1 = open(name, encoding='utf8')
        dic1 = json.load(f1)
        data = pd.json_normalize(dic1).T
        data['dst'] = data[0]
        data.columns = ['src', 'dst']
        data['src'] = data.index
        data.index = list(range(0, len(data)))
        return data
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        input('程序出错：请确保在同文件夹内存在'+name+'文件\r\n或存在此文件但文件格式不符合json格式\r\n')
        return 0
#将dataframe导出为名为name的文件
def tojson(data,name):
    try:
        data.index = data['src'].values
        data.drop(['src'],axis=1,inplace=True)
        data.columns=[0]
        out=json.dumps(data.to_dict()[0],indent=4,ensure_ascii=False)
        f1 = open(name, 'w', encoding='utf8')
        print(out, file=f1)
        f1.close()
        return 1
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        data.to_to_excel(f'{name}_fail.xlsx')
        return 0
#百度翻译
def baidu(targ,QPS,NPQ,appid, appkey, from_lang, to_lang,limits,used,last):
    data=targ.loc[targ['2']>=last]  #从上一个引擎中断的位置开始
    q = ''
    error = {}
    l = len(targ)
    t = []
    count = 0
    t.append(time.process_time())
    qt = 1 / QPS    #请求时间间隔
    ib=0    #中断位置
    usage=0 #记录消耗
    s=0 #记录未翻译的位置
    gototrs=0   #是否进入翻译
    temp=0  #临时字符串
    for inta in data.index:
        i=targ.loc[inta,'2']
        #如果temp不是0，把存储内容加入q中，temp归0
        if temp:
            q+=temp
            temp=0
        # 记录字符长度，如果超过NPQ，字符串存在temp中
        lenth=len((q+targ.loc[inta, 'src'] + '\n').encode())
        if lenth<=NPQ or i == len(targ) - 1 or len(q)==0:
            q += targ.loc[inta, 'src'] + '\n'
        else:
            temp = targ.loc[inta, 'src']+ '\n'
            gototrs=1
        if gototrs or i == len(targ) - 1:
            gototrs=0
            usage+=len(q.replace('\n',''))
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
                s = i
                for j in trsres:
                    try:
                        targ.loc[j['src'],'dst']=j['dst'].replace(spr[1], '\n').replace(spr[0],'\r')
                    except Exception as e:
                        print(traceback.format_exc())
                        print(e)
                        error.update(j)
                print('翻译中：{}/{}......\r\n'.format(i + 1, l))
            else:
                print('出错,请前往翻译引擎官网自行对照原因：\r\n', res,'自动切换至下一个翻译引擎（如果有的话），对应消耗量会依次增加\r\n')
                ib=s
                break
            q = ''
        # 如果本次翻译使字符消耗超过限制，中断翻译
        if used + usage +NPQ>= limits and i != len(targ) - 1:
            #如果是最后一个翻译引擎，记录中断位置
            ib = s
            break
    return targ,ib,error,usage
#彩云翻译
def caiyun(targ,token, direction,NPQ,limits,used,last):
    data=targ.loc[targ['2']>=last]  #从上一个引擎中断的位置开始
    q = []
    count = ''
    error = {}
    ib=0
    l = len(targ)
    s=0
    usage=0
    temp=0
    gototrs=0
    for inta in data.index:
        i=targ.loc[inta,'2']
        # 如果temp不是0，把存储内容加入q中，temp归0
        if temp:
            q.append(temp)
            count += temp
            temp = 0
        # 记录字符长度，如果超过NPQ，字符串存在temp中,如果是最后一行字符串刚好超过NPQ限制，也进行翻译
        #因为设置了从长倒短的顺序翻译，所以即使超过限制也不会超出很多，而在limits处的判断有留出一定余量，所以是安全的
        lenth = len(count+targ.loc[inta, 'src'])
        if lenth <= NPQ or i == len(targ) - 1 or len(q)==0:
            q.append(targ.loc[inta, 'src'])
            count += targ.loc[inta, 'src']
        else:
            temp = targ.loc[inta, 'src']
            gototrs = 1
        if gototrs or i == len(targ) - 1:
            gototrs=0
            usage+=len(count)
            res = caiyuntrs(token, direction, q)
            dst = res.get('target', 0)
            if dst:
                s = i
                trsres=[]
                for j in range(0,len(dst)):
                    trsres.append({'src':q[j],'dst':dst[j]})
                for j in trsres:
                    try:
                        targ.loc[j['src'], 'dst'] = j['dst'].replace(spr[1], '\n').replace(spr[0],'\r').replace('☆ _ _ ', '\n').replace('↑ _ _ ','\r')
                    except Exception as e:
                        print(traceback.format_exc())
                        print(e)
                        error.update(j)
                print('翻译中：{}/{}......\r\n'.format(i + 1, l))
            else:
                print('出错,请前往翻译引擎官网自行对照原因：\n', res,'自动切换至下一个翻译引擎（如果有的话），对应消耗量会依次增加\r\n')
                ib = s
                break
            q = []
            count = ''
        if used + usage +NPQ>= limits and i != len(targ) - 1:
            ib=s
            break
    return targ, ib, error,usage
#小牛翻译
def xiaoniu(targ,QPS,NPQ,from_lang, to_lang, dictNo, apikey,limits,used,last):
    data = targ.loc[targ['2'] >= last]  # 从上一个引擎中断的位置开始
    q = ''
    error = {}
    l = len(targ)
    t = []
    count = 0
    t.append(time.process_time())
    qt = 1 / QPS
    ib=0
    usage=0
    s=0
    temp=0
    gototrs=0
    for inta in data.index:
        i=targ.loc[inta,'2']
        #如果temp不是0，把存储内容加入q中，temp归0
        if temp:
            q+=temp
            temp=0
        # 记录字符长度，如果超过NPQ，字符串存在temp中
        lenth=len((q+targ.loc[inta, 'src'] + '\n').encode())
        if lenth<=NPQ or i == len(targ) - 1 or len(q)==0:
            q += targ.loc[inta, 'src'] + '\n'
        else:
            temp = targ.loc[inta, 'src']+ '\n'
            gototrs=1
        if gototrs or i == len(targ) - 1:
            gototrs=0
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
                s = i
                trsres=[]
                q = q.rstrip('\n').split('\n')
                dst=dst.rstrip('\n').split('\n')
                for j in range(0,len(q)):
                    trsres.append({'src':q[j],'dst':dst[j]})
                for j in trsres:
                    try:
                        targ.loc[j['src'], 'dst'] = j['dst'].replace(spr[1], '\n').replace(spr[0],'\r')
                    except Exception as e:
                        print(traceback.format_exc())
                        print(e)
                        error.update(j)
                print('翻译中：{}/{}......\r\n'.format(i + 1, l))
            else:
                print('出错,请前往翻译引擎官网自行对照原因：\n', res,'自动切换至下一个翻译引擎（如果有的话），对应消耗量会依次增加\r\n')
                ib = s
                break
            q = ''
        if used + usage+NPQ >= limits and i != len(targ) - 1:
            ib = s
            break
    return targ, ib, error,usage
#计算引擎余量，文本排序，统计字符数，翻译,运行正常返回target，ib，error或True（n的情况），出bug返回False
def mytrs(target,enginelist):
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
    index1=target.src.str.len().sort_values(ascending=False).index
    target=target.reindex(index1)
    target.index=list(range(0,len(target)))
    #统计字符数
    target['src'] += '↑☆↓☆'
    allstr = target['src'].sum().replace('\r',spr[0]).replace('\n',spr[1])
    total_usage = len(allstr.replace('↑☆↓☆', ''))
    target['2'] = target.index
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
        ib=0
        for i in enginelist:
            engine=i
            #替换字词库,allstr保存原文数据
            dicname = config[engine]['dic']
            if dicname:
                dic = readjson(dicname)
                for k in range(0, len(dic)):
                    allstr = allstr.replace(dic.loc[k, 'src'], dic.loc[k, 'dst'])
            target['src'] = allstr.rstrip('↑☆↓☆').split('↑☆↓☆')
            target.index = target['src']
            #将allstr恢复到原文状态
            if dicname:
                for k in range(0, len(dic)):
                    allstr = allstr.replace(dic.loc[k, 'dst'], dic.loc[k, 'src'])
            # 以最大字符量为间隔创建q,并翻译
            try:
                if 'baidu' in engine:
                    (target,ib,error,usage)=baidu(target,config[engine]['QPS'],config[engine]['NPQ'],config[engine]['appid'],
                                                  config[engine]['appkey'], config[engine]['from_lang'], config[engine]['to_lang']
                                                  ,config[engine]['limits'],config[engine]['usage'],ib)
                elif 'caiyun' in engine:
                    (target,ib,error,usage)=caiyun(target, config[engine]['token'], config[engine]['direction'], config[engine]['NPQ']
                                                   ,config[engine]['limits'],config[engine]['usage'],ib)
                elif 'xiaoniu' in engine:
                    (target,ib,error,usage)=xiaoniu(target,config[engine]['QPS'],config[engine]['NPQ'],config[engine]['from_lang'],
                                                    config[engine]['to_lang'], config[engine]['dictNo'], config[engine]['apikey']
                                                    ,config[engine]['limits'],config[engine]['usage'],ib)
                config[engine]['usage'] += usage
            except Exception as e:
                print(traceback.format_exc())
                print(e)
                print('请确保配置文件config.json格式正确，如果你确定配置文件没问题，请上报bug')
                if tojson(target, 'TrsData.bin'):
                    print('已将翻译数据保存在TrsData.bin内\r\n\r\n')
                else:
                    print('已将翻译数据保存在TrsData.bin_fail.xlsx内\r\n\r\n')
                return False
            target['src'] = allstr.replace(spr[1], '\n').replace(spr[0], '\r').rstrip('↑☆↓☆').split('↑☆↓☆')
            if not ib:break
        #翻译完成，进入最终处理
        del target['2']
        return target,ib,error
    else:return True
def findrep(data,name):
    data.index = list(range(0, len(data)))
    src_rep = config['src_rep']
    dst_rep = config['dst_rep']
    repeatd = {}
    for inde in range(0, len(data)):
        o = True
        for char in data.loc[inde, 'dst']:
            # 如果译文中有连续dst_rep个重复字符，并且原文和译文不相同，标记为异常
            if data.loc[inde, 'dst'].count(char) >= dst_rep and char * dst_rep in data.loc[inde, 'dst'] and data.loc[
                inde, 'src'] != data.loc[inde, 'dst']:
                for chars in data.loc[inde, 'src']:
                    # 如果原文有src_rep个重复字符，就说明译文重复是正常的
                    if data.loc[inde, 'src'].count(chars) >= src_rep and chars * src_rep in data.loc[inde, 'src']:
                        o = False
                if o:  # 如果文本异常，添加进dict
                    repeatd[data.loc[inde, 'src']] = data.loc[inde, 'dst']
    if len(repeatd):
        print(f'检测到有异常译文，已将异常译文保存为{name}.json')
        out = json.dumps(repeatd, indent=4, ensure_ascii=False)
        f1 = open(f'{name}.json', 'w', encoding='utf8')
        print(out, file=f1)
        f1.close()
# 检索翻译结果中是否有连续大量重复字符，如有，导出这些并尝试自动使用backupengine翻译
def retrs(data):
    findrep(data,'repeat')
    backupengine = config['backupengine']
    for engine in backupengine:
        print(f'即将开始使用{engine}重新翻译异常文本')
        repeat = readjson('repeat.json')
        try:
            repeat=mytrs(repeat,[engine])[0]
        # 报错和不翻译的情况，返回False
        except:
            print('重翻译出错，将保存原本的翻译数据')
            return False
        if type(repeat)==bool:return False
        repeat.index = list(range(0, len(repeat)))
        for inde in range(0,len(repeat)):
            ind=data[data.src==repeat.loc[inde,'src']].index
            data.loc[ind,'dst']=repeat.loc[inde,'dst']
        data.index = data['src']
        findrep(data,'repeat')
    return data
# 读取配置文件
try:
    spr = config['spr']
    enginelist=config['enginelist']
    #获取上一次记录的时间和系统时间，若系统时间与记录时间隔了月份，将所有在enginelist内的引擎的字符消耗重置归0
    recordyear=config['recordtime']['year']
    recordmonth=config['recordtime']['month']
    today=datetime.today()
    if today.year*12+today.month-(recordyear*12+recordmonth)>=1:
        for i in enginelist:
            config[i]['usage']=0
except Exception as e:
    print(traceback.format_exc())
    print(e)
    input('请确保config.json格式正确')

#读取ManualTransFile.json并删除无用字符串
target=readjson('ManualTransFile.json')
if config['cleaner']:
    print('剔除无用字符串中，请稍后......\r\n')
    for j in range(0, len(target)):
        if not cleaner(target.loc[j, 'src']):target.drop([j],axis=0,inplace=True)
# 第一次翻译
try:
    target,ib,error=mytrs(target,enginelist)
except:input()
# 再翻译
res=retrs(target)
# 返回结果不为False，再覆盖target
if type(res)!=bool:
    target=res
#如果完整翻译了整个文件，直接导出
if not ib:
    if tojson(target, 'TrsData.bin'):
        print('翻译完成，已保存为TrsData.bin\r\n\r\n')
    else:
        print('翻译完成，但保存出错，将结果临时保存为TrsData.bin_fail.xlsx，请自行转换为json格式\r\n\r\n')
#如果没有完整翻译，将已翻译部分导出为TrsData.bin，未翻译部分导出为untrsed.json
else:
    if ib:
        if tojson(target[:ib], 'TrsData.bin'):
            print('翻译全部未完成，将已翻译部分保存为TrsData.bin\r\n')
        else:
            print('翻译全部未完成，且保存出错，将翻译结果临时保存为TrsData.bin_fail.xlsx，请自行转换为json格式\r\n')
        if tojson(target[ib:], 'untrsed.json'):
            print('翻译全部未完成，将未翻译部分保存为untrsed.json\r\n\r\n')
        else:
            print('翻译全部未完成，且保存出错，将未翻译部分临时保存为untrsed.json_fail.xlsx，请自行转换为json格式\r\n\r\n')
if len(error):
    print('已将翻译失败部分保存为error.json\r\n')
    error_o = json.dumps(error, indent=4, ensure_ascii=False)
    ff=open('error.json','w',encoding='utf8')
    print(error_o,file=ff)
    ff.close()
#更新config
config['recordtime']['year']=today.year
config['recordtime']['month'] = today.month
f = open('config.json','w', encoding='utf8')
out = json.dumps(config, indent=4, ensure_ascii=False)
f.write(out)
f.close()
input()


