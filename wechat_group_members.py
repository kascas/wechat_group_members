from pywinauto.application import Application
import pywinauto
import time
import psutil
import pandas as pd
import numpy as np


def get_wechat_pid():
    pids = psutil.pids()
    for pid in pids:
        p = psutil.Process(pid)
        if p.name() == 'WeChat.exe':
            return pid
    return None


def get_name_list(pid):
    print('>>> 请打开【微信=>目标群聊=>聊天成员=>查看更多】，尤其是【查看更多】，否则查找不全！')
    for i in range(10):
        print('\r({} 秒)'.format(10 - i), end='')
        time.sleep(1)
    print('\r>>> WeChat.exe pid: {}'.format(pid))
    app = Application(backend='uia').connect(process=pid)
    win_main_Dialog = app.window(class_name='WeChatMainWndForPC')
    chat_list = win_main_Dialog.child_window(control_type='List', title='聊天成员')
    name_list = []
    all_members = []
    for i in chat_list.items():
        p = i.descendants()
        if p and len(p) > 5:
            if p[5].texts() and p[5].texts()[0].strip() != '' and (p[5].texts()[0].strip() != '添加' and p[5].texts()[0].strip() != '移出'):
                name_list.append(p[5].texts()[0].strip())
                all_members.append([p[5].texts()[0].strip(), p[3].texts()[0].strip()])
    pd.DataFrame(np.array(all_members)).to_csv('all_members.csv', header=['群昵称', '微信昵称'])
    print('>>> 群成员共 {} 人，结果已保存至all_members.csv'.format(len(name_list)))
    return name_list


def match():
    pid = get_wechat_pid()
    if pid == None:
        print('>>> 找不到WeChat.exe，请先打开WeChat.exe再运行此脚本！')
        return
    try:
        name_list = get_name_list(pid)
    except pywinauto.findwindows.ElementNotFoundError as e:
        print('>>> 未找到【聊天成员】窗口，程序终止！')
        print('>>> 若已开启【聊天成员】窗口但仍报错，请重启微信（原因：可能存在多个WeChat进程）')
        return
    mode = ''
    while True:
        mode = input('>>> 是否需要根据name_list.txt进行匹配？ [y/n] ')
        if mode != 'y' and mode != 'n':
            print('>>> 请输入 y 或 n选择模式 [y/n] ')
        else:
            if mode == 'n':
                return
            else:
                break
    not_found = []
    with open('./name_list.txt', 'r', encoding='utf-8')as fp:
        for i in fp.readlines():
            i, result = i.strip(), False
            if i == '':
                continue
            for j in name_list:
                if i in j:
                    result = True
                    name_list.remove(j)
            if not result:
                not_found.append(i)
    print('>>> 匹配失败列表：\n------------------------------')
    print('\n'.join(not_found))
    print('------------------------------')


if __name__ == '__main__':
    match()
