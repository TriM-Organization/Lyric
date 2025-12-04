# -*- coding: utf-8 -*-
"""
简单的歌词处理库
A library for parsing, reading & editing Lyrics


版权所有 © 2022-2025 金羿ELS、Baby2016 及 thecasttim
Copyright © 2022-2025 thecasttim & Baby2016 & Eilles

开源相关声明请见 仓库根目录下的 License.md
Terms & Conditions: License.md in the root directory
"""

# 睿乐组织 开发交流群 861684859
# Email TriM-Organization@hotmail.com
# 若需转载或借鉴 许可声明请查看仓库目录下的 License.md

from .main import Lyric
from .subclass import TimeStamp, SingleLine, MetaInfo
from .lrc.constants import (
    LRC_ID_TAG2META_NAME,
    STABLE_LRC_TIME_FORMAT_STYLE,
    LRC_TAG_PATTERN,
    LRC_TIME_PATTERN,
    LRC_ENHANCE_TIME_PATTERN_C,
    LRC_ENHANCE_TIME_PATTERN_N,
)

__version__ = "0.0.5"
__all__ = [
    #
    # 主类
    "Lyric",
    #
    # 副类
    "TimeStamp",
    "SingleLine",
    "MetaInfo",
    #
    # 常量
    "LRC_ID_TAG2META_NAME",
    "STABLE_LRC_TIME_FORMAT_STYLE",
    "LRC_TAG_PATTERN",
    "LRC_TIME_PATTERN",
    "LRC_ENHANCE_TIME_PATTERN_C",
    "LRC_ENHANCE_TIME_PATTERN_N",
]
__author__ = (("金羿", "Eilles"), ("Baby2016", "Baby2016"), ("thecasttim", "thecasttim"))
