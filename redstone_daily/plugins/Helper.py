from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event
from nonebot.params import CommandArg

from redstone_daily.plugins.utils import get_context

# 所有帮助信息都在这里 qwq

_help = on_command('help')


@_help.handle()
async def rd_help():
    '''
    显示帮助信息
    '''
    await _help.finish('RD QQ Bot帮助\n---------\n'
                       '指令大全: /commands\n'
                       '使用教程: /tutorial\n'
                       '关于rd: /about\n'
                       '---------')


commands = on_command('commands')


@commands.handle()
async def rd_commands(event: Event):
    '''
    显示指令列表
    '''

    sender, arg, group = get_context(event)

    commands_list = [
        '最新日报: latest',
        '帮助信息: rdhelp',
        '指令列表: commands',
        '使用教程: tutorial',
        '关于我们: about',
        '订阅日报推送: sub',
        '取消日报推送: unsub',
        '新用户欢迎: welcomenew',
        'OP指令: op',
        '禁言: mute',
        '修改昵称: nickname',
        '修改头衔: title',
        '踢出群聊: kick',
        '封禁: ban',
        '运势: luck',
        '命运骰子: dice',
        'TO-DO: todo',
        '推送管理: broadcast',
        '哔哩哔哩查成分: bili',
        '最新测试页面: dev',
    ]

    page = int(arg[0]) if arg else 1  # 处理页码

    start = (page - 1) * 10  # 计算开始位置
    end = page * 10  # 计算结束位置
    if end > len(commands_list):  # 处理页码超出范围
        end = len(commands_list) - 1

    commands_str = ''
    for i in range(start, end):
        commands_str += commands_list[i] + '\n'  # 构造字符串

    await commands.finish(f'RD QQ Bot指令列表 第 {page} / {int(len(commands_list) / 10) + 1} 页\n---------\n'
                          f'{commands_str}'
                          f'---------')


tutorial = on_command('tutorial')


@tutorial.handle()
async def rd_tutorial(args: Message = CommandArg()):
    '''
    显示使用教程
    '''
    command = args.extract_plain_text()  # 取出指令

    # 处理参数
    if command:
        if command == 'latest':
            await tutorial.finish('latest 显示最新一期的日报\n'
                                  '参数: 无需参数')
        elif command == 'rdhelp':
            await tutorial.finish('rdhelp 显示帮助信息\n'
                                  '参数: 无需参数')
        elif command == 'commands':
            await tutorial.finish('commands 显示指令列表\n'
                                  '参数: 无需参数')
        elif command == 'about':
            await tutorial.finish('about 关于我们的信息\n'
                                  '参数: 无需参数')
        elif command == 'tutorial':
            await tutorial.finish('tutorial 显示使用教程\n'
                                  '参数: [command] 查看此指令的详细教程')
        elif command == 'sub':
            await tutorial.finish('sub 订阅日报推送\n'
                                  '参数: 无需参数')
        elif command == 'unsub':
            await tutorial.finish('unsub 取消日报推送\n'
                                  '参数: 无需参数')
        elif command == 'welcome':
            await tutorial.finish('welcomenew 新用户欢迎\n'
                                  '参数: 无需参数')
        elif command == 'op':
            await tutorial.finish(
                'op OP指令\n'
                '参数: {command} [args]\n'
                'OP指令列表:\n'
                'op sub clear  清空订阅\n'
                'op set {qq_number} {permission}  设置权限\n'
                'op query [qq_number]  获取自己的权限\n'
                'op sub query {qq_number}  查询订阅\n'
                'op sub remove {qq_number}  删除订阅\n'
                'op sub add {qq_number}  添加订阅\n'
            )
        elif command == 'mute':
            await tutorial.finish('mute 禁言\n'
                                  '参数: {qq_number} {duration} 禁言指定用户\n'
                                  'duration用法: \n'
                                  '示例: 30s: 30秒 根据后缀字母 s.m.h.d 表示秒.分.时.天')
        elif command == 'set_nickname':
            await tutorial.finish('set_nickname 修改昵称\n'
                                  '参数: {qq_number} {new_nickname}')
        elif command == 'set_title':
            await tutorial.finish('set_title 修改头衔\n'
                                  '参数: {qq_number} {new_title}')
        elif command == 'kick':
            await tutorial.finish('kick 踢人\n'
                                  '参数: {qq_number} 踢出指定用户')
        elif command == 'ban':
            await tutorial.finish('ban 封禁\n'
                                  '参数: {qq_number}封禁指定用户')
        elif command in ['luck', '运势', '人品', '今日人品', 'jrrp']:
            await tutorial.finish('luck 今日运势 aliases=运势, 人品, 今日人品, jrrp\n'
                                  '参数: 无需参数')
        elif command == 'dice':
            await tutorial.finish('dice 命运骰子 aliases=命运骰子, 命运色子\n'
                                  '指定一位成员参与, 随机禁言成员或者发送者\n'
                                  '参数: {qq_number}参与者 []')
        elif command == 'todo':
            await tutorial.finish('todo 待办事项\n'
                                  '参数: {command} [args]\n'
                                  'todo 命令列表:\n'
                                  'todo create {todo_parts] 添加待办事项\n'
                                  '- 参数(无顺序限制, 不可包含空格):\n'
                                  '- title=<你的标题> 必填 字符串 事项标题\n'
                                  '- content=<你的正文> 选填 字符串 事项正文(补充内容)\n'
                                  '- user=<责任人> 选填 QQ号或at 责任人(不填则为自己)\n'
                                  '- ddl=<截止日期> 选填 时间戳 截止日期\n'
                                  '- req=<前置待办> 选填 列表 格式为 a,b,c,d(整数) 前置待办id 当所有前置待办完成才会显示\n'
                                  'todo edit {id} [todo_parts] 修改待办事项(注: 标题在这里不是必须的)\n'
                                  'todo show {id} 查看某项待办详情\n'
                                  'todo finished {id} 将某项标记为完成\n'
                                  'todo list [user_qid] 查询某人的待办事项(无参数则为自己)\n'
                                  'todo del {id} 删除待办事项 需要9级权限\n'
                                  'todo del_all 删除所有待办事项 需要10级权限')
        elif command == 'broadcast':
            await tutorial.finish('broadcast {stat} 推送管理\non / off 开启/关闭推送功能')
        elif command in ['bili', '查成分', '查用户']:
            await tutorial.finish('bili 哔哩哔哩用户成分查询 aliases=查成分, 查用户\n'
                                  '参数: {uid} 用户UID'
                                  '[count] 条数(默认10条)')
        elif command in ['dev', 'page']:
            await tutorial.finish('dev 测试页面操作 aliases=page\n'
                                  'dev info / dev 查询测试页面信息\n'
                                  'dev del {branch} 删除与某分支关联的测试页面\n')
        else:
            await tutorial.finish('指令不存在')
    else:
        await tutorial.finish('RD QQ Bot使用教程\n---------\n'
                              '常规指令格式: .指令 选项1 选项2\n'
                              '使用tutorial [指令名] 查看该指令的详细教程\n'
                              '选填参数[会以这种格式显示], 必填参数{会以这种格式显示}, 部分必填参数{会以这种格式显示]'
                              ', 参数中的参数<会以这种格式显示>\n'
                              '---------')


about = on_command('about')


@about.handle()
async def rd_about():
    '''
    显示关于我们信息
    '''
    await about.finish('红石日报Redstone Daily是一个开源非盈利的网站项目，收集跟进全网红石科技最新前沿进展，并以日报、周报、月报以及年报的形式发布。\n'
                       '更多信息请访问：https://redstonedaily.top/, https://redstone-daily.notion.site/Redstone-Daily-7e55265d870b424594c74acb65e3f62a\n'
                       'RD QQ Bot作者: @creepebucket(creepebucket@qq.com), @LonelySail(xiaocaicai_email@sina.com)')
