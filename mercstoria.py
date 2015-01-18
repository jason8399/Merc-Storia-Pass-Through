from cryptmanager import CryptManager
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
import requests
import time
import base64
import sys


class INFO:

    def __init__(self, uuid="", iid="-", device_token=""):
        self.__UUID = uuid
        self.__IID = iid
        self.__DEVICE_TOKEN = device_token
        self.__ENCRYPT_UUID = "" if len(self.__UUID) is 0 \
            else CryptManager.des_encrypt(CryptManager.DES_KEY, self.__UUID)
        self.__REQUEST_IV = "" if len(self.__ENCRYPT_UUID) is 0 \
            else CryptManager.MD5(self.__ENCRYPT_UUID)
        self.__REQUEST_HASH = CryptManager.MD5("ILovePerl")

        pass

    def read_xml(self, filename="jp.co.happyelements.tototw.xml"):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            self.__UUID = root.findall(".//string/.[@name='UUID']")[0].text
            self.__DEVICE_TOKEN = root.findall(".//string/.[@name='DeviceToken']")[0].text
            self.__IID = root.findall(".//string/.[@name='IID']")[0].text
        except ET.ParseError:
            return False
        return True

    def set_user(self, uuid="", iid="", device_token=""):
        if len(uuid) is 0 or len(iid) is 0 or len(device_token) is 0:
            raise Exception
        self.__UUID = uuid
        self.__IID = iid
        self.__DEVICE_TOKEN = device_token

    def get_uuid(self):
        return self.__UUID

    def get_iid(self):
        return self.__IID

    def get_device_token(self):
        return self.__DEVICE_TOKEN

    def get_encrypt_uuid(self):
        if len(self.__ENCRYPT_UUID) is 0:
            self.__ENCRYPT_UUID = CryptManager.des_encrypt(CryptManager.DES_KEY, self.__UUID)
        return self.__ENCRYPT_UUID

    def get_request_hash(self):
        return self.__REQUEST_HASH

    def get_request_iv(self):
        if len(self.__REQUEST_IV) is 0:
            self.__REQUEST_IV = CryptManager.MD5(self.get_encrypt_uuid())
        return self.__REQUEST_IV


class HEADER:

    def __init__(self, info):
        if type(info) is not INFO:
            raise Exception
        self.__INFO = info
        self.__RANDOM_HASH = "TYhGo022TyofIxfs2gRVoUuyWwv0iR2G0FgAC9ml"
        self.__APP_VERSION = 32
        self.__APPT_SALT = "merctotostoria"
        self.__HEADER = {
            "APP_ID_1": info.get_encrypt_uuid(),
            "APP_ID_2": CryptManager.SHA1(self.__RANDOM_HASH + info.get_uuid()),
            "APP_ID_3": CryptManager.des_encrypt(CryptManager.DEVICE_TOKEN_DES_KEY, info.get_device_token()),
            "DEVICE_INFO": "unknown:::Android OS 4.4.3 / API-19 (KTU84L/366813.5)",
            "AppVersion": self.__APP_VERSION,
            "PID": "-",
            "VID": "-",
            "IID": info.get_iid(),
            "Accept": "application/json",
            "Device": "android",
            "Encrypted": True,
            "User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.4.3; unknown Build/KTU84L)",
            "Host": "toto-taiwan.hekk.org",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Unity-Version": "4.5.4p3",
            "Accept-Encoding": "gzip",
            "Connection": "close",
            "APP_T": base64.b64encode(CryptManager.aes_encrypt(aes_key=info.get_request_hash(),
                                                               aes_iv=info.get_request_iv(),
                                                               scr=str(int(time.time())) + self.__APPT_SALT))
        }

    def get_header(self):
        return self.__HEADER

    def update_header(self, attr="APP_T", value=""):
        self.__HEADER.update({attr: value})

    def update_header_appt(self):
        self.update_header(base64.b64encode(CryptManager.aes_encrypt(aes_key=self.__INFO.get_request_hash(),
                                                                     aes_iv=self.__INFO.get_request_iv(),
                                                                     scr=str(int(time.time())) + self.__APPT_SALT)))


class Game:

    def __init__(self, header):
        self.__URL = "http://toto-taiwan.hekk.org/"
        self.__EXECUTE = "execute/"
        self.__QUEST = "quests/"
        self.__RESULT = "result"
        self.__AP_USE = "ap_use"
        self.__BATTLES = "battles/"
        # 關卡編號
        self.__EQ_NUM = "1"
        # 難度等級
        self.__DIFFICULTY = ["normal", "hard", "very_hard", "impossible"]
        self.__DIFFICULTY_ID = 0
        self.__MODE = ["quest", "battle"]
        self.__MODE_NUM = 0
        self.__E = ""
        self.__E_FIN = ""
        self.__header = {} if type(header) is not HEADER else header
        self.__response = None
        self.__json = None

    def get_e(self):
        # E裡面的文字(未加密)
        self.__E = "name=Quest&base=Quest/Quest&mode=" + self.__MODE[self.__MODE_NUM] + "&tipsLoading=true&id=" \
                   + str(self.__EQ_NUM) + "&difficulty_id=" + self.__DIFFICULTY[self.__DIFFICULTY_ID]\
                   + "&party_id=002&unit_ids=1"
        self.__E_FIN = self.__E + "&page_message=" + quote_plus(self.__E).replace("D", "d").replace("C", "c")\
            .replace("F", "f")
        return self.__E_FIN

    def set_mode_num(self, num=0):
        self.__MODE_NUM = int(num)

    def set_eq_num(self, num="1"):
        self.__EQ_NUM = num

    def set_difficulty_id(self, num="1"):
        self.__DIFFICULTY_ID = int(num) - 1

    def time_counter():
        for i in range(101):
            time.sleep(0.25)
            sys.stdout.write("\r[%-20s] %d%%" % ('=' * int(i * 0.2), i))
            sys.stdout.flush()
        print("")

    time_counter = staticmethod(time_counter)

    def login(self):
        self.__response = requests.post(self.__URL + "users/check_new_user.json",
                                        data="_method=GET",
                                        headers=self.__header.get_header())
        self.__json = self.__response.json()

    def select_mode(self):
        # 工會模式尚未完成
        num = int(input("選擇模式[1]關卡模式[2]工會模式(未完成)"))
        self.set_mode_num(num=1 - 1)

    def interface(self):
        # flag = True
        print("現在AP: " + str(self.__json["data"]["user"]["ap"]))
        print("現在BP: " + str(self.__json["data"]["user"]["bp"]))
        # while flag:
            # if self.__MODE_NUM is 0:
            #     if self.__json["data"]["user"]["ap"] is 0:
            #         print("沒有AP了～～～等等再玩吧")
            #         if input("是否結束遊戲?[y/n]").lower() is "y":
            #             exit(0)
            #         if input("是否切換成公會戰模式[y/n]").lower() is "y":
            #             self.set_mode_num(num=1)
            #     else:
            #         flag = False
            # if self.__MODE_NUM is 1:
            #     if self.__json["data"]["user"]["bp"] is 0:
            #         print("沒有BP了～～～快去打關卡回復AP")
            #         if input("是否結束遊戲?[y/n]").lower() is "y":
            #             exit(0)
            #         if input("是否切換成關卡模式[y/n]").lower() is "y":
            #             self.set_mode_num()
            #     else:
            #         flag = False
        self.set_eq_num(input("輸入關卡: "))
        self.set_difficulty_id(input("輸入難度: "))

    def play_game(self):

        data_encrypt = CryptManager.aes_encrypt(aes_key=userInfo.get_request_hash(),
                                                aes_iv=userInfo.get_request_iv(),
                                                scr="_method=GET")
        data = ''.join(chr(e) for e in data_encrypt)
        e = ''.join(
            chr(a) for a in base64.b64encode(CryptManager.aes_encrypt(aes_key=userInfo.get_request_hash(),
                                                                      aes_iv=userInfo.get_request_iv(),
                                                                      scr=self.get_e())))
        self.__response = requests.post(self.__URL + self.__QUEST + self.__EXECUTE + self.__EQ_NUM + ".json?e=" + e,
                                        data=data,
                                        headers=self.__header.get_header())
        if self.__response.status_code is 200:
            self.__json = self.__response.json()
        else:
            return False

        #AP USE
        ap_use_url = self.__json["ap_use_url"]
        ap_params = ''.join(chr(a) for a in base64.b64encode(
            CryptManager.aes_encrypt(aes_key=userInfo.get_request_hash(),
                                     aes_iv=userInfo.get_request_iv(),
                                     scr=ap_use_url.split("?")[1])))
        self.__header.update_header_appt()
        self.__response = requests.post(self.__URL + self.__QUEST + self.__AP_USE + "?e=" + ap_params,
                                        data=data,
                                        headers=self.__header.get_header())
        if self.__response.status_code is not 200:
            return False
        #RESULT
        ##WAIT
        self.time_counter()
        result_url = self.__json["result_url"].split("?")[1] + "&time=20.00000"
        result_params = ''.join(chr(a) for a in base64.b64encode(
            CryptManager.aes_encrypt(aes_key=userInfo.get_request_hash(),
                                     aes_iv=userInfo.get_request_iv(),
                                     scr=result_url)))
        self.__header.update_header_appt()
        self.__response = requests.post(self.__URL + self.__QUEST + self.__RESULT + "?e=" + result_params,
                                        data=data,
                                        headers=self.__header.get_header())
        if self.__response.status_code is 200:
            self.__json = self.__response.json()
        else:
            return False
        return True

if __name__ == '__main__':
    userInfo = INFO()
    userInfo.read_xml()
    header = HEADER(userInfo)
    game = Game(header)
    game.login()
    game.select_mode()
    while True:
        game.interface()
        if not game.play_game():
            input("Something Wrong <Enter to Continue>\n\n\n")





















