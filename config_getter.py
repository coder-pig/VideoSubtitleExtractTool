# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : config_getter.py
   Author   : CoderPig
   date     : 2021-01-13 11:33 
   Desc     : 读取配置文件配置
-------------------------------------------------
"""
import configparser
import os
import os.path


def get_config(section='config', key=None):
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config.ini'), encoding='utf8')
    return config.get(section, key)


def get_api(section='api', key=None):
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'api.ini'), encoding='utf8')
    return config.get(section, key)
