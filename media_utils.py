# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : media_utils.py
   Author   : CoderPig
   date     : 2021-09-30 10:18 
   Desc     : 音视频工具类
-------------------------------------------------
"""
import subprocess
import os
from pydub import AudioSegment
import cp_utils
import math
import time
import config_getter

audio_after_dir = os.path.join(os.getcwd(), config_getter.get_config(key="audio_after_dir"))


# 合并音视频
def merge_mp4_wav(video_path, audio_path, output_path):
    print("音视频合并中~")
    cmd = f'ffmpeg -i {video_path} -i {audio_path} -acodec copy -vcodec copy {output_path}'
    subprocess.call(cmd, shell=True)
    print("合并完毕，输出文件：", output_path)


# ffmpeg视频格式转换
def video_encode(origin_path, encode_ext):
    print("视频转换中~")
    origin_file_name = origin_path.split(".")[0]
    after_file_path = origin_file_name + encode_ext
    cmd = f'ffmpeg -i {origin_path} {origin_file_name + encode_ext}'
    print(cmd)
    subprocess.call(cmd, shell=True)
    print("合并完毕，输出文件：", after_file_path)


# 视频转换成多个wav文件
def video_to_wav(file_path, seconds):
    part_duration = seconds * 1000
    print(file_path)
    if file_path.endswith(".flv"):
        video = AudioSegment.from_flv(file_path)
    else:
        video = AudioSegment.from_file(file_path, format=file_path[-3:])
    # 获取文件名称
    src_file_name = file_path.split(os.path.sep)[-1].split('.')[0] + '_' + str(int(round(time.time() * 1000)))
    wav_save_dir = os.path.join(audio_after_dir, src_file_name)
    cp_utils.is_dir_existed(wav_save_dir)
    video_duration = int(video.duration_seconds * 1000)  # 获取视频时长
    if part_duration == 0:
        print("完整视频转换为wav文件...\n")
        wav_part = video[0: video_duration]
        wav_part.export(os.path.join(wav_save_dir, "{}.wav".format('all')), format="wav")
    else:
        part_count = math.ceil(video_duration / part_duration)  # 裁剪录音段数
        last_start = video_duration - video_duration % part_duration
        print("待处理视频时长为：{}，裁剪为：{} 段".format(video_duration, part_count))
        for part in range(0, part_count - 1):
            start = part * part_duration
            end = (part + 1) * part_duration - 1
            wav_part = video[start: end]
            print("导出时间段：{} - {}".format(start, end))
            wav_part.export(os.path.join(wav_save_dir, "{}.wav".format(part)), format="wav")
        # 剩下一段
        wav_part = video[last_start: video_duration]
        print("导出时间段：{} - {}".format(last_start, video_duration))
        wav_part.export(os.path.join(wav_save_dir, "{}.wav".format(part_count - 1)), format="wav")
    return wav_save_dir


if __name__ == '__main__':
    video_encode("test.ts", ".flv")
