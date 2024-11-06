import nonebot
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot

from redstone_daily.plugins.utils import permission_required, get_context, User

ban_matcher = on_command('ban', force_whitespace=True)
mute_matcher = on_command('mute', force_whitespace=True)
kick_matcher = on_command('kick', force_whitespace=True)
title_matcher = on_command('title', force_whitespace=True)
nickname_matcher = on_command('nickname', force_whitespace=True)
# 时间单位映射表
time_mapping = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}


@ban_matcher.handle()
@permission_required(9)
async def handle_ban(event: GroupMessageEvent):
    '''
        拉黑
        :param event: GroupMessageEvent 对象
    '''
    sender, arg, group = get_context(event)
    victim = User(int(arg[0]))

    if len(arg) != 1 or (not arg[0].isdigit()):  # 如果参数个数不为1，则提醒用户输入正确的参数
        await ban_matcher.finish('参数错误，请重新输入！')

    # 如果被拉黑的用户权限高于执行者，则拒绝执行
    if victim.get_permission(group) >= sender.get_permission(group):
        await ban_matcher.finish('你不能拉黑比自己权限高的人！')

    try:
        await group.ban(victim)
    except ActionFailed:
        await ban_matcher.finish('没有权限执行此操作！')

    await ban_matcher.finish(F'已将用户 {victim.name} 拉黑。')


@mute_matcher.handle()
@permission_required(8)
async def handle_mute(event: GroupMessageEvent):
    """
        禁言命令
        :param bot: Bot 对象
        :param event: GroupMessageEvent 对象
    """
    sender, arg, group = get_context(event)

    if len(arg) != 2:  # 如果参数个数不为2，则提醒用户输入正确的参数
        await mute_matcher.finish('参数错误，请重新输入！')

    victim_id, time = arg  # 获取禁言用户和禁言时间
    if not victim_id.isdigit():  # 如果禁言用户不是纯数字，则提醒用户输入正确的参数
        await mute_matcher.finish('第一个参数用户 QQ 号格式错误，请重新输入！')

    victim = User(int(victim_id))  # 将禁言用户转换为User对象
    if victim.get_permission(group) >= sender.get_permission(group):  # 如果被禁言的用户权限高于执行者，则拒绝执行
        await mute_matcher.finish('你不能禁言比自己权限高的人！')

    # 将禁言时间转换为秒数
    mute_time = 0
    for time in time.split('+'): mute_time += (int(time[:-1]) * time_mapping.get(time[-1].upper(), 0))  # 遍历时间单位并计算秒数
    if mute_time < 0:  # 如果禁言时间小于或等于 0，则提醒用户输入正确的参数
        await mute_matcher.finish('时间参数输入错误或者格式不正确，请重新尝试！')

    try:  # 禁言用户
        await group.mute(victim, mute_time)
    except ActionFailed:
        await mute_matcher.finish('没有权限执行此操作！')
    await mute_matcher.finish(F'已将用户 {victim.name} 禁言 {mute_time} 秒。')


@kick_matcher.handle()
@permission_required(9)
async def handle_kick(event: GroupMessageEvent):
    '''
        踢人
        :param event: GroupMessageEvent 对象
    '''
    sender, arg, group = get_context(event)
    victim = User(int(arg[0]))

    if len(arg) != 1 or (not arg[0].isdigit()):  # 如果参数个数不为1，则提醒用户输入正确的参数
        await kick_matcher.finish('参数错误，请重新输入！')

    # 如果被踢的用户权限高于执行者，则拒绝执行
    if victim.get_permission(group) >= sender.get_permission(group):
        await kick_matcher.finish('你不能踢比自己权限高的人！')

    try:
        await group.kick(victim)
    except ActionFailed:
        await kick_matcher.finish('没有权限执行此操作！')

    await kick_matcher.finish(F'已将用户 {victim.name} 踢出群组。')


"""@title_matcher.handle()
async def handle_title(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    ''' 改变群头衔 '''
    arg = get_args(args)  # 获取命令参数
    sender_permission = get_permission(event.get_user_id())  # 获取发送者权限
    if sender_permission < 8:  # 如果用户等级不足 8 级，则拒绝执行
        await title_matcher.finish(F'你需要 8 级以上权限才能执行此命令！你的权限为 {sender_permission} 级。')
    if len(arg) != 2:  # 如果参数个数不为2，则提醒用户输入正确的参数
        await title_matcher.finish('参数错误，请重新输入！')
    user, title = args
    if not user.isdigit():  # 如果 QQ 号不是纯数字，则提醒用户输入正确的参数
        await title_matcher.finish('第一个参数用户 QQ 号格式错误，请重新输入！')
    user = int(user)  # 将 QQ 号转换为数字
    # 如果被改头衔的用户权限高于执行者，则拒绝执行
    if get_permission(user) >= sender_permission:
        await title_matcher.finish('你不能更改比自己权限高的人的头衔！')
    try:
        await bot.set_group_special_title(group_id=event.group_id, user_id=user, special_title=title, duration=-1)
    except ActionFailed:
        await mute_matcher.finish('没有权限执行此操作！')
    await title_matcher.finish(F'已将用户 {user} 的头衔改为 {title}。')"""


@nickname_matcher.handle()
@permission_required(6)
async def handle_nickname(event: GroupMessageEvent):
    '''
        改变群昵称
        :param event: GroupMessageEvent 对象
    '''
    sender, arg, group = get_context(event)

    if len(arg) != 2:  # 如果参数个数不为2，则提醒用户输入正确的参数
        await nickname_matcher.finish('参数错误，请重新输入！')

    user_id, nickname = arg  # 获取 QQ 号和昵称
    if not user_id.isdigit():  # 如果 QQ 号不是纯数字，则提醒用户输入正确的参数
        await nickname_matcher.finish('第一个参数用户 QQ 号格式错误，请重新输入！')

    user = User(int(user_id))  # 将 QQ 号转换为User对象
    if user.get_permission(group) >= sender.get_permission(group):  # 如果被改名的用户权限高于执行者，则拒绝执行
        await nickname_matcher.finish('你不能改名比自己权限高的人！')

    try:
        await group.set_nickname(user, nickname)
    except ActionFailed:
        await nickname_matcher.finish('没有权限执行此操作！')
    await nickname_matcher.finish(F'已将用户 {user.name} 的群昵称改为 {nickname}。')
