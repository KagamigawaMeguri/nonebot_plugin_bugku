import json
import httpx
from .config import *
from bs4 import BeautifulSoup
import pickle


def check_captcha(text: str) -> bool:
    """验证码"""
    text = text.strip()
    if len(text) == 4 and text.isalnum():
        return True
    return False


def add_data(data: list):
    """将当前获取的房间数据放于库内"""
    hs = hash(str(data[0] + str(data[2])))
    config.MatchDict[hs] = data


def check_data(data: list) -> bool:
    """检测当前房间数据是否存在于库内"""
    hs = hash(str(data[0] + str(data[2])))
    if hs in config.MatchDict:
        return True
    else:
        return False


async def sava_cookies(res):
    """保存cookies"""
    dic = {}
    for key, value in res.cookies.items():
        dic[key] = value
    config.LoginCookies = dic
    with open(file_cookies, 'wb+') as f:
        pickle.dump(dic, f)


async def get_cookies() -> dict:
    """从config或本地文件中获取保存的cookies"""
    if len(config.LoginCookies) != 0:
        return config.LoginCookies
    elif file_cookies.exists():
        with open(file_cookies, 'rb') as f:
            return pickle.load(f)
    return {}


async def save_userinfo(data: list):
    """将用户数据保存在本地"""
    with open(file_userinfo, 'wb+') as f:
        pickle.dump(data, f)


async def get_userinfo() -> list:
    """从本地文件中获取备份的用户数据"""
    if file_userinfo.exists():
        with open(file_userinfo, 'rb') as f:
            return pickle.load(f)
    return []


async def request_login(captcha):
    login_cookies = await get_cookies()
    url = "https://ctf.bugku.com:443/login/check.html"
    data = {"username": config.bugku_username,
            "password": config.bugku_password, "vcode": captcha, "autologin": "1"}
    login_headers = {"Sec-Ch-Ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"",
                     "Accept": "*/*", "X-Requested-With": "XMLHttpRequest", "Sec-Ch-Ua-Mobile": "?0",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
                     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                     "Origin": "https://ctf.bugku.com", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors",
                     "Sec-Fetch-Dest": "empty", "Referer": "https://ctf.bugku.com/login",
                     "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, data=data, cookies=login_cookies, headers=login_headers)
    return res


async def request_detect():
    detect_url = "https://ctf.bugku.com:443/pvp.html"
    cookies = await get_cookies()
    headers = {"Cache-Control": "max-age=0",
               "Sec-Ch-Ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"",
               "Sec-Ch-Ua-Mobile": "?0", "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
               "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1",
               "Sec-Fetch-Dest": "document", "Referer": "https://ctf.bugku.com/pvp.html",
               "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
    async with httpx.AsyncClient() as client:
        res = await client.get(detect_url, cookies=cookies, headers=headers)
    return res


async def get_captcha():
    """请求验证码文件放入res文件夹并保存当前cookies"""
    url = "https://ctf.bugku.com/captcha.html"
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        with open(img_captcha, 'wb+') as f:
            f.write(res.content)
    await sava_cookies(res)


async def match_data_solve(res) -> list:
    """处理返回值"""
    soup = BeautifulSoup(res.text, 'lxml')
    soup_tbody = soup.find('tbody')
    match_list = []
    for i in soup_tbody.children:
        if str(i).strip() == '':
            continue
        status = i.td.span.string
        if status == '即将开始':
            per_list = []
            for j in i.children:
                s = j.string
                if s is None or s == '\n' or s == ' ':
                    continue
                per_list.append(s.strip())
            match_list.append(per_list)
        elif status == "已经结束":
            break
    return match_list


async def check_in():
    url = "https://ctf.bugku.com:443/user/checkin"
    cookies = get_cookies()
    headers = {"Sec-Ch-Ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"",
               "Accept": "*/*", "X-Csrf-Token": "0f564f2a5d35352abd95f0602dacc520", "Sec-Ch-Ua-Mobile": "?0",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
               "X-Requested-With": "XMLHttpRequest", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors",
               "Sec-Fetch-Dest": "empty", "Referer": "https://ctf.bugku.com/", "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
    async with httpx.AsyncClient() as client:
        res = await client.get(url, cookies=cookies, headers=headers)
    return res
