# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : extract_subtitle.py
   Author   : CoderPig
   date     : 2021-10-13 10:27 
   Desc     : 提取字幕
-------------------------------------------------
"""
import cp_utils
import os
import config_getter
import ffmpeg
import json
import time
import extract_text_by_api

origin_video_dir = os.path.join(os.getcwd(), config_getter.get_config(key="origin_video_dir"))
frame_dir = os.path.join(os.getcwd(), config_getter.get_config(key="frame_dir"))


def function():
    while True:
        video = choose_video()
        if video is not None:
            choose_process_method(video)
        else:
            print("当前目录下暂无视频")
            return


# 选择视频
def choose_video():
    video_list = cp_utils.filter_file_by_types(origin_video_dir, ".mp4", ".flv", ".avi", ".ts", ".wmv", ".mkv", ".mpeg")
    if len(video_list) == 0:
        print("待处理视频为空")
        return None
    print("请输入要提取字幕的视频序号：\n{}".format('=' * 64))
    for pos, video_path in enumerate(video_list):
        print("{} → {}".format(pos, video_path))
    print("=" * 64)
    video_choose_index = int(input())
    return video_list[video_choose_index]


# 选择提取方式
def choose_process_method(video_path):
    print(
        "{}\n当前选中视频：{}\n请输入提取方式序号：\n{}\n{}\n{}\n{}\n{}\n{}".format("=" * 64, video_path, '=' * 64,
                                                                   "1 → ffmpeg提取字幕流",
                                                                   "2 → 区域裁剪+OCR文字识别提取",
                                                                   "3 → 音频转文字API提取",
                                                                   "4 → 取消选中",
                                                                   "=" * 64))
    input_pos = int(input())
    if input_pos == 1:
        extract_by_ffmpeg(video_path)
    elif input_pos == 2:
        extract_by_ocr(video_path)
    elif input_pos == 3:
        extract_text_by_api.function(video_path)
    elif input_pos == 4:
        return


# ffmpeg提取字幕流文件
def extract_by_ffmpeg(video_path):
    print("=" * 64)
    probe = ffmpeg.probe(video_path)
    if probe['streams'] is not None:
        print("解析流：")
        has_subtitle = False
        for stream in probe['streams']:
            print(stream)
            if stream['codec_name'] == 'subtitle':
                has_subtitle = True
                ffmpeg.input(video_path).output("-map 0:s:0", str(time.time()) + ".srt", "").run()
        if not has_subtitle:
            print("未检测到字幕流，请使用其他方式进行字幕提取...")
            choose_process_method(video_path)
        else:
            print("字幕流提取完毕...")


# ocr文字识别字幕
def extract_by_ocr(video_path):
    ffmpeg.input(video_path).output('{}%d.jpg'.format(frame_dir + os.path.sep)).run()


if __name__ == '__main__':
    cp_utils.is_dir_existed(frame_dir)
    function()
