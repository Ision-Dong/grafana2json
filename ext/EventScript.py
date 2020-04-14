# -*- coding: utf-8 -*-
import logging
import re
import time
import threading

import requests
import configparser

user = 'dcmadmin'
passwords = '83b1733b1fb61f90a9a55ce66d0bc0c360a3905f3ddeef3d5c2f34d98ad1efae'
logginApi = 'https://192.168.19.5:8643/DcmConsole/login/login'
entityApi= 'https://192.168.19.5:8643/DcmConsole/modeling/enumerateDirectChildren'
lastdataApi = 'https://192.168.19.5:8643/DcmConsole/data/getLatestEntityData'
eventApi = 'https://192.168.19.5:8643/DcmConsole/event/enumerateEventData'
count = 'https://192.168.19.5:8643/DcmConsole/modeling/statisticDeviceStatus'
zabbixApi = 'http://192.168.2.186/zabbix/api_jsonrpc.php'


# config = configparser.ConfigParser()
# config.read('./config.ini')
# setions = config.sections()

class GetEventer:

    def __init__(self):

        self.r = requests.session()

    def DCMloggin(self):

        data = {
            'requestObj':
                {
                    'name': user,
                    'password': passwords
                }
        }
        response = self.r.post(logginApi,json=data,verify=False)
        cookie = requests.utils.dict_from_cookiejar(response.cookies)

        return cookie['JSESSIONID']

    def getDCMEvenList(self):

        data ={
            'antiCSRFId': self.DCMloggin(),
            'requestObj': {'id': -1},
            'criteriaObj':{
                'sortObj':[{'field':'timestamp','order':2}]
            }
        }
        response = self.r.post(eventApi,json=data)
        result = eval(re.sub('false', 'False', response.text))

        for i in result['responseObj']:
            yield {
                    'hostname':i['entityName'],
                    'serious': i['severity'],
                    'event':{
                        'timestamp':i['timestamp']['time'],
                        'assetTag':i['assetTag'],
                        'eventType':i['eventType'],
                        'description':i['description']
                    }
            }

    def getDCMcount(self):

        data = {
            'antiCSRFId': self.DCMloggin()
        }

        response = self.r.post(count, verify=False,json=data)
        result = eval(response.text)
        return (result['responseObj']['total'],result['responseObj']['unhealthy'],result['responseObj']['powerOff'],\
                result['responseObj']['unmanaged'],result['responseObj']['total']-result['responseObj']['powerOff'])

    def ZABBIXlogin(self):

        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": "Admin",
                "password": "zabbix"
            },
            "id": 1,
            "auth": None
        }

        url = zabbixApi
        response = self.r.post(url, json=data)
        return eval(response.text)['result']

    def getZABBIXHost(self):

        token = self.ZABBIXlogin()

        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": [
                    "hostid",
                    "host"
                ],
                "selectInterfaces": [
                    "interfaceid",
                    "ip"
                ]
            },
            "id": 2,
            "auth": token
        }
        response = self.r.post(zabbixApi, json=data)
        return response.text

class DataProcessor:
    def __init__(self):
        self.g = GetEventer()
        self.action = {
            '1':'serious',
            '2':'wrong',
            '3':'warning',
            '4':'information'
        }

    def put2Count(self):

        result = self.g.getDCMcount()
        times = time.gmtime(time.time())
        evertime = time.mktime(time.strptime('%s-%s-%s 00:00:00'%(times.tm_year,times.tm_mon,times.tm_mday),
                                             '%Y-%m-%d %X'))
        while True:
            print('正在执行put2Count函数.....')
            serious = warning = 0
            for i in self.g.getDCMEvenList():
                if int(str(i['event']['timestamp'])[:-3]) >= evertime:
                    if i['serious'] == 1:
                        serious += 1
                    elif i['serious'] == 3:
                        warning += 1

            self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='COUNT,type=total value=%s' % result[0])
            self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='COUNT,type=unhealthy value=%s' % result[1])
            self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='COUNT,type=powerOff value=%s' % result[2])
            self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='COUNT,type=unmanaged value=%s' % result[3])
            self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='COUNT,type=online value=%s' % result[4])
            self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='COUNT,type=serious value=%s' % serious)
            self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='COUNT,type=warning value=%s' % warning)
            time.sleep(300)

            # return None

    def put2Event(self):

        while True:
            print('正在执行put2Event函数.....')
            datadict = []
            data = self.g.getDCMEvenList()
            for item in data:
                if int(str(item['event']['timestamp'])[:-3]) >= time.time() - 1800:
                    datadict.append((item['hostname'],self.action[str(item['serious'])],item['event']['eventType']\
                                         ,item['event']['description']))
            try:
                for i in datadict:
                    status,eventname,detail = (re.findall(r'Status:(.*?);',i[3]),re.findall(r'Name:(.*?);',i[3]),\
                                               re.findall(r'Detail:(.*)',i[3]))
                    self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='EVENT,hostname=%s,eventname=%s,level=%s,\
                                                                detail=%s value=0'%(i[0],eventname[0].replace(' ','\ '),
                                                                            status[0].replace(' ','\ '),
                                                                            detail[0].replace(' ','\ ')))
                                                                            # status[0].replace(' ','\ '),
                                                                            # detail[0].replace(' ','\ '))
                    # self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='EVENT,hostname=a,eventname=b,level=c,detail=e value=0')
                    # self.g.r.post('http://127.0.0.1:8086/wsrite?db=DCM',data='EVENT,hostname="%s"' % i[0])
                    # self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='EVENT,type=hostname value="%s"' % i[0])
                    # self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='EVENT,type=level value="%s"' % i[1])
                    # self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='EVENT,type=eventType value="%s"' % i[2])
                    # self.g.r.post('http://127.0.0.1:8086/write?db=DCM',data='EVENT,type=description value="%s"' % i[3].replace(' ','\ '))
            except UnicodeEncodeError:
                pass
            time.sleep(1800)

if __name__ == '__main__':

    g = GetEventer()
    print(g.getDCMcount())
    for i in g.getDCMEvenList():
        print(i)
    # for i in g.getDCMEvenList():
    #     print(i)
    # process = DataProcessor()
    #
    # d = DataHandler(dcm)
    # #
    # # t1 = threading.Thread(target=process.put2Count)
    # t2 = threading.Thread(target=process.put2Event)
    # # t3 = threading.Thread(target=d.put)
    #
    # # t1.start()
    # t2.start()
    # # t3.start()
    #
    # print(threading.active_count())
    # # process.put2Event()


'''
influxdb 写入数据的规则：
    1、字符串中有空格，必须要转义。
    2、可以定义key-value 但是value必须是数值，不能为字符串
    3、插入的后一条记录的字段如果比前一条记录的字段要少，则无法写入数据库   ?????
    4、格式：tablename(,)tag=tagvalue,[tag2=tag2value] key=value[,key1=value1]
'''
