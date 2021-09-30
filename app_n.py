# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : app_n.py
   Author   : CoderPig
   date     : 2021-09-30 9:46 
   Desc     : 程序入口类
-------------------------------------------------
"""
import video_download

if __name__ == '__main__':
    while True:
        choice_hint = "请输入您要进行的操作序号 (输入其他字符退出)：\n\n{}\n{}\n{}\n".format(
            "1、视频下载", "2、视频处理", "3、字幕提取")
        print(choice_hint)
        choice_input = input()
        if choice_input == "1":
            video_download.function()
        elif choice_input == "2":
            pass
        elif choice_input == "3":
            pass
        else:
            exit(0)
