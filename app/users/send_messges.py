"""
FileName: utils
Date: 26 02
Author: lvah
Connect: 976131979@qq.com
Description:

"""

import json
import requests
import  string
import  random

class YunPian(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self.single_send_url = 'https://sms.yunpian.com/v2/sms/single_send.json'

    def send_sms(self, code, mobile):
        # 需要传递的参数
        parmas = {
            "apikey": self.api_key,
            "mobile": mobile,
            #此处一定要{code} 以中括号，可以将自动生成的验证码填入此处
            "text": "【刘红英test】验证码 是 {code}".format(code=code)
        }
        response = requests.post(self.single_send_url, data=parmas)
        re_dict = json.loads(response.text)
        return re_dict
    @staticmethod
    def generate_code(count=6):
        return  "".join(random.sample(string.digits, count))



if __name__ == "__main__":
    # 例如：9b11127a9701975c734b8aee81ee3526
    API_KEY = "728ae485e15be5da2391b34618de4cfa"
    yun_pian = YunPian(api_key=API_KEY)
    code = yun_pian.generate_code()
    result = yun_pian.send_sms(code, "18009211109")
    print(result)
