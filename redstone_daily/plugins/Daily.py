import time

from .Config import config
from redstone_daily.Data import Subscribers
from redstone_daily.Utils import turn_message, broadcast_message

import requests
from datetime import datetime, timedelta

from nonebot import get_bot, on_command, require
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import Event, Bot

from .utils import get_context, get_database, User, config_db, permission_required
from .utils.database import Database

require('nonebot_plugin_apscheduler')
from nonebot_plugin_apscheduler import scheduler

'''
Redstone Daily日报的获取与推送
'''

latest_matcher = on_command('latest', force_whitespace=True)
subscribe_mathcer = on_command('sub', force_whitespace=True)
unsubscribe_matcher = on_command('unsub', force_whitespace=True)
weight_map_matcher = on_command('weightmap', force_whitespace=True)

chinese_numbers = ['壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']  # 繁体中文编号


@permission_required(10)
@weight_map_matcher.handle()
async def weight_map_handler(event: Event):
    ''' 权重映射 '''
    sender, arg, group = get_context(event)

    weight_map_db = Database('redstone_daily')
    weight_map_db.set_collection('config')
    weight_map = weight_map_db.find_one({'name': 'weight_map'})

    if not arg:
        # 显示权重映射总览
        await weight_map_matcher.finish(f'---[权重映射]---\n'
                                        f'类别[terms] 含有 {len(weight_map["terms"])}项\n'
                                        f'类别[blacklist] 含有 {len(weight_map["blacklist"])}项\n'
                                        f'类别[special] 含有 {len(weight_map["special"])}项\n'
                                        f'类别[global] 含有 {len(weight_map["global"])}项\n'
                                        f'-----[完]-----')
    if len(arg) == 1:
        # 默认查看指定类别详细映射
        category = arg[0]
        if category not in weight_map:
            await weight_map_matcher.finish(f'未知的类别 {category}！')

        def generate_string():
            # 根据类别结构生成美化字符串
            if category == 'terms' or category == 'blacklist':
                for index, item in enumerate(weight_map[category]):
                    yield f' [{index}]- {item}\n'

            elif category == 'special':
                for item in weight_map[category]:
                    yield f'---{item['keyword']}---\n'
                    yield f' -在标题中权重 {item["title"][0]} 不存在 {item["title"][1]} -\n'
                    yield f' -在正文中权重 {item["description"][0]} 不存在 {item["description"][1]} -\n'
                    yield f' -在标签中权重 {item["tags"][0]} 不存在 {item["tags"][1]} -\n'

            elif category == 'global':
                yield f'  [关键词]    [权重]\n'
                for item in weight_map[category]:
                    yield f' {item["keyword"]}  {item["weight"]}\n'

        await weight_map_matcher.finish(f' -----[权重映射-{category}]-----\n'
                                        + ''.join(generate_string())
                                        + '----------[完]----------')
    elif len(arg) > 2:
        # 添加或删除权重映射
        category = arg[0]
        option = arg[1]
        name = arg[2]

        if category not in weight_map:
            await weight_map_matcher.finish(f'未知的类别 {category}！')

        if option == 'add':
            if category == 'terms' or category == 'blacklist':
                if name in weight_map[category]:
                    await weight_map_matcher.finish(f'{name} 已在 {category} 列表中！')
                weight_map[category].append(name)
                weight_map_db.update_one({'name': 'weight_map'}, {'$set': {'terms': weight_map['terms'],
                                                                           'blacklist': weight_map['blacklist']}})
                await weight_map_matcher.finish(f'{name} 已添加到 {category} 列表！')
            elif category == 'special':
                if len(arg) <= 8:
                    await weight_map_matcher.finish(f'参数不足！')
                if name in [item['keyword'] for item in weight_map[category]]:
                    await weight_map_matcher.finish(f'{name} 已在 {category} 列表中！')
                weight_map[category].append({'keyword': name, 'title': [int(arg[3]), int(arg[4])],
                                             'description': [int(arg[5]), int(arg[6])],
                                             'tags': [int(arg[7]), int(arg[8])]})
                weight_map_db.update_one({'name': 'weight_map'}, {'$set': {'special': weight_map['special']}})
                await weight_map_matcher.finish(f'{name} 已添加到 {category} 列表！')
            elif category == 'global':
                if len(arg) <= 3:
                    await weight_map_matcher.finish(f'参数不足！')
                if name in [item['keyword'] for item in weight_map[category]]:
                    await weight_map_matcher.finish(f'{name} 已在 {category} 列表中！')
                weight_map[category].append({'keyword': name, 'weight': int(arg[3])})
                weight_map_db.update_one({'name': 'weight_map'}, {'$set': {'global': weight_map['global']}})
                await weight_map_matcher.finish(f'{name} 已添加到 {category} 列表！')

        elif option == 'del':
            if category == 'terms' or category == 'blacklist':
                if name not in weight_map[category]:
                    await weight_map_matcher.finish(f'{name} 不在 {category} 列表中！')
                weight_map[category].remove(name)
                weight_map_db.update_one({'name': 'weight_map'}, {'$set': {'terms': weight_map['terms'],
                                                                           'blacklist': weight_map['blacklist']}})
                await weight_map_matcher.finish(f'{name} 已从 {category} 列表中移除！')
            elif category == 'global':
                if name not in [item['keyword'] for item in weight_map[category]]:
                    await weight_map_matcher.finish(f'{name} 不在 {category} 列表中！')
                weight_map[category] = [item for item in weight_map[category] if item['keyword']!= name]
                weight_map_db.update_one({'name': 'weight_map'}, {'$set': {'global': weight_map['global']}})
                await weight_map_matcher.finish(f'{name} 已从 {category} 列表中移除！')
            elif category =='special':
                if name not in [item['keyword'] for item in weight_map[category]]:
                    await weight_map_matcher.finish(f'{name} 不在 {category} 列表中！')
                weight_map[category] = [item for item in weight_map[category] if item['keyword']!= name]
                weight_map_db.update_one({'name': 'weight_map'}, {'$set': {'special': weight_map['special']}})
                await weight_map_matcher.finish(f'{name} 已从 {category} 列表中移除！')


@latest_matcher.handle()
async def latest_daily():
    ''' 返回最新一期的日报 '''
    try:
        await latest_matcher.send('正在获取最新一期的日报，请稍后……')
        message = turn_message(daily_handler())
        await latest_matcher.finish(message)
    except FinishedException:
        pass
    except Exception as error:
        await latest_matcher.finish(F'出错了，请稍后再试！错误信息为 {error}')


@subscribe_mathcer.handle()
async def handle_subscribe(event: Event):
    ''' 订阅日报推送 '''
    sender, arg, group = get_context(event)

    if sender.is_subscriber():
        await subscribe_mathcer.finish('你已经订阅过日报推送了！')  # 已经订阅过
    # 没有订阅过，则添加
    sender.set_subscribe(True)
    await subscribe_mathcer.finish('订阅成功，请加 Bot 好友以接收日报推送！若未添加好友，你将不会收到推送。')


@unsubscribe_matcher.handle()
async def handle_unsubscribe(event: Event):
    ''' 取消日报推送 '''
    sender, arg, group = get_context(event)
    # 确认是否订阅过
    if not sender.is_subscriber():
        await unsubscribe_matcher.finish('你还没有订阅过日报推送！')  # 未订阅过
    # 取消订阅
    sender.set_subscribe(False)
    await unsubscribe_matcher.finish('取消订阅成功！')


def get_data():
    for _ in range(5):
        response = requests.get('https://api.rsdaily.com/v2/daily')
        if response.status_code == 200:
            return response.json()


def daily_handler():
    '''
    获取最新一期的日报
    :return:
    Message: 最新一期的日报文本
    '''
    if data := get_data():
        # 解析视频
        videos: list = data
        videos.sort(key=lambda info: info['weight']
                                     + 3 * (info['data']['favorite'] / info['data']['play'])
                                     + (info['data']['like'] / info['data']['play']),
                    reverse=True)
        yield F'最新日报：{videos[0]["date"]}'  # 发送消息
        yield '今日前三甲：\n'
        for index, video in enumerate(videos[:3]):
            yield F'{chinese_numbers[index]} 《{video["title"]}》'
            yield F'{video['url']}\n'
        yield F'更多内容请访问：https://www.rsdaily.com/#/daily/{videos[0]["date"].replace("-", "/")}'
        return None
    yield '获取日报失败，请稍后再试！运维或者前端来处理一下啊喂 TAT。'


async def broadcast():
    ''' 每天定时执行一次，推送最新一期的日报 '''

    # 检查执行时间是否为设置的时间
    hour, minute = config.broadcast_time
    now = datetime.now()

    if now.hour != hour or now.minute not in [minute - 1, minute + 1]:
        return

    # 如果禁止推送，则直接返回
    if not config_db.find_one({'type': 'config'})['broadcast']:
        return

    bot: Bot = get_bot()
    message = turn_message(daily_handler())
    # 向每个推送群发送消息
    await broadcast_message(bot, message)
    # 推送订阅者
    for doc in get_database('subscribers').collection.find():

        user = User(int(doc['id']))
        if doc['sub']:
            # 发送私聊消息
            try:
                await user.send(message)
            except FinishedException:
                pass
            except Exception:
                user.set_subscribe(False)  # 移除出错的订阅者
                message = F'在尝试推送日报给用户 {user.id} 时出错，已移除此订阅者！请加好友后尝试重新订阅。'
                await broadcast_message(bot, message)
        time.sleep(1)  # 避免频繁推送


next_run_time = (datetime.now() + timedelta(minutes=1))  # 下一次运行时间
paramters = {'next_run_time': next_run_time, 'hour': '*', 'minute': '0,30'}
scheduler.add_job(broadcast, 'cron', **paramters)  # 每天在指定的qq时间运行
