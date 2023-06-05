import pandas as pd
import json
# 判断字符是否为汉字
def is_chinese(char):
    if '\u4e00' <= char <= '\u9fff':
        return True
    else:
        return False
def ifisallnum(x,special,chinese=0):#如果全是字母,数字和特殊符号，返回0，否则返回原字符串
    if special:nums=special
    else:nums = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x',
            'c', 'v', 'b', 'n', 'm',
            'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Z', 'X',
            'C', 'V', 'B', 'N', 'M',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '`', '[', '{', ']', '}', '\\', '|',
            ';', ':', '\'', '\"', ',', '<',
            '.', '>', '/', '?', ' ', '。', '~', '`', '「', '」', '　', '）', '（', '：', '・', '♡', '？', '２', '＝', '【', '】',
            '％', '’', '『', '』',
            '…', '！', '＋', '❤', '÷', '×', '•', 'Ք', 'Փ', 'Ւ', 'Ց', 'Ր', 'Տ', 'Վ', 'Ս', 'Ռ', 'Ջ', 'Պ', 'Չ', 'Ո', 'Շ', 'Ն',
            'Յ', 'Մ', 'Ճ', 'Ղ', 'Ձ',
            'Հ', 'Կ', 'Ծ', 'Խ', 'Լ', 'Ի', 'Ժ', 'Թ', 'Ը', 'Է', 'Զ', 'Ե', 'Դ', 'Գ', 'Բ', 'Ա', 'ჵ', 'ჰ', 'ჯ', 'ჴ', 'ხ',
            'ჭ', 'წ', 'ძ', 'ც', 'ჩ', 'შ', 'ყ',
            'ღ', 'ქ', 'ფ', 'ჳ', 'ტ', 'ს', 'რ', 'ჟ', 'პ', 'ო', 'ჲ', 'ნ', 'მ', 'ლ', 'კ', 'ი', 'თ', 'ჱ', 'ზ', 'ვ', 'ე',
            'დ', 'გ', 'ბ', 'ა', '、', '◦', '◾',
            '〇', '一', '二', '三', '四', '五', '六', '七', '八', '九', '�', '×', '｜','子','丑','寅','卯','辰','巳','午',
            '未','申','酉','戌','亥','甲','乙','丙','丁','戊','己','庚','辛','壬','癸',
            '零','十','百','千','萬','負','※','”','☆']
    res=x
    if chinese:
        for i in x:
            if is_chinese(i):
                res=res.replace(i,'')
            if not len(res):return 0
    for i in nums:
        res=res.replace(i,'')
        if not len(res):
            break
    if len(res):
        return x
    else:return 0
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

try:
    f = open('config.json', encoding='utf8')
    config = json.load(f)
    f.close()
    cleaner=config['cleaner']
    chinese=config['chinese']
    special=config['special']
except:
    cleaner=1
    special=0
    print('没有找到config.json，默认使用cleaner功能\r\n\r\n')
target=readjson('ManualTransFile.json')
trsdata=readjson('TrsData.bin')
#剔除无用字符
print('处理中，请稍等………………')
if cleaner:
    for j in range(0, len(target) - 1):
        if not ifisallnum(target.loc[j, 'src'],special,chinese): target.drop([j], axis=0, inplace=True)
#将索引设为原文
target.index=target['src']
for i in trsdata['src']:
    if i in target.index:target.drop([i], axis=0, inplace=True)
tojson(target,'untrs_ManualTransFile.json')
input('已将未翻译部分保存为untrs_ManualTransFile.json')
