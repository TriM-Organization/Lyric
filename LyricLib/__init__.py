# -*- coding: utf-8 -*-
"""
简单的歌词处理库
A library for parsing, reading & editing Lyrics

版权所有© 2022-2023 全体 LyricLib 作者 及 thecasttim
Copyright 2022-2023 thecasttim and all the developers of LyricLib

开源相关声明请见 ../License.md
Terms & Conditions: ../License.md
"""

# 睿穆组织 开发交流群 861684859
# Email TriM-Organization@hotmail.com
# 版权所有 Lyric全体开发者
# 若需转载或借鉴 许可声明请查看仓库目录下的 License.md

from .main import *

__version__ = "0.0.4"
__all__ = [

    # 主类
    "Lyric",

    # 副类
    "TimeStamp",
    "SingleLineLyric",
    "LyricMetaInfo",
    
    # 常量
    "LRC_ID_TAG2META_NAME",
    "STABLE_LRC_TIME_FORMAT_STYLE",
    "LRC_TAG_PATTERN",
    "LRC_TIME_PATTERN",
    "LRC_ENHANCE_TIME_PATTERN_C",
    "LRC_ENHANCE_TIME_PATTERN_N",
]
__author__ = (("金羿", "Eilles Wan"), ("thecasttim", "thecasttim"))
