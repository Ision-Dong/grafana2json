import logging
import re
import time
import sys
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DCMcontroller:

    def __init__(self):

        self.login = 'https://192.168.19.5:8643/DcmConsole/login/login'
        self.data = 'https://192.168.19.5:8643/DcmConsole/data/getLatestEntityData'
        self.entiy = 'https://192.168.19.5:8643/DcmConsole/modeling/enumerateDirectChildren'
        self.req = requests.session()

    def _gettoken(self):
        data = {
            'requestObj':
                {
                    'name': 'dcmadmin',
                    'password': "83b1733b1fb61f90a9a55ce66d0bc0c360a3905f3ddeef3d5c2f34d98ad1efae"
                }
        }
        self.req.keep_alive = False
        response = self.req.post(self.login,
                            json=data, verify=False)
        cookie = requests.utils.dict_from_cookiejar(response.cookies)
        #antiCSRFId =
        return cookie['JSESSIONID']

    def _getentityId(self):
        antiCSRFId_data = {
            'antiCSRFId': self._gettoken(),
            'requestObj': {'datas': [{'id': -1, 'prop': 'NODE'}]}
        }
        r = self.req.post(self.entiy,
                     json=antiCSRFId_data,
                     verify=False)

        return re.sub('true','True',re.sub('false','False',r.text))

    def getdata(self,id=None):
        get_data = {
            'antiCSRFId': self._gettoken(),
            'requestObj': {"entityId": id, }
        }
        # response = self.req.post(self.data, json=get_data, verify=False)
        # return re.sub('false', 'False', response.text)
        try:
            response = self.req.post(self.data, json=get_data,verify=False)
            return re.sub('false', 'False', response.text)
        except ConnectionError as e :
            response = self.getdata(id)
        finally:
            return re.sub('false', 'False', response.text)

    def get(self):
        return self._getentityId()

class DataHandler:

    def __init__(self,dcm=None):

        if isinstance(dcm,DCMcontroller):
            self.dcm = dcm
        else:
            raise TypeError('loss require args..')

    def _dillwith(self):
        r = self.dcm.get()
        result = eval(r)['responseObj']['entityList']
        # ip = eval(r)['responseObj']['ipAddress']


        for item in result:
            d = self.dcm.getdata(item['id'])
            templ = eval(d)['responseObj']['data'][0]['value']
            power = eval(d)['responseObj']['data'][1]['value']
            ip = eval(d)['responseObj'].get('ipAddress','No IP')
            # timestamp = eval(d)['responseObj']['data'][0]['time']['time']
            yield (ip,templ,power)

    def put(self):
        r = requests.session()

        while True:
            print('正在执行put函数.....')
            logging.info('putting datas... ...')
            for item in self._dillwith():
                ip,templ,power = item
                res1 = r.post('http://127.0.0.1:8086/write?db=DCM',
                              data='DCM,host=%s,temp=%s,power=%s temperature=%s,powerwaste=%s' % (ip,'temp','power',templ,power))
                # res2 = r.post('http://127.0.0.1:8086/write?db=DCM',
                #               data='DCM,host=%s,timestampe=%s,type=%s value=%s' % (ip,
                #                                                                    t,
                #                                                                    "templ",
                #                                                                    templ))
            time.sleep(60)

dcm = DCMcontroller()

if __name__ == '__main__':
    d = DataHandler(dcm=dcm)
    for i in d._dillwith():
        print(i)
