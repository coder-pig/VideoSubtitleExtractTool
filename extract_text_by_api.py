# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : extract_text_by_api.py
   Author   : CoderPig
   date     : 2021-01-28 15:42 
   Desc     : 利用APP的API生成字幕
-------------------------------------------------
"""
import hashlib
import math
import os
import time
import config_getter
import requests as r
from pydub import AudioSegment

import cp_utils

host = 'app.xunjiepdf.com'
# 用户信息
device_id = config_getter.get_user(key='device_id')
account = config_getter.get_user(key='account')
user_token = config_getter.get_user(key='user_token')
machine_id = config_getter.get_user(key='machine_id')
# 相关目录
origin_video_dir = os.path.join(os.getcwd(), config_getter.get_config(key="origin_video_dir"))
srt_save_dir = os.path.join(os.getcwd(), config_getter.get_config(key="srt_save_dir"))
audio_after_dir = os.path.join(os.getcwd(), config_getter.get_config(key="audio_after_dir"))
wav_to_mp3_dir = os.path.join(os.getcwd(), config_getter.get_config(key="wav_to_mp3_dir"))
subtitle_before_dir = os.path.join(os.getcwd(), config_getter.get_config(key="subtitle_before_dir"))
subtitle_after_dir = os.path.join(os.getcwd(), config_getter.get_config(key="subtitle_after_dir"))
# API接口
base_url = 'https://{}/api/v4/'.format(host)
member_profile_url = base_url + "memprofile"
upload_par_url = base_url + "uploadpar"
upload_file_url = base_url + "uploadfile"
task_state_url = base_url + "taskstate"
task_down_url = base_url + "taskdown"
# 常量字段
product_info = 'F5030BB972D508DCC0CA18BDF7AE48E26717591F38906C09587358DAAC0092F0'
software_name = '录音转文字助手'

# 普通请求头
okhttp_headers = {
    'Host': host,
    'User-Agent': 'okhttp/3.10.0'
}

# 上传文件请求头
upload_headers = {
    'Host': host,
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 8; Mi 20 Build/QQ3A.200805.001)',
    'Content-Type': 'application/octet-stream'
}


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


# 获取用户信息
def member_profile():
    data = {
        "deviceid": device_id,
        "timestamp": int(time.time()),
        "productinfo": product_info,
        "account": account,
        "usertoken": user_token
    }
    data_sign = md5(dict_to_str(data))
    data['datasign'] = data_sign
    resp = r.post(url=member_profile_url, headers=okhttp_headers, data=data)
    print(resp.json())


# 文件上传校验
def upload_par(file_path):
    file_name = file_path.split(os.path.sep)[-1]
    data = {
        "outputfileextension": "srt",
        "tasktype": "voice2text",
        "productid": "34",
        "isshare": 0,
        "softname": software_name,
        "usertoken": user_token,
        "filecount": 1,
        "filename": file_name,
        "machineid": machine_id,
        "fileversion": "defaultengine",
        "softversion": "4.3.2",
        "fanyi_from": "zh",
        "limitsize": "204800",
        "account": account,
        "timestamp": int(time.time())
    }
    data_sign = md5(dict_to_str(data))
    data['datasign'] = data_sign
    resp = r.post(url=upload_par_url, headers=okhttp_headers, data=data)
    print("请求：", resp.url)
    if resp is not None:
        resp_json = resp.json()
        print(resp_json)
        if resp_json['code'] == 10000:
            return TaskInfo(resp_json['tasktag'], resp_json['tasktoken'], resp_json['timestamp'])
        else:
            return resp_json


# 文件分块上传
def upload_file(upload_task, file_path):
    # 获得文件字节数
    file_size = os.path.getsize(file_path)
    # 计算文件块数
    chunks_count = math.ceil(file_size / 1048576)
    upload_params = {
        'tasktag': upload_task.task_tag,
        'timestamp': upload_task.timestamp,
        'tasktoken': upload_task.task_token,
        'fileindex': 0,
        'chunks': chunks_count,
    }
    # 分段请求
    for count in range(chunks_count):
        upload_params['chunk'] = count
        start_index = count * 1048576
        with open(file_path, 'rb') as f:
            f.seek(start_index)
            content = f.read(1048576)
            resp = r.post(url=upload_file_url, headers=upload_headers, params=upload_params, data=content)
            print("请求：", resp.url)
            if resp is not None:
                print(resp.json())
            count += 1


# 查询翻译状态
def task_state(upload_task):
    data = {
        "ifshowtxt": "1",
        "productid": "34",
        "deviceos": "android10",
        "softversion": "4.3.2",
        "tasktag": upload_task.task_tag,
        "softname": software_name,
        "usertoken": user_token,
        "deviceid": device_id,
        "devicetype": "android",
        "account": account,
        "timestamp": int(time.time())
    }
    data_sign = md5(dict_to_str(data))
    data['datasign'] = data_sign
    while True:
        resp = r.post(url=task_state_url, headers=okhttp_headers, data=data)
        print("请求：", resp.url)
        if resp is not None:
            resp_json = resp.json()
            if resp_json['code'] == 10000:
                print(resp_json['message'])
                return resp_json['code']
            elif resp_json['code'] == 20000:
                print(resp_json['message'])
                time.sleep(1)
                continue
            else:
                return resp_json['code']


# 获取翻译结果
def task_down(upload_task):
    data = {
        "downtype": 2,
        "tasktag": upload_task.task_tag,
        "productinfo": product_info,
        "usertoken": user_token,
        "deviceid": device_id,
        "account": account,
        "timestamp": int(time.time())
    }
    data_sign = md5(dict_to_str(data))
    data['datasign'] = data_sign
    resp = r.post(url=task_down_url, headers=okhttp_headers, data=data)
    resp_json = resp.json()
    download_url = resp_json.get('downurl')
    print(download_url)
    if download_url is not None:
        download_resp = r.get(download_url)
        if download_resp is not None:
            file_name = os.path.join(srt_save_dir, download_url.split('/')[-1])
            with open(file_name, 'wb') as f:
                f.write(download_resp.content)
                return file_name


# 解析srt文件提取时间及内容列表
def analyse_srt(srt_file_path):
    time_list = []
    text_list = []
    time_start_pos = 1
    text_start_pos = 2
    with open(srt_file_path, 'rb') as f:
        for i, value in enumerate(f.readlines()):
            if i == time_start_pos:
                time_list.append(value.decode().strip()[0:8])
                time_start_pos += 4
            elif i == text_start_pos:
                text_list.append(value.decode().strip())
                text_start_pos += 4
    return time_list, text_list


# 字幕写入
def save_subtitle(input_wav_path, output_mp3_path, subtitle_dir=None):
    # 文件转换
    os.system('ffmpeg -i {} -vn -ar 16000 -acodec libmp3lame {}'.format(input_wav_path, output_mp3_path))
    # 文件校验
    task = upload_par(output_mp3_path)
    time.sleep(2)
    # 文件上传
    upload_file(task, output_mp3_path)
    # 查询翻译状态
    task_state(task)
    # 下载翻译结果文件
    srt_file_name = task_down(task)
    if srt_file_name is not None:
        save_file_dir = os.path.join(subtitle_before_dir, '' if subtitle_dir is None else subtitle_dir + os.path.sep)
        cp_utils.is_dir_existed(save_file_dir)
        result_txt_file = os.path.join(save_file_dir, '{}.txt'.format(int(time.time())))
        with open(result_txt_file, 'w+', encoding='utf-8') as f:
            for text in analyse_srt(srt_file_name)[1]:
                f.writelines(text + '\n')
        print("文件写入完成：", result_txt_file)
        return result_txt_file


# md5加密
def md5(content):
    md = hashlib.md5()
    md.update(content.encode('utf-8'))
    return md.hexdigest()


# 字典转字符串
def dict_to_str(data_dict):
    # 按键升序排列
    sorted_tuple = sorted(data_dict.items(), key=lambda d: d[0], reverse=False)
    content = ''
    for t in sorted_tuple:
        content += '&{}={}'.format(t[0], t[1])
    content += 'hUuPd20171206LuOnD'
    if content.startswith("&"):
        content = content.replace("&", "", 1)
    return content


class TaskInfo:
    def __init__(self, task_tag, task_token, timestamp):
        self.task_tag = task_tag
        self.task_token = task_token
        self.timestamp = timestamp


if __name__ == '__main__':
    cp_utils.is_dir_existed(origin_video_dir)
    cp_utils.is_dir_existed(audio_after_dir)
    cp_utils.is_dir_existed(wav_to_mp3_dir)
    cp_utils.is_dir_existed(srt_save_dir)
    cp_utils.is_dir_existed(subtitle_after_dir)
    flv_file_list = cp_utils.filter_file_type(origin_video_dir, '.flv')
    mp4_file_list = cp_utils.filter_file_type(origin_video_dir, '.mp4')
    flv_file_list += mp4_file_list
    if len(flv_file_list) == 0:
        print("待处理视频为空")
        exit(0)
    print("\n请选择要提取字幕的视频序号：\n{}".format('=' * 64))
    for pos, video_path in enumerate(flv_file_list):
        print("{} → {}".format(pos, video_path))
    print("=" * 64)
    file_choose_index = int(input())
    file_choose_path = flv_file_list[file_choose_index]
    input_duration = int(input("请输入分割长度，单位s，输入0表示不切割直接转换 \n"))
    print("开始切割，请稍后...")
    wav_output_dir = video_to_wav(file_choose_path, input_duration)
    wav_file_list = cp_utils.filter_file_type(wav_output_dir, '.wav')
    print("切割完成，请选择后续操作：\n{}\n1、完整转换\n2、处理单独的视频片段\n{}".format('=' * 64, '=' * 64))
    translate_choose_input = int(input())
    if translate_choose_input == 1:
        print("开始转换全部音频")
        subtitle_path_list = []
        dir_name = str(int(time.time()))
        dir_name_path = os.path.join(wav_to_mp3_dir)
        cp_utils.is_dir_existed(dir_name_path)
        for index, wav_file in enumerate(wav_file_list):
            print("处理第{}段视频：{}".format(index + 1, wav_file))
            mp3_output_path = os.path.join(dir_name_path, '{}.mp3'.format(int(time.time())))
            subtitle_path_list.append(save_subtitle(wav_file, mp3_output_path, dir_name))
        # 合并多个字幕文件
        print("开始字幕合并...")
        all_subtitle = ''
        all_subtitle_file = os.path.join(subtitle_after_dir, '{}.txt'.format(int(time.time())))
        for txt in subtitle_path_list:
            with open(txt, 'r', encoding='utf-8') as tf:
                all_subtitle += tf.read()
        with open(all_subtitle_file, 'w+', encoding='utf-8') as atf:
            atf.write(all_subtitle)
        print("合并完毕，输出文件：", all_subtitle_file)
    else:
        print("\n请选择要处理音频片段序号：")
        for pos, wav_path in enumerate(wav_file_list):
            print("{} → {}".format(pos, wav_path))
        wav_choose_index = int(input())
        wav_input_path = wav_file_list[wav_choose_index]
        mp3_output_path = os.path.join(wav_to_mp3_dir, '{}.mp3'.format(int(time.time())))
        save_subtitle(wav_input_path, mp3_output_path)
