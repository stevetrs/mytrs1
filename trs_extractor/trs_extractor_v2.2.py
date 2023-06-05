import json
import os
import traceback

try:
    with open('config.json', 'r', encoding='utf8') as f:
        config = json.load(f)
except:
    input('请确保在同文件夹内存在格式正确的config.json文件')

# 判断字符串是否含有汉字
def is_chinese(string):
    # for i in config['file_extensions']:
    #     if i in string: return False
    for char in string:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False
# 判断数据是否含字符串，且字符串含汉字
def readtype(data):
    tp = type(data)
    if tp == list:
        for i in data:
            if readtype(i):return True
    elif tp == dict:
        for i in data.keys():
            if readtype(data[i]):return True
    elif tp==str and is_chinese(data):return True
    return False
# same用以判断是否为相同数据，从有数据不是list或dict的层级开始判断，若有任一非str数据不等，则same置否
# 返回替换好的json文件
# 如果上一级是dict，则将key传递到下一级（主要用于判断是否是parameters，以判断list能否用旧版直接覆盖）
def readf(untrs_data, trsed_data, same=True,upperkey=0):
    if trsed_data==False or same==False:
        tp = type(untrs_data)
        if tp == list:
            temp = []
            for i in range(0, len(untrs_data)):
                temp.append(readf(untrs_data[i], trsed_data, same))
        elif tp == dict:
            temp = {}
            for i in untrs_data.keys():
                temp[i] = readf(untrs_data[i], trsed_data, same)
        else:return untrs_data
        return temp
    else:
        tp = type(untrs_data)
        tp2 = type(trsed_data)
        if tp == tp2:
            if tp == list:
                temp = []
                pa=False
                # 长度相等
                if len(untrs_data) >= len(trsed_data):
                    lenth=len(trsed_data)
                else:
                    lenth = len(untrs_data)
                    # 如果本级元素内有非list或dict元素，则对数据进行比对，当非str元素不相等时，same置否
                for i in range(0, lenth):
                    typ = type(untrs_data[i])
                    typ2 = type(trsed_data[i])
                    if typ not in [list, dict]:
                        if typ != typ2:
                            same = False
                        elif (not readtype(trsed_data[i])) and untrs_data[i] != trsed_data[i]:
                            same = False
                # 长度不等
                if len(untrs_data) != len(trsed_data):
                    # 只对上级是dict，且key在config内的list进行旧版覆盖新版
                    if readtype(trsed_data) and config['difflist'] and upperkey in config['upperkey']:
                        pa = True
                        temp=trsed_data
                        same=False
                    elif not config['difflist2']:
                        same=False
                if not pa:
                    d=len(untrs_data)-len(trsed_data)
                    if d>0:
                        for i in range(0, len(trsed_data)):
                            temp.append(readf(untrs_data[i], trsed_data[i], same))
                        for i in range(len(trsed_data), len(untrs_data)):
                            temp.append(readf(untrs_data[i], False, same))
                    else:
                        for i in range(0, len(untrs_data)):
                            temp.append(readf(untrs_data[i], trsed_data[i], same))
            elif tp == dict:
                temp = {}
                count=0
                for key in trsed_data.keys():
                    # 未翻译文件应该包含有已翻译文件的全部key
                    if key not in untrs_data.keys():
                        same = False
                    else:
                        typ = type(untrs_data[key])
                        typ2 = type(trsed_data[key])
                        if typ not in [list, dict]:
                            if typ != typ2:
                                same = False
                            elif (not readtype(trsed_data[key])) and untrs_data[key] != trsed_data[key]:
                                count+=1
                if count/len(untrs_data)>config['diff']:same=False
                for i in untrs_data.keys():
                    if i in trsed_data.keys():
                        temp[i] = readf(untrs_data[i], trsed_data[i], same,upperkey=i)
                    else:
                        temp[i] = readf(untrs_data[i], False, same,upperkey=i)
            else:
                # 若为字符串，且same为True，进行替换，但仅在字符串含有汉字时进行替换
                if same and tp == str and is_chinese(trsed_data):
                    return trsed_data
                else:
                    return untrs_data
        else:
            return untrs_data
        return temp



try:
    trsed_path=config['trsed_path']
    untrs_path=config['untrs_path']
    trsed_names = os.listdir(trsed_path)
    untrs_names = os.listdir(untrs_path)
except:
    input('请确保config.json内填写的文件路径正确。\r\n'
          'trsed_path为已汉化的游戏路径，untrs_path是未汉化游戏路径，均为指向到data文件夹\r\n'
          r'路径格式应为C:\\new\\新建文件夹\\data\\格式，注意是双反斜杠，data后面也要有\\。')
try:
    for name in untrs_names:
        if name in trsed_names:
            sig=False
            print(f'正在处理{name}')
            try:
                with open(trsed_path+name,'r', encoding='utf8') as f:
                    trsed_data = json.load(f)
            except:
                with open(trsed_path+name,'r', encoding='utf-8-sig') as f:
                    trsed_data = json.load(f)
            try:
                with open(untrs_path+name,'r', encoding='utf8') as f:
                    untrs_data = json.load(f)
            except:
                with open(untrs_path+name,'r', encoding='utf-8-sig') as f:
                    sig=True
                    untrs_data = json.load(f)
            data=readf(untrs_data,trsed_data)
            out=json.dumps(data,ensure_ascii=False)
            if not os.path.exists('data'):os.mkdir('data')
            if sig:
                with open('data\\' + name, 'w', encoding='utf-8-sig') as f1:
                    print(out, file=f1)
            else:
                with open('data\\'+name, 'w', encoding='utf8') as f1:
                    print(out, file=f1)
    input('已全部处理完成，将data文件夹覆盖到data文件夹即可（建议事先备份）。')
except Exception as e:
    print(traceback.format_exc())
    print(e)
    input('程序出错，请复制错误信息并上报bug,如报错涉及到具体文件，请同时提供此文件')