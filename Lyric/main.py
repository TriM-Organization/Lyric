# -*- coding: UTF-8 -*-
"""歌词的处理工具

此部分的代码由 thecasttim 的 [lrc-parser](https://gitee.com/thecasttim/lrc-parser) 项目改编而来

引用协议：
    MIT License

    Copyright (c) 2021 thecasttim

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

继承协议：
版权所有© 全体 Lyric 作者 及 thecasttim

   Copyright 2022-2023 thecasttim and all the developers of Lyric

   Licensed under the Apache License, Version 2.0 (the 'License');
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       https://www.apache.org/licenses/LICENSE-2.0
"""

import codecs
import re
from enum import Enum


# 标签类型
class TagType(Enum):
    ID = 0          # ID标签
    TIME = 1        # 时间戳标签
    UNKNOWN = 2      # 未知标签


# 正则表达式
# 标签匹配模式
TAG_PATTERN = r"\[.*?\]"
# 时间戳标签匹配模式
# (hh:)mm:ss(.xxx)
# hh:mm:ss(.xxx)时, hh可为任意整数, mm和ss在0~59之间, xxx在0~999之间或省略;
# mm:ss(.xxx)时, mm可为任意整数, ss在0~59之间, xxx在0~999之间或省略;
# TIME_PATTERN = r"^(\d+:){0,1}([0-5][0-9]:){0,1}([0-5][0-9])(\.[\d]{1,3}){0,1}$"
TIME_PATTERN = r"^(?P<p1>\d+:){0,1}(?P<p2>[0-5][0-9]:){0,1}(?P<p3>[0-5][0-9])(?P<p4>\.[\d]{1,3}){0,1}$"    # 命名分组
ENHANCE_TIME_PATTERN_C = r"\<(\d+\:){0,1}([0-5][0-9]\:){0,1}([0-5][0-9])(\.[\d]{1,3}){0,1}\>"   # 捕获分组
ENHANCE_TIME_PATTERN_N = r"\<(?:\d+\:){0,1}(?:[0-5][0-9]\:){0,1}(?:[0-5][0-9])(?:\.[\d]{1,3}){0,1}\>"    # 非捕获分组



class Lyric:
    """歌词的操作"""
    def __init__(self,):
        '''建立一个歌词对象'''

        # 歌词列表
        #   每个元素为字典{
        #                'time': ...,
        #                'lyric': ...,
        #                'extends': {'timestamps': [...], 'parts': [...]}
        #               }
        #   -- time: 每段歌词前时间标签所标注的时间
        #   -- lyric：本time到下一个time标注之间的这段歌词(如:"[time1]lyric/n[time2]")
        #   -- parts：对于含有<mm:ss.xx>的增强格式的内容切分后的列表
        self.lyrics = []

        # ID标签列表, 每个元素为( 'ID', '内容' )
        self.IDs = []

        # 未知标签类型, 每个元素为('标签', '内容')
        self.unknown_texts = []



    def from_lrc(self, lrc_path: str, lrc_encoding: str = 'utf-8'):
        '''
        从Lrc歌词文件打开
        '''
        with codecs.open(lrc_path, 'r', encoding=lrc_encoding) as f:
            # 整个歌词文件的内容
            lrc_raw_text = f.read()

        # 检查[]<>等标签括号是否匹配
        if not self.is_tags_valid(lrc_raw_text):
            raise SyntaxError('文件损坏：标签括号未闭合')

        # 歌词列表
        #   每个元素为字典{
        #                'time': ...,
        #                'lyric': ...,
        #                'extends': {'timestamps': [...], 'parts': [...]}
        #               }
        #   -- time: 每段歌词前时间标签所标注的时间
        #   -- lyric：本time到下一个time标注之间的这段歌词(如:"[time1]lyric/n[time2]")
        #   -- parts：对于含有<mm:ss.xx>的增强格式的内容切分后的列表
        self.lyrics = []

        # ID标签列表, 每个元素为('ID', '内容')
        self.IDs = []

        # 未知标签类型, 每个元素为('标签', '内容')
        self.unknown_texts = []

        # 提取所有标签
        tags = [tag[1:-1] for tag in re.findall(TAG_PATTERN, lrc_raw_text)]

        # 提取所有标签标注的内容
        segments = [segment.strip() for segment in re.split(TAG_PATTERN, lrc_raw_text)]
        segments = segments[1:]          # split结果包含第一个标签前的字符(包括空字符), 将其丢弃

        tags_num = len(tags)
        if tags_num != len(segments):
            raise ValueError('文件损坏：不匹配的标签数与标注内容个数')

        # 逐段解析标签及其内容
        for i in range(0, tags_num):
            tag_type = self.get_tag_type(tags[i])

            # 判断标签是时间标签还是ID标签, 分别处理
            if tag_type == TagType.TIME:
                res = {'time': tags[i]}

                if self.is_enhanced(segments[i]):
                    # 增强格式
                    timestamps, parts = self.parse_enhanced_lrc(segments[i])
                    res['lyric'] = "".join(parts)
                    res['extends'] = {'timestamps': timestamps, 'parts': parts}
                else:
                    # 普通格式
                    res['lyric'] = segments[i]
                    res['extends'] = None
                self.lyrics.append(res)

            elif tag_type == TagType.ID:
                colon_pos = tags[i].find(":")
                self.IDs.append((tags[i][:colon_pos], tags[i][colon_pos + 1:]))

            elif tag_type == TagType.UNKNOWN:
                self.unknown_texts.append((tags[i], segments[i]))

    @staticmethod
    def is_tags_valid(text):
        """
        检查标签括号是否匹配
        :param text: lrc歌词文件完整内容
        :return: 如果[]与<>匹配则返回True，否则返回False
        """
        if text is None:
            return True

        res = list()
        pair = {']': '[', '>': '<'}
        for c in text:
            if c == ']' or c == '>':
                if not res or res[-1] != pair[c]:
                    return False
                res.pop()
            elif c == '[' or c == '<':
                res.append(c)

        return len(res) == 0

    @staticmethod
    def get_tag_type(tag):
        """
        获取标签类型
        :param tag: 标签
        :return: tag_type: 标签类型
        """
        # 时间戳标签匹配模式
        time_tag_pattern = TIME_PATTERN
        # ID标签匹配模式
        id_tag_pattern = r"[a-zA-Z]*:.*"

        if re.match(time_tag_pattern, tag):
            return TagType.TIME
        elif re.match(id_tag_pattern, tag):
            return TagType.ID
        else:
            return TagType.UNKNOWN

    @staticmethod
    def parse_time_tag(tag):
        """
        将时间戳解析为 时、分、秒、毫秒
        :param tag: 时间戳字符串
        :return: 时、分、秒、毫秒(整数)
        """
        time_pattern = TIME_PATTERN

        m = re.match(time_pattern, tag)
        time_parts = m.groupdict()

        # 毫秒
        ms = 0
        if time_parts['p4'] is not None:
            # ".xxx秒" ---> 毫秒
            ms = int(float(time_parts['p4']) * 1000)

        # 秒
        s = 0
        if time_parts['p3'] is not None:
            s = int(time_parts['p3'])

        # 小时与分钟
        if time_parts['p2'] is None:
            h = 0
            if time_parts['p1'] is not None:
                # <p1>xx:<p3>xx(<p4>.xx)形式( xx:xx(.xx) )
                minute = int(time_parts['p1'][:-1])
                if minute >= 60:
                    h = minute // 60
                    minute = minute % 60
            else:
                # <p3>xx(<p4>.xx)形式( xx(.xx) )
                minute = 0
        else:
            h = int(time_parts['p1'][:-1])
            minute = int(time_parts['p2'][:-1])

        return h, minute, s, ms

    @staticmethod
    def is_enhanced(segment):
        """
        判断是否是增强格式
        :param segment: 一段歌词
        :return: True, 包含增强格式的时间戳, False, 不含增强格式的时间戳
        """
        pattern = ENHANCE_TIME_PATTERN_N
        m = re.search(pattern, segment)
        if m is not None:
            return True
        else:
            return False

    @staticmethod
    def parse_enhanced_lrc(segment):
        """
        解析增强格式的歌词
        :param segment: 增强格式的歌词
        :return: timestamps: 时间戳列表, 由时间戳分割的各部分构成的列表
        """
        pattern = ENHANCE_TIME_PATTERN_N
        timestamps = [time[1:-1] for time in re.findall(pattern, segment)]
        parts = re.split(pattern, segment)
        return timestamps, parts

    @property
    def get_ids(self):
        # 获取 ID 标签列表
        return self.IDs

    @property
    def get_lyrics(self):
        # 获取歌词列表
        return self.lyrics

    @property
    def get_unknowns(self):
        # 获取未知标签字段列表
        return self.unknown_texts


if __name__ == "__main__":

    lrc = Lyric("test.lrc")

    print("ID:")
    for item in lrc.get_ids:
        print(item)
    print("-" * 60)

    print("歌词:")
    for item in lrc.get_lyrics:
        print(item)
        if item['extends'] is not None:
            print("  增强型格式：")
            for key, val in item['extends'].items():
                print(f"\t{key}: {val}")
    print("-" * 60)

    print("未知:")
    for item in lrc.get_unknowns:
        print(item)
    print("-" * 60)

    print("解析时间戳:")
    # 解析时间戳
    tag = "11:22:33.66"
    h, m, s, ms = lrc.parse_time_tag(tag)
    print(tag, "--->", h, m, s, ms)
