import json
import re
import traceback
try:
    f = open('config.json', encoding='utf8')
    config = json.load(f)
    f.close()
    cleaner1=config['cleaner']
except:
    cleaner1=1
    config={'ja':True,'en':False}
    print('没有找到config.json，默认使用cleaner功能\r\n\r\n')
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

data=readjson('ManualTransFile.json')
trsdata=readjson('TrsData.bin')
#剔除无用字符
print('处理中，请稍等………………')
if cleaner1:
    for key in data.keys():
        if not cleaner(key): del data[key]
#将索引设为原文
for key in trsdata.keys():
    if key in data.keys():del data[key]
tojson(data,'untrs_ManualTransFile.json')
input('已将未翻译部分保存为untrs_ManualTransFile.json')
