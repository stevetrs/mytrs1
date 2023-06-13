import pandas as pd
import json
import re

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
    except:
        input('程序出错：请确保在同文件夹内存在'+name+'文件\r\n\r\n')
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
    except:
        f1 = open('{}_fail.txt'.format(name), 'w', encoding='utf8')
        print(data, file=f1)
        f1.close()
        return 0

target=readjson('ManualTransFile.json')
trsdata=readjson('TrsData.bin')
#剔除无用字符
print('处理中，请稍等………………')
if cleaner1:
    for j in range(0, len(target)):
        if not cleaner(target.loc[j, 'src']): target.drop([j], axis=0, inplace=True)
#将索引设为原文
target.index=target['src']
for i in trsdata['src']:
    if i in target.index:target.drop([i], axis=0, inplace=True)
tojson(target,'untrs_ManualTransFile.json')
input('已将未翻译部分保存为untrs_ManualTransFile.json')
