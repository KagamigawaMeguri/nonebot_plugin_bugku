from .data_source import *
from nonebot import on_command
from nonebot.adapters.cqhttp import MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from .config import *
from nonebot import require
from .cron_send import *

scheduler = require('nonebot_plugin_apscheduler').scheduler
bugku = on_command("bugku")
start = on_command("start")
init = on_command("init", priority=10)


@init.handle()
async def initialize(bot: Bot, event: Event, state: T_State):
    if not config.InitStatus:
        config.LoginStatus = False
        config.LoginCookies = await get_cookies()
        config.UserInfo = await get_userinfo()
        await init.finish("系统初始化成功，请输入/start执行下一步")
    else:
        await init.finish("系统已初始化完毕，请勿重复初始化")


@start.handle()
async def start_up(bot: Bot, event: GroupMessageEvent, state: T_State):
    user = User(str(event.group_id), 'group')
    if user not in config.UserInfo:
        config.UserInfo.append(user)
        await save_userinfo(config.UserInfo)
        await start.finish("已将本群加入通知列表，请使用/bugku命令即时检测当前房间情况")
    else:
        await start.finish("本群已加入配置，请勿重复初始化")


@start.handle()
async def start_up(bot: Bot, event: PrivateMessageEvent, state: T_State):
    user = User(str(event.user_id), 'private')
    if user not in config.UserInfo:
        config.UserInfo.append(user)
        await save_userinfo(config.UserInfo)
        await start.finish("已将你的QQ加入通知列表，请使用/bugku命令检测当前房间情况")
    else:
        await start.finish("你的QQ已加入配置，请勿重复初始化")


@bugku.args_parser
async def parse(bot: Bot, event: Event, state: T_State):
    state[state["_current_key"]] = str(event.get_message())


@bugku.handle()
async def first_receive(bot: Bot, event: Event, state: T_State):
    # 获取用户原始命令，如：/bugku
    print(state["_prefix"]["raw_command"])
    cookies = await get_cookies()
    if len(cookies) != 0:
        res = await request_detect()
        if '请登录' in res.text:
            scheduler.pause_job('detect_online', jobstore=None)
            await pre_login()
        elif res != '' and res is not None:
            # 正常登录后才能进行工作
            config.LoginStatus = True
            scheduler.resume_job('detect_online')
            await sava_cookies(res)
            await imme_detect_send(res)
    else:
        await pre_login()


@bugku.handle()
async def captcha_receive(bot: Bot, event: Event, state: T_State):
    # 登录事件
    if config.LoginStatus:  # 如果是已登录状态就跳过此handle
        await bugku.finish()
    msg = str(event.get_message()).strip()
    if check_captcha(msg):
        # 符合验证码规范，开始登录
        await login_check(msg)
    else:
        await bugku.reject("验证码格式错误，请重新输入")


async def imme_detect_send(res):
    match_list = await match_data_solve(res)
    if len(match_list) == 0:
        await bugku.finish("Master！暂未侦测到公开房间!")
    else:
        await bugku.send("Master！侦测到公开房间")
        for i in match_list:
            add_data(i)
            await bugku.send("【房间名】 {}\n【赛题】 {}\n【时间】 {}\n【名额】 {}  【入场费】 {}".format(*i))
        await bugku.finish()


@scheduler.scheduled_job('cron', minute='*/15', id='detect_online')
async def cron_detect():
    if not config.LoginStatus:
        return
    bots = nonebot.get_bots()
    for name, bot in bots.items():
        if not isinstance(bot, nonebot.adapters.cqhttp.bot.Bot):
            continue
        res = await request_detect()
        if '请登录' in res.text:
            config.LoginStatus = False
            send_msgs(bot, config.bugku_own, 'private', ["Cookies失效，请重新登录"])
            await bugku.finish()
        match_list = await match_data_solve(res)
        if len(match_list) == 0:
            await bugku.finish()
        else:
            await sava_cookies(res)
            for user in config.UserInfo:
                print("定时任务触发成功")
                tip = "Master！侦测到新的公开房间"
                msg = "【房间名】 {}\n【赛题】 {}\n【时间】 {}\n【名额】 {}  【入场费】 {}"
                msgs = [tip] + [msg.format(*i) for i in match_list]
                send_msgs(bot, user.user, user.user_type, msgs)


async def pre_login():
    await get_captcha()
    await bugku.send(('登录验证码' + MessageSegment.image(f"file:///{img_captcha}")))
    await bugku.pause("Cookie失效，请输入验证码重新登录")  # 暂停handle，准备接收验证码，然后执行下一个handle


async def login_check(captcha):
    res = await request_login(captcha)
    if '登录成功' in res.text:
        config.LoginStatus = True
        await bugku.finish("登录成功，请重新输入指令")
        await sava_cookies(res)
    elif '验证码错误' in res.text:
        await bugku.reject("验证码错误，登录失败，请重新登录")
    else:
        config.LoginStatus = False
        await bugku.finish("登录失败，请检查")


@scheduler.scheduled_job('cron', hour=6, minute=0, id='check_in')
async def cron_check_in():
    res = await check_in()
    msg = ''
    if '签到成功' in res.text:
        msg = '签到成功'
    elif '请登录' in res.text:
        msg = 'Cookies失效，签到失败'
    elif '今天您已经签到过' in res.text:
        return
    bots = nonebot.get_bots()
    for name, bot in bots.items():
        if not isinstance(bot, nonebot.adapters.cqhttp.bot.Bot):
            continue
        send_msgs(bot, config.bugku_own, 'private', [msg])


scheduler.add_job(do_send_msgs, 'interval', seconds=0.3, coalesce=True)
