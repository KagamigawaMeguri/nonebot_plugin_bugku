import os
from nonebot import get_driver
from pydantic import BaseSettings
from pathlib import Path
from dataclasses import dataclass


class Config(BaseSettings):
    InitStatus: bool = False
    LoginStatus: bool = False
    MatchDict: dict = []
    MatchList: list = []
    bugku_username: str
    bugku_password: str

    class Config:
        extra = "ignore"


@dataclass
class User:
    user: str
    user_type: str


class Lib:
    UserInfo: list = []
    LoginCookies: dict = {}
    captcha: bytes


global_config = get_driver().config
config = Config(**global_config.dict())
lib = Lib()
current_path = Path.cwd()
res_path = (current_path.parent / 'res').resolve()
img_captcha = res_path / 'captcha.png'
file_cookies = res_path / 'cookies.json'
file_userinfo = res_path / 'userinfo.json'
if not res_path.exists():
    os.mkdir(res_path)
