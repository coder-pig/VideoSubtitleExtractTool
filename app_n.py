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
import extract_subtitle
import media_utils
import os
import config_getter
import cp_utils

origin_video_dir = os.path.join(os.getcwd(), config_getter.get_config(key="origin_video_dir"))
frame_dir = os.path.join(os.getcwd(), config_getter.get_config(key="frame_dir"))
srt_save_dir = os.path.join(os.getcwd(), config_getter.get_config(key="srt_save_dir"))
audio_after_dir = os.path.join(os.getcwd(), config_getter.get_config(key="audio_after_dir"))
wav_to_mp3_dir = os.path.join(os.getcwd(), config_getter.get_config(key="wav_to_mp3_dir"))
subtitle_before_dir = os.path.join(os.getcwd(), config_getter.get_config(key="subtitle_before_dir"))
subtitle_after_dir = os.path.join(os.getcwd(), config_getter.get_config(key="subtitle_after_dir"))


if __name__ == '__main__':
    cp_utils.is_dir_existed(origin_video_dir)
    cp_utils.is_dir_existed(frame_dir)
    cp_utils.is_dir_existed(srt_save_dir)
    cp_utils.is_dir_existed(audio_after_dir)
    cp_utils.is_dir_existed(wav_to_mp3_dir)
    cp_utils.is_dir_existed(subtitle_before_dir)
    cp_utils.is_dir_existed(subtitle_after_dir)
    while True:
        choice_hint = "请输入操作序号 (输入其他退出)：\n\n{}\n{}\n{}\n{}\n".format(
            "1、字幕提取", "2、视频下载", "3、音频下载", "4、音视频处理")
        print(choice_hint)
        choice_input = input()
        if choice_input == "1":
            extract_subtitle.function()
        elif choice_input == "2":
            video_download.function()
        elif choice_input == "3":
            media_utils.video_encode("2.ts", ".mp4")
        else:
            exit(0)
