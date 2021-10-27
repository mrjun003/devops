# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <spug.dev@gmail.com>
# Released under the AGPL-3.0 License.
from django.http.response import HttpResponse
from django.db.models import QuerySet
from datetime import datetime, date as datetime_date
from decimal import Decimal
import string
import random
import json
from pathlib import Path
from Crypto.Cipher import AES
import base64
from django.conf import settings
import math

#拼装dic
def toDic(nameList ,dataList):
    datas = []
    for data in dataList:
        datas.append(dict(zip(nameList, data)))
    return datas

#加密解密
class Prpcrypt(object):
    def __init__(self,key=settings.AES_KEY):
        self.key = key
        self.mode = AES.MODE_CBC

    # cryptographic functions
    def encrypt(self,text):
        cryptor = AES.new(self.key,self.mode,self.key)
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0'*add)
        self.ciphertext = cryptor.encrypt(text)
        return str(base64.b64encode(self.ciphertext),encoding="utf-8")

    def decrypt(self,text):
        text=bytes(text, encoding="utf8")
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(base64.b64decode(text))
        # print(plain_text)
        # str(plain_text, encoding="utf-8")
        # print(str(plain_text, encoding="utf-8").rstrip('\0'))
        return str(plain_text, encoding="utf-8").rstrip('\0')

#判断文件或者目录是否存在
def isExist(file_name):
    my_file = Path(file_name)
    return my_file.exists()

# 转换时间格式到字符串
def human_datetime(date=None):
    if date:
        assert isinstance(date, datetime)
    else:
        date = datetime.now()
    return date.strftime('%Y-%m-%d %H:%M:%S')

# 转换时间格式到字符串(天)
def human_date(date=None):
    if date:
        assert isinstance(date, datetime)
    else:
        date = datetime.now()
    return date.strftime('%Y-%m-%d')

def human_time(date=None):
    if date:
        assert isinstance(date, datetime)
    else:
        date = datetime.now()
    return date.strftime('%H:%M:%S')

# 解析时间类型的数据
def parse_time(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        if len(value) == 10:
            return datetime.strptime(value, '%Y-%m-%d')
        elif len(value) == 19:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    raise TypeError('Expect a datetime.datetime value')

# 传两个时间得到一个时间差
def human_diff_time(time1, time2):
    time1 = parse_time(time1)
    time2 = parse_time(time2)
    delta = time1 - time2 if time1 > time2 else time2 - time1
    if delta.seconds < 60:
        text = '%d秒' % delta.seconds
    elif delta.seconds < 3600:
        text = '%d分' % (delta.seconds / 60)
    else:
        text = '%d小时' % (delta.seconds / 3600)
    return '%d天%s' % (delta.days, text) if delta.days else text

def json_response(data='', message=''):
    content = AttrDict(data=data, message=message)
    if message:
        content.data = ''
    elif hasattr(data, 'to_dict'):
        content.data = data.to_dict()
    elif isinstance(data, (list, QuerySet)) and all([hasattr(item, 'to_dict') for item in data]):
        content.data = [item.to_dict() for item in data]
    return HttpResponse(json.dumps(content, cls=DateTimeEncoder), content_type='application/json')

# 继承自dict，实现可以通过.来操作元素
class AttrDict(dict):
    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __delattr__(self, item):
        self.__delitem__(item)

# 日期json序列化
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime_date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, Decimal):
            return float(o)

        return json.JSONEncoder.default(self, o)

# 生成指定长度的随机数
def generate_random_str(length: int = 4, is_digits: bool = True) -> str:
    words = string.digits if is_digits else string.ascii_letters + string.digits
    return ''.join(random.sample(words, length))

def get_request_real_ip(headers: dict):
    x_real_ip = headers.get('x-forwarded-for')
    if not x_real_ip:
        x_real_ip = headers.get('x-real-ip', '')
    return x_real_ip.split(',')[0]

#将一个list平均分成n份,最后一份可能不足平均数
def cutList(orgList,n):
    if n>0:
        l = len(orgList)
        cnt = math.floor(l/n)
        i = 0
        rList = []
        while i*cnt<l:
            rList.append(orgList[i*cnt:(i+1)*cnt])
            i = i + 1
        return rList
    else:
        return orgList
