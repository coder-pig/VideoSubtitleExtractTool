# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : config_getter.py
   Author   : CoderPig
   date     : 2021-01-13 11:33 
   Desc     : 
-------------------------------------------------
"""
import configparser
import os
import os.path


def get_config(section='config', key=None):
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config.ini'), encoding='utf8')
    return config.get(section, key)


def get_user(section='user', key=None):
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'user.ini'), encoding='utf8')
    return config.get(section, key)
