# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : app.py
   Author   : CoderPig
   date     : 2021-01-11 18:15 
   Desc     : 程序运行类
-------------------------------------------------
"""
import math
import os
import re
import time

import speech_recognition as sr
from pydub import AudioSegment as pydub_as
from you_get import common as you_get

import config_getter
import cp_utils

url_match_pattern = re.compile(r'((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?',
                               re.S)

video_before_dir = os.path.join(os.getcwd(), config_getter.get_config(key="video_before_dir"))
audio_before_dir = os.path.join(os.getcwd(), config_getter.get_config(key="audio_before_dir"))
audio_after_dir = os.path.join(os.getcwd(), config_getter.get_config(key="audio_after_dir"))
subtitle_before_dir = os.path.join(os.getcwd(), config_getter.get_config(key="subtitle_before_dir"))
subtitle_after_dir = os.path.join(os.getcwd(), config_getter.get_config(key="subtitle_after_dir"))
cookies_dir = os.path.join(os.getcwd(), config_getter.get_config(key="cookies_dir"))
os.environ['path'] = os.environ.get('path')


# 下载B站视频
def download_bilibli_video(url):
    # 遍历文件夹判断cookies文件是否存在
    path_list = cp_utils.filter_file_by_string(cookies_dir, "bilibili.txt")
    if len(path_list) == 0:
        print("Cookies文件不存在，使用默认下载，速度可能较慢")
        you_get.any_download_playlist(url=url, info_only=False, output_dir=video_before_dir)
    else:
        you_get.any_download_playlist(url=url, info_only=False, output_dir=video_before_dir, merge=True,
                                      cookies_dir=path_list[0])


# 将flv文件转换为wav音频文件
def flv_to_wav(file_path):
    flv = pydub_as.from_flv(file_path)
    wav_save_dir = os.path.join(audio_after_dir, str(int(round(time.time() * 1000))))
    cp_utils.is_dir_existed(wav_save_dir)
    flv_duration = int(flv.duration_seconds * 60000)  # 获得视频时长
    part_count = math.ceil(flv_duration / 60000)  # 录音段数 5s为1段
    last_start = flv_duration - flv_duration % 60000
    print("待处理视频时长为：{}，裁剪为：{} 段".format(flv_duration, part_count))
    for part in range(0, part_count - 1):
        start = part * 60000
        end = (part + 1) * 60000 - 1
        wav_part = flv[start: end]
        print("导出时间段：{} - {}".format(start, end))
        wav_part.export(os.path.join(wav_save_dir, "{}.wav".format(part)), format="wav")
    # 剩下一段
    wav_part = flv[last_start: flv_duration]
    print("导出时间段：{} - {}".format(last_start, flv_duration))
    wav_part.export(os.path.join(wav_save_dir, "{}.wav".format(part_count)), format="wav")
    return wav_save_dir


# 提取wav文本
def extract_text(file_path):
    pass


if __name__ == '__main__':
    # 相关文件夹初始化
    cp_utils.is_dir_existed(video_before_dir)
    cp_utils.is_dir_existed(audio_before_dir)
    cp_utils.is_dir_existed(audio_after_dir)
    cp_utils.is_dir_existed(subtitle_before_dir)
    cp_utils.is_dir_existed(subtitle_after_dir)
    cp_utils.is_dir_existed(cookies_dir)
    choose_hint = "请输入您要进行的操作序号：\n\n{}\n{}\n{}\n{}\n{}\n{}\n".format(
        "1、视频下载一条龙", "2、本地视频一条龙", "3、视频转音频",
        "4、音频分割", "5、字幕提取", "6、字幕拼接")
    print(choose_hint)
    choose_input = input()
    if choose_input == "1":
        print("请输入要下载的地址")
        while True:
            download_url = input()
            result = url_match_pattern.match(download_url)
            if result is not None:
                if download_url.find("bilibili") != -1:
                    download_bilibli_video(download_url)
                    break
                else:
                    you_get.any_download(url=download_url, info_only=False, output_dir=video_before_dir)
                    break
            else:
                print("URL格式错误，请输入正确的URL")
        # 扫描flv文件
        flv_list = cp_utils.filter_file_type(video_before_dir, ".flv")
        print(flv_list)
    elif choose_input == "2":
        flv_list = cp_utils.filter_file_type(video_before_dir, ".flv")
        if len(flv_list) == 0:
            print("本地视频为空，请检查后重试：")
        else:
            print("请选择处理视频的序号：\n{}\n".format("=" * 64))
            for index, value in enumerate(flv_list):
                print("{}.{}".format(index, value))
            file_choose = input("\n{}\n请输入序号：\n".format("=" * 64))
            file_choose_int = int(file_choose)
            if 0 <= file_choose_int < len(flv_list):
                wav_path = flv_to_wav(flv_list[file_choose_int])
                print("flv转wav完成，输出文件：", wav_path)
            else:
                print("序号选择错误")
    elif choose_input == "5":
        # mp3_path = os.path.join(audio_after_dir, "1610545418381/0.mp3")
        wav_path = os.path.join(audio_after_dir, "1610607876412/12.wav")
        # mp3_file = AudioSegment.from_mp3(mp3_path)
        # mp3_file.export(wav_path, format="wav")
        # file = SPHFile(wav_path)
        # file.write_wav(filename=wav_path)
        print(wav_path)
        r = sr.Recognizer()
        test = sr.AudioFile(wav_path)
        with test as source:
            audio = r.record(source)
        text = r.recognize_sphinx(audio, language='zh-CN')
        print(text)
