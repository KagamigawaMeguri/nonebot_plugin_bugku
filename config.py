import os
from nonebot import get_driver
from pydantic import BaseSettings
from pathlib import Path
from dataclasses import dataclass


class Config(BaseSettings):
    InitStatus: bool = False
    LoginStatus: bool = False
    LoginCookies: dict = {}
    MatchDict: dict = []
    MatchList: list = []
    UserInfo: list = []
    bugku_username: str
    bugku_password: str

    class Config:
        extra = "ignore"


@dataclass
class User:
    user: str
    user_type: str


global_config = get_driver().config
config = Config(**global_config.dict())
current_path = Path.cwd()
res_path = (current_path.parent / 'res').resolve()
img_captcha = res_path / 'captcha.png'
img_test = res_path / '1.jpg'
file_cookies = res_path / 'cookies'
file_userinfo = res_path / 'userinfo'
if not res_path.exists():
    os.mkdir(res_path)
