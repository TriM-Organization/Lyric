# -*- coding: utf-8 -*-

"""
针对 LRC 歌词文件类型的工具函数
"""

"""
版权所有 © 2022-2025 金羿ELS 及 thecasttim
Copyright © 2022-2025 thecasttim & Eilles

开源相关声明请见 仓库根目录下的 License.md
Terms & Conditions: License.md in the root directory
"""

# 睿乐组织 开发交流群 861684859
# Email TriM-Organization@hotmail.com
# 若需转载或借鉴 许可声明请查看仓库目录下的 License.md

import re

from enum import Enum
from typing import Tuple

from .constants import LRC_TIME_PATTERN, LRC_ENHANCE_TIME_PATTERN_N
from .exceptions import TimeTagError


class TagType(Enum):
    """标签类型类"""

    ID = 0  # ID标签
    TIME = 1  # 时间戳标签
    UNKNOWN = 2  # 未知标签

def parse_lrc_time_tag(time_tag_str) -> Tuple[int, ...]:
    """
    将LRC文件的字符串格式的时间戳解析为 时、分、秒、毫秒

    Parameters
    ----------
    time_tag_str: int
        时间戳字符串

    Returns
    -------

    tuple(int时, int分, int秒, int毫秒)
    """

    m = re.match(LRC_TIME_PATTERN, time_tag_str)
    if m:
        time_parts = m.groupdict()
    else:
        raise TimeTagError(time_tag_str)

    # 毫秒
    ms = 0
    if time_parts["p4"] is not None:
        # ".xxx秒" ---> 毫秒
        ms = int(float(time_parts["p4"]) * 1000)

    # 秒
    s = 0
    if time_parts["p3"] is not None:
        s = int(time_parts["p3"])

    # 小时与分钟
    if time_parts["p2"] is None:
        h = 0
        if time_parts["p1"] is not None:
            # <p1>xx:<p3>xx(<p4>.xx)形式( xx:xx(.xx) )
            minute = int(time_parts["p1"][:-1])
            if minute >= 60:
                h = minute // 60
                minute = minute % 60
        else:
            # <p3>xx(<p4>.xx)形式( xx(.xx) )
            minute = 0
    else:
        h = int(time_parts["p1"][:-1])
        minute = int(time_parts["p2"][:-1])

    return h, minute, s, ms





def is_lrc_tag_valid(text):
    """
    检查标签括号是否匹配
    :param text: lrc歌词文件完整内容
    :return: 如果[]与<>匹配则返回True，否则返回False
    """
    if text is None:
        return True

    res = list()
    pair = {"]": "[", ">": "<"}
    for c in text:
        if c == "]" or c == ">":
            if not res or res[-1] != pair[c]:
                return False
            res.pop()
        elif c == "[" or c == "<":
            res.append(c)

    return len(res) == 0



def get_lrc_tag_type(tag):
    """
    获取标签类型
    :param tag: 标签
    :return: tag_type: 标签类型
    """
    # 时间戳标签匹配模式
    time_tag_pattern = LRC_TIME_PATTERN
    # ID标签匹配模式
    id_tag_pattern = r"[a-zA-Z]*:.*"

    if re.match(time_tag_pattern, tag):
        return TagType.TIME
    elif re.match(id_tag_pattern, tag):
        return TagType.ID
    else:
        return TagType.UNKNOWN


def is_lrc_segment_enhanced(segment):
    """
    判断是否是增强格式
    :param segment: 一段歌词
    :return: True, 包含增强格式的时间戳, False, 不含增强格式的时间戳
    """
    pattern = LRC_ENHANCE_TIME_PATTERN_N
    m = re.search(pattern, segment)
    if m is not None:
        return True
    else:
        return False


def parse_lrc_enhanced_segment(segment):
    """
    解析增强格式的歌词
    :param segment: 增强格式的歌词
    :return: timestamps: 时间戳列表, 由时间戳分割的各部分构成的列表
    """
    pattern = LRC_ENHANCE_TIME_PATTERN_N
    timestamps = [time[1:-1] for time in re.findall(pattern, segment)]
    parts = re.split(pattern, segment)
    return timestamps, parts
