from redstone_daily.plugins.Config import config
from redstone_daily.Data import Subscribers

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Event

from redstone_daily.plugins.utils import permission_required, get_context, User, get_database, config_db

op_sub_add_matcher = on_command(
    'op sub add', force_whitespace=True, priority=10, block=True)
op_sub_list_matcher = on_command(
    'op sub list', force_whitespace=True, priority=10, block=True)
op_sub_remove_matcher = on_command(
    'op sub remove', force_whitespace=True, priority=10, block=True)
op_sub_clear_matcher = on_command(
    'op sub clear', force_whitespace=True, priority=10, block=True)


@op_sub_add_matcher.handle()
@permission_required(5)
async def perm_sub_add(event: Event):
    sender, arg, group = get_context(event)

    for user_id in arg[2:]:
        if not user_id.isdigit():  # 输入的 QQ 号格式不正确
            await op_sub_add_matcher.send('输入的 QQ 号格式不正确，请重新输入后尝试！')

        user = User(int(user_id))
        if user.is_subscriber():  # 输入的 QQ 号已经订阅过了
            await op_sub_add_matcher.send('该用户已经订阅过了，无法重复设置。')

        user.set_subscribe(True)
        await op_sub_add_matcher.send(F'设置用户 {user.id} 订阅成功！')


@op_sub_list_matcher.handle()
@permission_required(5)
async def perm_sub_list(event: Event):
    sender, arg, group = get_context(event)
    subscribers = get_database('subscribers').collection

    message = ''
    for i in subscribers.find():  # 遍历数据库中的所有订阅用户
        message += F'{i["id"]}, ' if i['sub'] else ''

    if message:
        await op_sub_list_matcher.finish('当前订阅用户：\n' + message)  # 输出当前订阅用户
    await op_sub_list_matcher.finish('当前没有任何订阅用户！')


@op_sub_remove_matcher.handle()
@permission_required(5)
async def perm_sub_remove(event: Event):
    sender, arg, group = get_context(event)

    for user_id in arg[2:]:
        if not user_id.isdigit():  # 输入的 QQ 号格式不正确
            await op_sub_add_matcher.send('输入的 QQ 号格式不正确，请重新输入后尝试！')

        user = User(int(user_id))
        if not user.is_subscriber():  # 输入的 QQ 号没有订阅过
            await op_sub_remove_matcher.finish('该用户没有订阅过，无法取消订阅。')

        user.set_subscribe(False)
        await op_sub_remove_matcher.finish(F'取消用户 {user.id} 订阅成功！')


@op_sub_clear_matcher.handle()
@permission_required(10)
async def perm_sub_clear(event: Event):
    sender, arg, group = get_context(event)

    if len(arg) == 3 and arg[2] == 'confirm':  # 确认清空所有订阅用户
        get_database('subscribers').clear()
        await op_sub_clear_matcher.finish('已清空所有订阅用户！')

    await op_sub_clear_matcher.finish('确认清空所有订阅用户？请输入 "op sub clear confirm" 进行确认。')


broadcast_matcher = on_command('broadcast', force_whitespace=True, priority=10, block=True)


@broadcast_matcher.handle()
@permission_required(10)
async def broadcast(event: Event):
    sender, arg, group = get_context(event)

    if not arg:  # 没有参数
        await broadcast_matcher.finish('参数错误: 不能为空！')

    if arg[0] == 'on':
        config_db.find_one_and_update({'type': 'config'}, {'$set': {'broadcast': True}})
        await broadcast_matcher.finish('推送已开启！')
    elif arg[0] == 'off':
        config_db.find_one_and_update({'type': 'config'}, {'$set': {'broadcast': False}})
        await broadcast_matcher.finish('推送已关闭！')
    else:
        await broadcast_matcher.finish('参数错误: 请输入 "on" 或 "off"！')
