import queue

import nonebot
from nonebot import logger
import time

QUEUE = queue.Queue()
LAST_SEND_TIME = time.time()


async def do_send_msgs():
    global LAST_SEND_TIME
    if time.time() - LAST_SEND_TIME < 1.5:
        return
    if not QUEUE.empty():
        bot, user, user_type, msg, retry_time = QUEUE.get()
        try:
            if user_type == 'group':
                await bot.call_api('send_group_msg', group_id=user, message=msg)
            elif user_type == 'private':
                await bot.call_api('send_private_msg', user_id=user, message=msg)
        except:
            if retry_time > 0:
                QUEUE.put((bot, user, user_type, msg, retry_time - 1))
            else:
                logger.warning('send msg err {}'.format(msg))
        LAST_SEND_TIME = time.time()


def send_msgs(bot: nonebot.Bot, user: str, user_type: str, msgs: list):
    for msg in msgs:
        QUEUE.put((bot, user, user_type, msg, 2))
