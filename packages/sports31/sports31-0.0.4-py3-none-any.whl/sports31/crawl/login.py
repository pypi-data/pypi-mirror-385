import base64
from hashlib import md5
import json

import requests

from sports31.logging_config import setup_logger

logger = setup_logger(__name__)


def signPassword(pw):
    # 这个函数在实际中没有使用（coros中冗余的js代码）
    salt = "EtsPYVgTCk184RxjLveofpW0BIMNn2wr"
    return "bear-" + salt + str(base64.b64encode(pw.encode()))


def dpassword(pw):
    # coros使用md5处理了密码，没有使用salt和前缀等功能
    return md5(pw.encode()).hexdigest()


def getToken(account, password, accountType=2):
    pwd = dpassword(password)

    url = f"https://teamcnapi.coros.com/account/login"
    json_data = {"account": account, "accountType": accountType, "pwd": pwd}
    r = requests.post(url, json=json_data)
    # print(r.text)
    # print(r.json())
    # print(r.headers)
    jd = json.loads(r.text)
    try:
        return jd["data"]["accessToken"]
    except:
        logger.error(f"获取token失败, message:{jd['message']}")
        return None


if __name__ == "__main__":
    account = "account"
    pw = "password"
    print(getToken(account, pw))
