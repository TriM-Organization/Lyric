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
版权所有© 全体 LyricLib 作者 及 thecasttim
Copyright 2022-2023 thecasttim and all the developers of LyricLib

开源相关声明请见 ../License.md
Terms & Conditions: ../License.md
"""

import codecs
from typing import Any, TextIO

from .constants import *
from .exceptions import *
from .subclass import *


@dataclass(init=False)
class Lyric:
    """歌词的操作以及数据类"""

    lyrics: Dict[TimeStamp, SingleLineLyric]
    """歌词字典，以一个时间戳对应一个单行歌词类"""

    meta_info: LyricMetaInfo
    """曲目基础信息"""

    extra_info: Dict[str, Any]
    """特殊信息字典"""

    def __init__(
        self,
        lyrics: Dict[TimeStamp, SingleLineLyric] = {},
        meta_info: LyricMetaInfo = LyricMetaInfo(),
    ):
        """
        建立一个歌词对象
        """

        self.lyrics = lyrics

        self.meta_info = meta_info

        self.extra_info = {}

    @classmethod
    def from_lrc(cls, lrc_path: str, lrc_encoding: str = "utf-8"):
        """
        从Lrc歌词文件获取歌词对象
        """
        with codecs.open(lrc_path, "r", encoding=lrc_encoding) as f:
            # 整个歌词文件的内容
            lrc_raw_text = f.read()

        lrc = cls()

        # 检查[]<>等标签括号是否匹配
        if not lrc.is_tags_valid(lrc_raw_text):
            raise LrcDestroyedError("标签括号未闭合")

        # 提取所有标签
        tags = [tag[1:-1] for tag in re.findall(LRC_TAG_PATTERN, lrc_raw_text)]
        """单行上的标签"""

        # 提取所有标签标注的内容
        segments = [
            segment.strip() for segment in re.split(LRC_TAG_PATTERN, lrc_raw_text)
        ]
        """标签后的文字"""

        segments = segments[1:]  # split结果包含第一个标签前的字符(包括空字符), 将其丢弃

        tags_num = len(tags)
        if tags_num != len(segments):
            raise LrcDestroyedError("不匹配的标签数与标注内容个数")

        # 逐段解析标签及其内容
        for i in range(0, tags_num):
            tag_type = lrc.get_tag_type(tags[i])

            # 判断标签是时间标签还是ID标签, 分别处理
            if tag_type == TagType.TIME:
                # 若为时间标签，载入歌词

                if lrc.is_enhanced(segments[i]):
                    # 增强格式（字词标签处理）
                    timestamps, parts = lrc.parse_enhanced_lrc(segments[i])

                    lrc.lyrics[
                        TimeStamp.from_lrc_time_tag(tags[i])
                    ] = SingleLineLyric.from_lrc_str_list(
                        "".join(parts), timestamps, parts[1:]
                    )
                else:
                    # 普通格式（单句标签）
                    lrc.lyrics[TimeStamp.from_lrc_time_tag(tags[i])] = SingleLineLyric(
                        segments[i]
                    )

            elif tag_type == TagType.ID:
                # 若为ID标签，载入信息字典中
                colon_pos = tags[i].find(":")
                lrc.meta_info.set_meta(
                    LRC_ID_TAG2META_NAME[tags[i][:colon_pos]], tags[i][colon_pos + 1 :]
                )

            elif tag_type == TagType.UNKNOWN:
                # 未知标签，独立载入
                lrc.extra_info[tags[i]] = segments[i]

        return lrc

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
        pair = {"]": "[", ">": "<"}
        for c in text:
            if c == "]" or c == ">":
                if not res or res[-1] != pair[c]:
                    return False
                res.pop()
            elif c == "[" or c == "<":
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
        time_tag_pattern = LRC_TIME_PATTERN
        # ID标签匹配模式
        id_tag_pattern = r"[a-zA-Z]*:.*"

        if re.match(time_tag_pattern, tag):
            return TagType.TIME
        elif re.match(id_tag_pattern, tag):
            return TagType.ID
        else:
            return TagType.UNKNOWN

    @staticmethod
    def is_enhanced(segment):
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

    @staticmethod
    def parse_enhanced_lrc(segment):
        """
        解析增强格式的歌词
        :param segment: 增强格式的歌词
        :return: timestamps: 时间戳列表, 由时间戳分割的各部分构成的列表
        """
        pattern = LRC_ENHANCE_TIME_PATTERN_N
        timestamps = [time[1:-1] for time in re.findall(pattern, segment)]
        parts = re.split(pattern, segment)
        return timestamps, parts

    @property
    def get_ids(self):
        # 获取 ID 标签列表
        return self.meta_info

    @property
    def get_lyrics(self):
        # 获取歌词列表
        return self.lyrics

    @property
    def get_unknowns(self):
        # 获取未知标签字段列表
        return self.extra_info

    def to_lrc(self, fdist: TextIO, time_format_style=STABLE_LRC_TIME_FORMAT_STYLE):
        """
        保存为LRC文件
        """
        for id, value in self.meta_info.lrc_id_dict().items():
            if value:
                fdist.write("[{}:{}]\n".format(id, value))
        for time, sentense in self.lyrics.items():
            fdist.write(
                "[{}]{}\n".format(
                    time.to_lrc_str(format_style=time_format_style),
                    sentense.to_lrc_str(format_style=time_format_style),
                )
            )
        for info_tag, value in self.extra_info.items():
            fdist.write("[{}]{}\n".format(info_tag, value))
