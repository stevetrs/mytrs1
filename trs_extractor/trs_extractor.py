import json
import os
import traceback
try:
    with open('config.json', 'r', encoding='utf8') as f:
        config = json.load(f)
except:
    input('请确保在同文件夹内存在格式正确的config.json文件')
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
                    trsed_datalist = json.load(f)
            except:
                with open(trsed_path+name,'r', encoding='utf-8-sig') as f:
                    trsed_datalist = json.load(f)
            try:
                with open(untrs_path+name,'r', encoding='utf8') as f:
                    untrs_datalsit = json.load(f)
            except:
                with open(untrs_path+name,'r', encoding='utf-8-sig') as f:
                    untrs_datalsit = json.load(f)
            if type(trsed_datalist)==list and trsed_datalist[0]==None:
                trsed_datalist.pop(0)
            if name=='CommonEvents.json':
                for j in range(1, len(untrs_datalsit)):
                    # 打开相同的id的dict
                    id = untrs_datalsit[j]['id']
                    for temp in trsed_datalist:
                        if temp['id'] == id:
                            trsed_data = temp
                            trsed_datalist.remove(temp)
                            break
                    if untrs_datalsit[j]['switchId']==trsed_data['switchId'] and untrs_datalsit[j]['trigger'] == trsed_data['trigger']:
                        trsed_list=trsed_data['list']
                        # 如果基本信息匹配，对未翻译文件的list遍历，找到已翻译文件中对应‘code’的dict，对其中的parameters进行比对，如不相同则存入待导出dict
                        for jj in range(0,len(untrs_datalsit[j]['list'])):
                            temp=False
                            code=untrs_datalsit[j]['list'][jj]['code']
                            indent = untrs_datalsit[j]['list'][jj]['indent']
                            for k in trsed_list:
                                if k['code']==code and k['indent']==indent:
                                    temp=k
                                    # 如果双方长度相等
                                    if len(untrs_datalsit[j]['list'][jj]['parameters'])==len(k['parameters']):
                                        for no in range(0,len(untrs_datalsit[j]['list'][jj]['parameters'])):
                                            if untrs_datalsit[j]['list'][jj]['parameters'][no]!=k['parameters'][no] and type(untrs_datalsit[j]['list'][jj]['parameters'][no])==str:
                                                untrs_datalsit[j]['list'][jj]['parameters'][no]=k['parameters'][no]
                                    break
                            if temp:trsed_list.remove(temp)
            elif name=='Troops.json':
                for j in range(1, len(untrs_datalsit)):
                    # 打开相同的id的dict
                    id = untrs_datalsit[j]['id']
                    for temp in trsed_datalist:
                        if temp['id'] == id:
                            trsed_data = temp
                            trsed_datalist.remove(temp)
                            break
                    # 将翻译后文件定位到list层
                    trsed_pageslist=trsed_data['pages']
                    if untrs_datalsit[j]['members']==trsed_data['members']:
                        for jk in range(0,len(untrs_datalsit[j]['pages'])):
                            conditions=untrs_datalsit[j]['pages'][jk]['conditions']
                            for temp in trsed_pageslist:
                                if temp['conditions'] == conditions:
                                    trsed_pages = temp
                                    trsed_pageslist.remove(temp)
                                    break
                            trsed_list=trsed_pages['list']
                            # 如果基本信息匹配，对未翻译文件的list遍历，找到已翻译文件中对应‘code’的dict，对其中的parameters进行比对，如不相同则存入待导出dict
                            for jj in range(0,len(untrs_datalsit[j]['pages'][jk]['list'])):
                                temp=False
                                code=untrs_datalsit[j]['pages'][jk]['list'][jj]['code']
                                indent = untrs_datalsit[j]['pages'][jk]['list'][jj]['indent']
                                for k in trsed_list:
                                    if k['code']==code and k['indent']==indent:
                                        temp=k
                                        # 如果双方长度相等
                                        if len(untrs_datalsit[j]['pages'][jk]['list'][jj]['parameters'])==len(k['parameters']):
                                            for no in range(0,len(untrs_datalsit[j]['pages'][jk]['list'][jj]['parameters'])):
                                                if untrs_datalsit[j]['pages'][jk]['list'][jj]['parameters'][no]!=k['parameters'][no] and type(untrs_datalsit[j]['pages'][jk]['list'][jj]['parameters'][no])==str:
                                                    untrs_datalsit[j]['pages'][jk]['list'][jj]['parameters'][no]=k['parameters'][no]
                                        break
                                if temp:trsed_list.remove(temp)
            # 如除字符串以外所有数据均相同，则对字符串进行替换
            elif name in ['Actors.json','Armors.json','Classes.json','Enemies.json','Items.json','MapInfos.json','Skills.json','States.json','Weapons.json']:
                for j in range(1, len(untrs_datalsit)):
                    # 打开相同的id的dict
                    id = untrs_datalsit[j]['id']
                    for temp in trsed_datalist:
                        if temp['id'] == id:
                            trsed_data = temp
                            trsed_datalist.remove(temp)
                            break
                    dic = {}  # 用以暂存不相等的键值对
                    same=True
                    for key in untrs_datalsit[j].keys():
                        if key in trsed_data.keys():
                            # 如果数据不是字符串，并且前后不等，说明不是同一组数据
                            if type(untrs_datalsit[j][key])!=str:
                                if untrs_datalsit[j][key]!=trsed_data[key]:
                                    same=False
                            # 如果某个键值是字符串，且前后不相等，替换为翻译后的
                            else:
                                if untrs_datalsit[j][key]!=trsed_data[key]:
                                    dic[key]=trsed_data[key]
                    if same and len(dic):
                        for key in dic.keys():
                            untrs_datalsit[j][key]=dic[key]
            elif name in ['Animations.json','System.json','ContainerProperties.json','Tilesets.json']:continue
            elif 'Map' in name:
                trsed_datalist = trsed_datalist['events']
                while None in trsed_datalist:trsed_datalist.remove(None)
                for j in range(1, len(untrs_datalsit['events'])):
                    # 打开相同的id的dict
                    if untrs_datalsit['events'][j]!=None:
                        id = untrs_datalsit['events'][j]['id']
                        for temp in trsed_datalist:
                            if temp['id'] == id:
                                trsed_data = temp
                                trsed_datalist.remove(temp)
                                break

                        # 将翻译后文件定位到list层
                        trsed_pageslist=trsed_data['pages']
                        for jk in range(0,len(untrs_datalsit['events'][j]['pages'])):
                            conditions=untrs_datalsit['events'][j]['pages'][jk]['conditions']
                            for temp in trsed_pageslist:
                                if temp['conditions'] == conditions:
                                    trsed_pages = temp
                                    trsed_pageslist.remove(temp)
                                    break
                            trsed_list=trsed_pages['list']
                            # 如果基本信息匹配，对未翻译文件的list遍历，找到已翻译文件中对应‘code’的dict，对其中的parameters进行比对，如不相同则存入待导出dict
                            for jj in range(0,len(untrs_datalsit['events'][j]['pages'][jk]['list'])):
                                temp=False
                                code=untrs_datalsit['events'][j]['pages'][jk]['list'][jj]['code']
                                indent = untrs_datalsit['events'][j]['pages'][jk]['list'][jj]['indent']
                                for k in trsed_list:
                                    if k['code']==code and k['indent']==indent:
                                        temp=k
                                        # 如果双方长度相等
                                        if len(untrs_datalsit['events'][j]['pages'][jk]['list'][jj]['parameters'])==len(k['parameters']):
                                            for no in range(0,len(untrs_datalsit['events'][j]['pages'][jk]['list'][jj]['parameters'])):
                                                if untrs_datalsit['events'][j]['pages'][jk]['list'][jj]['parameters'][no]!=k['parameters'][no] and type(untrs_datalsit['events'][j]['pages'][jk]['list'][jj]['parameters'][no])==str:
                                                    untrs_datalsit['events'][j]['pages'][jk]['list'][jj]['parameters'][no]=k['parameters'][no]
                                        break
                                if temp:trsed_list.remove(temp)
            out=json.dumps(untrs_datalsit,ensure_ascii=False)
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
    input('程序出错，请复制错误信息并上报bug')