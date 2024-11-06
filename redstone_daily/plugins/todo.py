from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event

from redstone_daily.plugins.utils import get_database, get_context

db = get_database('todo').get_db()
todo_config = db.find_one({'type': 'config'})

todo_matcher = on_command('todo', force_whitespace=True)


def todo_formatter(id, arg, sender, edit=False):
    """ 格式化待办 """

    title, content, ddl, req = False, False, 0, []
    user = sender.id
    doc = db.find_one({'type': 'todo', 'id': id})

    if len(arg) < 1:
        raise ValueError('请输入待办内容')

    # 提取参数
    for i in range(len(arg)):
        if arg[i].startswith('title='):
            title = arg[i][6:]
        if arg[i].startswith('content='):
            content = arg[i][8:]
        if arg[i].startswith('ddl='):
            if len(ddl) != 3 or not all(map(lambda x: x.isdigit(), ddl)):
                raise ValueError('请输入正确的截止日期')
            ddl = arg[i][4:].split('-')
        if arg[i].startswith('req='):
            req = arg[i][4:]
        if arg[i].startswith('user='):
            if len(arg[i]) > 5 and arg[i][5:].isdigit():  # 直接输入QQ号
                user = int(arg[i][5:])
            elif arg[i + 1].isdigit():  # at消息
                user = int(arg[i + 1])
            else:
                raise ValueError('请输入正确的用户QQ号或at用户')

    # 处理数据
    if not title:
        raise ValueError('请输入待办标题')
    if type(req) == str:
        req = req.split(',')
    if ddl and ddl.isdigit():
        ddl = int(ddl)
    elif ddl:
        raise ValueError('请输入正确的截止日期')

    todo_data = {}
    todo_data['type'] = 'todo'
    todo_data['id'] = id
    todo_data['title'] = title if not edit else title if title else doc['title']  # 防止在编辑时误重置字段
    todo_data['content'] = content if not edit else content if content else doc['content']
    todo_data['ddl'] = ddl if not edit else ddl if ddl else doc['ddl']
    todo_data['req'] = req if not edit else req if req else doc['req']
    todo_data['status'] = 'unfinished' if not edit else doc['status']
    todo_data['user'] = user if not edit else user if user else doc['user']

    return todo_data


@todo_matcher.handle()
async def handle_todo(event: Event):
    sender, arg, group = get_context(event)

    if not arg:  # 无参数，显示所有待办
        pass

    else:
        if arg[0] == 'create':

            """ 创建待办 """
            # 获取id
            # 查找并更新配置文档中的max_id
            config_doc = db.find_one_and_update(
                {'type': 'config'},
                {'$inc': {'max_id': 1}},
                projection={'max_id': True, '_id': False},
                upsert=True
            )
            max_id = config_doc['max_id']

            try:
                todo_data = todo_formatter(max_id, arg, sender)
                db.insert_one(todo_data)
                await todo_matcher.finish('创建待办成功')

            except ValueError as e:
                await todo_matcher.finish(str(e))

        elif arg[0] == 'edit':

            """ 编辑待办 """

            if len(arg) < 2 or not arg[1].isdigit():
                await todo_matcher.finish('不正确的待办id')

            doc = db.find_one({'type': 'todo', 'id': int(arg[1])})

            if doc['user'] != sender.id:  # 不是该用户的待办
                await todo_matcher.finish('此待办不属于你')

            try:
                todo_data = todo_formatter(int(arg[1]), arg, sender, edit=True)
                db.update_one({'type': 'todo', 'id': int(arg[1])}, {'$set': todo_data})
                await todo_matcher.finish('编辑待办成功')

            except ValueError as e:
                await todo_matcher.finish(str(e))

        elif arg[0] == 'show':

            """ 显示待办详情 """

            if len(arg) < 2 or not arg[1].isdigit():
                await todo_matcher.finish('不正确的待办id')

            doc = db.find_one({'type': 'todo', 'id': int(arg[1])})

            # 格式化待办详情
            todo_str = f'-----[id:{doc["id"]}]-----    '
            todo_str += f'\n标题: {doc["title"]}'
            todo_str += f'\n正文: {doc["content"]}' if doc['content'] else ''
            todo_str += f'\n截止日期: {doc["ddl"]}' if not doc['ddl'] == 0 else ''
            todo_str += f'\n前置的待办: {doc["req"]}' if doc['req'] else ''
            todo_str += f'\n状态: {"已完成" if doc["status"] == "finished" else "未完成"}'
            todo_str += f'\n责任人: {doc["user"]}'

            await todo_matcher.finish(todo_str)

        elif arg[0] == 'list':

            """ 显示待办列表 """

            user = sender.id

            if len(arg) > 1 and (arg[1].isdigit() or type(arg[1]) == int):  # 指定用户
                user = int(arg[1])

            # 查找待办
            todo_list = list(db.find({'type': 'todo', 'user': user, 'status': 'unfinished', 'req': []}))

            if not todo_list:
                await todo_matcher.finish('没有待办事项, 好棒!')

            # 格式化待办列表
            todo_str = ('你' if user == sender.id else f'{user}') + f'的待办事项: (共{len(todo_list)}项)'
            for i in todo_list:
                todo_str += f'\n    -----[id:{i["id"]}]-----    '
                todo_str += f'\n标题: {i["title"]}'
                todo_str += f'\n正文: {i["content"]}' if i['content'] else ''
                todo_str += f'\n截止日期: {i["ddl"]}' if not i['ddl'] == 0 else ''
                todo_str += f'\n前置的待办: {i["req"]}' if i['req'] else ''

            await todo_matcher.finish(todo_str)

        elif arg[0] == 'finished':

            """ 标记待办为已完成 """

            if len(arg) < 2 or not arg[1].isdigit():
                await todo_matcher.finish('不正确的待办id')

            doc = db.find_one({'type': 'todo', 'id': int(arg[1])})

            if doc['user'] != sender.id:  # 不是该用户的待办
                await todo_matcher.finish('此待办不属于你')

            db.update_one({'type': 'todo', 'id': int(arg[1])}, {'$set': {'status': 'finished'}})

            # 更新待办
            db.update_many({'req': {'$in': [str(doc['id'])]}}, {'$pull': {'req': str(doc['id'])}})
            await todo_matcher.finish(f'待办[{doc['title']}]已完成')
