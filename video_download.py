# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : video_download.py
   Author   : CoderPig
   date     : 2021-09-30 10:03 
   Desc     : 下载视频(除B站提供破解下载外，默认使用you_get下载)
-------------------------------------------------
"""
import json
import os
import re
import time
from http import cookiejar

import requests as r
from idm import IDMan
from you_get import common as you_get

import config_getter
import media_utils

base_url = 'https://www.bilibili.com'
play_url = 'https://api.bilibili.com/x/player/playurl'
page_list_url = 'https://api.bilibili.com/x/player/pagelist'

# 获取视频信息的正则
bv_pattern = re.compile(r'(BV.{10})', re.S)
play_info_pattern = re.compile(r'window\.__playinfo__=(\{.*?\})</script>', re.MULTILINE | re.DOTALL)
initial_state_pattern = re.compile(r'window\.__INITIAL_STATE__=(\{.*?\});', re.MULTILINE | re.DOTALL)
url_match_pattern = re.compile(r'((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?',
                               re.S)

# 保存文件的目录
video_before_dir = os.path.join(os.getcwd(), config_getter.get_config(key='video_before_dir'))
origin_video_dir = os.path.join(os.getcwd(), config_getter.get_config(key='origin_video_dir'))
audio_after_dir = os.path.join(os.getcwd(), config_getter.get_config(key='audio_after_dir'))
subtitle_before_dir = os.path.join(os.getcwd(), config_getter.get_config(key='subtitle_before_dir'))
subtitle_after_dir = os.path.join(os.getcwd(), config_getter.get_config(key='subtitle_after_dir'))
cookies_dir = os.path.join(os.getcwd(), config_getter.get_config(key='cookies_dir'))

# 清晰度
support_formats_dict = {
    116: '1080P 60帧',
    80: '1080P 高清',
    64: '720P 60帧',
    32: '480P 清晰',
    16: '360P 流畅'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/83.0.4103.97 Safari/537.36',
    'Origin': base_url
}

# B站Cookie文件
cookies_file_path = os.path.join(cookies_dir, 'bilibili.txt')
cookies_jar = cookiejar.MozillaCookieJar(cookies_file_path) if os.path.exists(cookies_file_path) else None


# 获取mp4视频
def fetch_mp4_video_url(b_video):
    params = {
        'cid': b_video.cid,
        'bvid': b_video.bvid,
        'qn': 112,
        'type': '',
        'otype': 'json',
        'fourk': 1,
        'fnver': 0,
        'fnval': 80,
        'avid': b_video.avid
    }
    resp = r.get(url=play_url, params=params, headers=headers, cookies=cookies_jar)
    if resp is not None:
        video_list = []
        audio_list = []
        resp_json = resp.json()
        dash = resp_json['data'].get('dash')
        if dash is not None:
            videos = dash.get('video')
            if videos is not None:
                for video in videos:
                    video_list.append([video['baseUrl'], video['mimeType'], video['codecs'], video['id']])
            audios = dash.get('audio')
            if audios is not None:
                for audio in audios:
                    audio_list.append([audio['baseUrl'], audio['mimeType'], audio['codecs']])
        return video_list, audio_list


# B站视频类
class BVideo:
    def __init__(self, title=None, cid=None, bvid=None, avid=None, mp4_url=None, wav_url=None,
                 merge_video=None):
        self.title = title
        self.cid = cid
        self.bvid = bvid
        self.avid = avid
        self.mp4_url = mp4_url
        self.wav_url = wav_url
        self.merge_video = merge_video

    def to_str(self):
        return '{}-{}-{}-{}-{}-{}-{}'.format(self.title, self.cid, self.bvid, self.avid,
                                             self.mp4_url, self.wav_url, self.merge_video)


# 获取B站视频列表
def fetch_b_video_list(url):
    if headers.get("Referer") is not None:
        headers.pop('Referer')
    bv_result = bv_pattern.search(url)
    if bv_result is not None:
        params = {
            'bvid': bv_result.group(1),
            'jsonp': 'jsonp'
        }
        b_video_list = []
        resp = r.get(url=page_list_url, headers=headers, params=params, cookies=cookies_jar)
        print("请求：", resp.url)
        if resp is not None:
            resp_json = resp.json()
            pages_json = resp_json.get('data')
            if pages_json is not None:
                for page in pages_json:
                    b_video = BVideo(bvid=bv_result.group(1))
                    b_video.cid = page['cid']
                    b_video.title = page['part'].replace(' ', '')
                    b_video_list.append(b_video)
                return b_video_list
    else:
        print("URL格式错误")


# 获取B站视频数据
def fetch_b_video_info(url):
    if headers.get("Referer") is not None:
        headers.pop('Referer')
    b_video_list = []
    resp = r.get(url=url, headers=headers, cookies=cookies_jar)
    if resp is not None:
        support_formats_dict_list = []
        resp_text = resp.text
        # 获取支持的清晰度
        play_info_result = play_info_pattern.search(resp_text)
        if play_info_result is not None:
            result_json = json.loads(play_info_result.group(1))
            support_formats_dict_json = result_json['data']['support_formats_dict']
            for support_format in support_formats_dict_json:
                quality = support_formats_dict.get(support_format['quality'])
                if quality is not None:
                    support_formats_dict_list.append(quality)
                else:
                    support_formats_dict_list.append(support_format['quality'])
        initial_result = initial_state_pattern.search(resp_text)
        if initial_result is not None:
            result_json = json.loads(initial_result.group(1))
            video_data = result_json['videoData']
            avid = video_data['aid']
            bvid = video_data['bvid']
            pages_json = video_data.get('pages')
            if pages_json is not None:
                for page_json in pages_json:
                    b_video = BVideo(avid=avid, bvid=bvid)
                    b_video.cid = page_json['cid']
                    b_video.title = page_json['part']
                    b_video_list.append(b_video)
        return support_formats_dict_list, b_video_list


# 获取mp4视频
def fetch_mp4_video_url(b_video):
    params = {
        'cid': b_video.cid,
        'bvid': b_video.bvid,
        'qn': 112,
        'type': '',
        'otype': 'json',
        'fourk': 1,
        'fnver': 0,
        'fnval': 80,
        'avid': b_video.avid
    }
    resp = r.get(url=play_url, params=params, headers=headers, cookies=cookies_jar)
    if resp is not None:
        video_list = []
        audio_list = []
        resp_json = resp.json()
        dash = resp_json['data'].get('dash')
        if dash is not None:
            videos = dash.get('video')
            if videos is not None:
                for video in videos:
                    video_list.append([video['baseUrl'], video['mimeType'], video['codecs'], video['id']])
            audios = dash.get('audio')
            if audios is not None:
                for audio in audios:
                    audio_list.append([audio['baseUrl'], audio['mimeType'], audio['codecs']])
        return video_list, audio_list


# 普通方式下载资源
def download_normal(url, referer_url, file_type, title=''):
    headers['Referer'] = referer_url
    print("下载：", url)

    file_name = '{}{}{}_{}.{}'.format(video_before_dir, os.path.sep, title, str(int(round(time.time() * 1000))),
                                      file_type)
    resp = r.get(url=url, headers=headers)
    with open(file_name, "wb+") as f:
        f.write(resp.content)
        print("下载完成：", resp.url)
    return file_name


# IDM方式下载
def download_idm(url, referer_url, file_type, title=''):
    print("下载：", url)
    file_name = '{}_{}.{}'.format(title, str(int(round(time.time() * 1000))), file_type)
    downloader = IDMan()
    downloader.download(url, path_to_save=video_before_dir, output=file_name, referrer=referer_url)
    print("下载完成：", url)
    return os.path.join(video_before_dir, file_name)


# you-get下载
def you_get_download(url):
    # 判断是否为B站视频，检索是否有cookies文件，有的话设置下
    if url.find('bilibili') != -1:
        if os.path.exists(cookies_file_path):
            you_get.load_cookies(cookies_file_path)
    you_get.any_download(url=url, info_only=False, output_dir=origin_video_dir, merge=True)


# 功能入口
def function():
    while True:
        input_url = input("请输入要下载的URL(输入quit退出下载)：\n")
        url_match_result = url_match_pattern.match(input_url)
        if url_match_result is None:
            if input_url == "quit":
                break
            else:
                print("链接格式错误，请输入正确的URL")
        else:
            if input_url.find("bilibili") != -1:
                print("检测到链接为B站链接，请选择下载方式：\n {}\n1、破解下载\n2、you-get下载\n{}".format('=' * 64, '=' * 64))
                download_type_input = int(input())
                if download_type_input == 1:
                    v_list = fetch_b_video_list(input_url)
                    print("\n检测到多P，请输入想要下载的视频序号：\n{}".format('=' * 64))
                    for index, value in enumerate(v_list):
                        print('{}、{}'.format(index, value.title))
                    print("=" * 64)
                    part_choose = int(input())
                    if 0 <= part_choose < len(v_list):
                        choose_video = v_list[part_choose]
                        print("解析：{}".format(choose_video.title))
                        video_result = fetch_mp4_video_url(choose_video)
                        if video_result is not None:
                            video_urls = video_result[0]
                            audio_urls = video_result[1]
                            if len(video_urls) > 0 and len(audio_urls) > 0:
                                print("检测到多种视频源，请输入想要下载的画质序号：\n{}".format('=' * 64))
                                for index, value in enumerate(video_urls):
                                    quality_str = support_formats_dict.get(value[3])
                                    print('{}、{} {} {}'.format(index, quality_str, value[1], value[2]))
                                print("=" * 64)
                                video_choose = int(input())
                                bv_video_url = video_urls[video_choose][0]
                                bv_audio_url = audio_urls[0][0]
                                download_type_choose = int(
                                    input("请输入下载方式：\n{}\n0、requests\n1、idm\n{}\n".format('=' * 64, '=' * 64)))
                                after_video_path = os.path.join(origin_video_dir,
                                                                '{}_after.{}'.format(choose_video.title, 'mp4'))
                                if download_type_choose == 0:
                                    b_video_path = download_normal(bv_video_url, input_url, 'mp4', choose_video.title)
                                    b_audio_path = download_normal(bv_audio_url, input_url, 'mp4', choose_video.title)
                                    print("音视频下载完毕，准备合并")
                                    media_utils.merge_mp4_wav(b_video_path, b_audio_path, after_video_path)
                                elif download_type_choose == 1:
                                    b_video_path = download_idm(bv_video_url, input_url, 'mp4', choose_video.title)
                                    b_audio_path = download_idm(bv_audio_url, input_url, 'mp4', choose_video.title)
                                    # idm是异步的，拿不到下载进度，这里休眠30s，避免等下出现文件未合并的情况
                                    time.sleep(60)
                                    print("音视频下载完毕，准备合并")
                                    media_utils.merge_mp4_wav(b_video_path, b_audio_path, after_video_path)
                                else:
                                    print("输出错误")
                                    exit(0)
                        else:
                            print("无法解析视频源地址")
                elif download_type_input == 2:
                    you_get_download(input_url)
            else:
                print("检测到非B站链接，默认采用you-get下载")
                you_get_download(input_url)