import time
import json, random

from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.rule import to_me
from nonebot.plugin import *
from nonebot.adapters import Message
from nonebot.params import CommandArg, Event
from nonebot import require
from scipy.stats import norm
from zhipuai import ZhipuAI

from redstone_daily.plugins.utils import get_context, User

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

"""
娱乐功能
"""

divine = on_command("luck", aliases={'运势', '人品', '今日人品', 'jrrp'})


@divine.handle()
async def handle_divine(event: Event):
    """
    今日人品
    """

    _time = time.time()  # 获取当前时间
    sender = event.user_id  # 取出发送者

    _time += 28800  # 时差8小时
    random.seed(int(sender) + int(_time - _time % 86400))  # 随机种子

    # 计算人品(运势, 财富, 事业, 健康)
    luck = random.normalvariate(0, 17)
    money = random.normalvariate(0, 17)
    career = random.normalvariate(0, 17)
    health = random.normalvariate(0, 17)

    # 计算均值
    mean = (luck + money + career + health) / 4

    def get_score(score):
        # 评价分数映射表
        mark_string = ""
        score_map = {
            -25: "衰神附体",
            -20: "倒了血霉",
            -12: "运势极差",
            -7: "运势不佳",
            -3: "运势较差",
            3: "运势一般",
            7: "运势较好",
            12: "运势优秀",
            20: "运势极佳",
            25: "祖上显灵",
            99999999: "天命之子"}

        for i in score_map:
            if score <= i:
                mark_string = score_map[i]  # 找到对应的评价
                break

        score_string = f"{round(score, 2)}%" if score < 0 else f"+{round(score, 2)}%"  # 给分数加上符号

        cdf_value = norm.cdf(score, 0, 17)  # 计算累积分布函数值
        cdf_string = f"{cdf_value:.2%}" if score < 0 else f"{(1 - cdf_value):.2%}"  # 变换累积分布函数值

        return f"{mark_string}({score_string}|{cdf_string})"

    await divine.finish(f"今日人品: \n"
                        f"-------------\n"
                        f"运势: {get_score(luck)}\n"
                        f"财富: {get_score(money)}\n"
                        f"事业: {get_score(career)}\n"
                        f"健康: {get_score(health)}\n"
                        f"-------------\n"
                        f"总评: {get_score(mean)}")


'''at_bot = on_message(rule=to_me())

@at_bot.handle()
async def at():
    """
    处理@机器人
    :return:
    """

    await at_bot.finish("喵喵喵? 喵喵喵, /rdhelp 喵喵喵喵喵!")'''

welcome = on_command("welcomenew")


@welcome.handle()
async def welcome_new():
    """
    新用户欢迎
    """
    await welcome.finish("欢迎新朋友！\n"
                         "使用 /rdhelp 获取更多信息")


dice = on_command("dice", aliases={'命运骰子', '命运色子'})


@dice.handle()
async def handle_dice(event: GroupMessageEvent):
    """
    骰子
    指定一位成员参与, 随机禁言成员或者发送者
    """
    sender, arg, group = get_context(event)

    if len(arg) > 0:  # 指定了参与者
        num = random.randint(1, 20000) / 1000
        await dice.send(f"你向{arg[0]}投出了一枚命运的骰子...")
        time.sleep(1)

        victim = User(int(arg[0]))

        if num <= 5:  # 骰子点数小于等于5, 禁言玩家
            await group.mute(victim, int(((6 - num) * 5) ** 2))
            await dice.finish(f"骰子停下了...{victim.name}被禁言了{int(((6 - num) * 5) ** 2)}秒")
        else:  # 骰子点数大于5, 禁言发送者
            await group.mute(sender, int(((num - 1) * 5) ** 2))
            await dice.finish(f"骰子停下了...玩弄命运者终将受到惩罚, 你被禁言了{int(((num - 1) * 5) ** 2)}秒")

'''fish = on_keyword({'鱼上钩啦'})

@fish.handle()
async def handle_fish(event: Event):
    sender, arg, group = get_context(event)
    if group.id != 714475609:
        return

    await fish.send('收杆')
    await fish.finish('钓鱼')'''

whatami = on_keyword({"那我是什么"})

@whatami.handle()
async def handle_whatami(event: Event):
    sender, arg, group = get_context(event)

    await whatami.send('傻逼')

    if sender.id != 3327018890:
        time.sleep(0.5)
        await whatami.finish('开玩笑的啦, 你已经很棒了, 你不需要寻求别人的认可! 价值是自己给予自己的, 超过昨天的自己就已经很棒了喵!')