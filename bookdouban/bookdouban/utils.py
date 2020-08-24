import requests
import logging
import random
import time
logger = logging.getLogger(__name__)


def get_one_proxy(api_url):
    """ 使用API接口获取一个代理IP"""
    # API接口返回的IP
    try:
        r = requests.get(api_url)
        if r.status_code != 200:
            logger.error("fail to get proxy")
            return None
        return r.text
    except ValueError:
        time.sleep(10)
        get_one_proxy(api_url)



def get_proxy(api_url):

    r = requests.get(api_url)

    return r.json().get("proxy")

def delete_proxy(proxy):
    requests.get(f'http://127.0.0.1:5010/delete/?proxy={proxy}')