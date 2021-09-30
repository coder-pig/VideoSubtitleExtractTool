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
import extract_text_by_api
import media_utils

if __name__ == '__main__':
    while True:
        choice_hint = "请输入您要进行的操作序号 (输入其他字符退出)：\n\n{}\n{}\n{}\n".format(
            "1、视频下载", "2、字幕提取", "3、视频处理")
        print(choice_hint)
        choice_input = input()
        if choice_input == "1":
            video_download.function()
        elif choice_input == "2":
            extract_text_by_api.function()
        elif choice_input == "3":
            media_utils.video_encode("2.ts", ".mp4")
        else:
            exit(0)
