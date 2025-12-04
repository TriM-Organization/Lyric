# -*- coding: utf-8 -*-

"""
词幕库下属子类
"""

"""
版权所有 © 2022-2025 金羿ELS、Baby2016 及 thecasttim
Copyright © 2022-2025 thecasttim & Baby2016 & Eilles

开源相关声明请见 仓库根目录下的 License.md
Terms & Conditions: License.md in the root directory
"""

# 睿乐组织 开发交流群 861684859
# Email TriM-Organization@hotmail.com
# 若需转载或借鉴 许可声明请查看仓库目录下的 License.md


from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union, Optional, Literal

from PIL import ImageColor, Image, ImageFont
from datetime import time, timedelta

from .exceptions import TimeTooPreciseError
from .constants import HOUR, MINUTE, SECOND, MILLISECOND, CENTISECOND

from .lrc.constants import LRC_ID_TAG2META_NAME, STABLE_LRC_TIME_FORMAT_STYLE
from .lrc.exceptions import LrcDestroyedError, WordTagError

from .lrc.utils import parse_lrc_time_tag




@dataclass(init=False)
class TimeStamp:
    """时间戳类"""

    _hours: int
    _minutes: int
    _seconds: int
    _milliseconds: int

    def __init__(
        self,
        hour: Union[float, int] = 0,
        min: Union[float, int] = 0,
        sec: Union[float, int] = 0,
        ms: int = 0,
    ):
        """
        定义一个时间戳

        Parameters
        ----------
        hour, min, sec, ms 正如其名
        分别是距离开始时的 时、分、秒、毫秒
        """

        if ms != int(ms):
            raise TimeTooPreciseError("毫秒不应为小数。")

        millisec = ms + sec * 1000 + min * 60000 + hour * 360000

        self._milliseconds = int(millisec % 1000)
        self._seconds = int(millisec / 1000 % 60)
        self._minutes = int(millisec / 60000 % 60)
        self._hours = int(millisec / 360000)

    # 只读属性
    @property
    def hours(self):
        """时"""
        return self._hours

    @property
    def minutes(self):
        """分"""
        return self._minutes

    @property
    def seconds(self):
        """秒"""
        return self._seconds

    @property
    def milliseconds(self):
        """毫秒"""
        return self._milliseconds


    @property
    def in_hours(self) -> float:
        """以小时为单位的时间戳"""
        return (
            self._hours
            + self._minutes / 60
            + self._seconds / 360
            + self._milliseconds / 360000
        )

    @property
    def in_minutes(self) -> float:
        """以分钟为单位的时间戳"""
        return (
            self._hours * 60
            + self._minutes
            + self._seconds / 60
            + self._milliseconds / 60000
        )

    @property
    def in_seconds(self) -> float:
        """以秒为单位的时间戳"""
        return (
            self._hours * 360
            + self._minutes * 60
            + self._seconds
            + self._milliseconds / 1000
        )

    @property
    def in_milliseconds(self) -> int:
        """以毫秒为单位的时间戳"""
        return (
            self._hours * 360000
            + self._minutes * 60000
            + self._seconds * 1000
            + self._milliseconds
        )

    def __tuple__(self) -> Tuple[int, int, int, int]:
        return (self._hours, self._minutes, self._seconds, self._milliseconds)

    def __dict__(self) -> Dict[str, int]:
        return {
            HOUR: self._hours,
            MINUTE: self._minutes,
            SECOND: self._seconds,
            MILLISECOND: self._milliseconds,
        }

    def __hash__(self) -> int:
        return self.in_milliseconds

    def __str__(self) -> str:
        """
        直接以最完整的格式输出字符串
        """
        return "{}:{}:{}.{}".format(
            self._hours, self._minutes, self._seconds, self._milliseconds
        )

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, TimeStamp)
            and (self._hours == other._hours)
            and (self._minutes == other._minutes)
            and (self._seconds == other._seconds)
            and (self._milliseconds == other._milliseconds)
        )

    def __lt__(self, other) -> bool:
        """
        判小于
        """
        if isinstance(other, TimeStamp):
            if self._hours < other.hours:
                return True
            elif self._minutes < other.minutes:
                return True
            elif self._seconds < other.seconds:
                return True
            elif self._milliseconds < other.milliseconds:
                return True
            return False
        else:
            return NotImplemented
    def __gt__(self, other) -> bool:
        """
        判大于
        """
        return other.__lt__(self)

    def __add__(self, other) -> "TimeStamp":
        if isinstance(other, TimeStamp):
            return TimeStamp(hour=self.hours + other.hours,                             min=self.minutes + other.minutes,sec=self.seconds + other.seconds,                             ms=self.milliseconds + other.milliseconds)
        else:
            return NotImplemented


    # 打包支持 Pickle

    def _getstate(self):
        return self.__tuple__()

    def __reduce__(self):
        return (self.__class__, self._getstate())

    @classmethod
    def from_lrc_timetag(cls, time_tag_str: str):
        """
        从Lrc歌词文件的时间标签读取时间戳

        Parameters
        ----------

        time_tag_str: str
            Lrc歌词文件的字符串时间标签
        """

        try:
            # print(time_tag_str)
            return cls(
                *parse_lrc_time_tag(time_tag_str.replace("[", "").replace("]", ""))
            )
        except TimeTooPreciseError:
            raise LrcDestroyedError(
                "时间标签出现错误: {}".format(time_tag_str), time_tag_str
            )

    def to_lrc_timetag(self, format_style: str = STABLE_LRC_TIME_FORMAT_STYLE) -> str:
        """
        以特定样式的LRC格式的时间标签返回字符串
        """

        return format_style.format(
            **{
                unit: value
                for unit, value in {
                    **self.__dict__(),
                    **{CENTISECOND: self._milliseconds / 10},
                }.items()
                if unit in format_style
            }
        )


class LocationAnchor(Enum):
    """字幕位置锚点"""

    # 第一个值是横轴位置，第二是纵轴位置
    TOP_LEFT = (-1, -1)
    TOP_CENTER = (0, -1)
    TOP_RIGHT = (1, -1)
    MIDDLE_LEFT = (-1, 0)
    MIDDLE_CENTER = (0, 0)
    MIDDLE_RIGHT = (1, 0)
    BOTTOM_LEFT = (-1, 1)
    BOTTOM_CENTER = (0, 1)
    BOTTOM_RIGHT = (1, 1)

    def __tuple__(self) -> Tuple[Literal[-1,0,1], Literal[-1,0,1]]:
        return self.value

    # 打包支持 Pickle

    def _getstate(self):
        return self.__tuple__()

    def __reduce__(self):
        return (self.__class__, self._getstate())


@dataclass(init=False)
class LineLocation:
    """歌词位置"""

    archer: LocationAnchor
    """定位点"""
    offset: Tuple[int, int]
    """偏移量，单位屏幕百分比"""


@dataclass(init=False)
class StyledLine:
    """字体样式"""

    font_name: str
    font_size: int
    bold: bool
    italic: bool
    underline: int
    outline: int
    foreground_colour: str
    background_colour: str
    opacity: str
    context: str





@dataclass(init=False)
class SingleLine:
    """一句词，这里的 Line 指的是台词"""


    location: LineLocation
    context: List[StyledLine]
    duration: Optional[TimeStamp]
    word_extension: Optional[Dict[TimeStamp, str]]

    def __init__(
        self,
        sentence: str,
        duration: Optional[TimeStamp] = None,
        extension: Optional[Dict[TimeStamp, str]] = None,
    ):
        """建立一句歌词"""
        self.context = sentence
        self.duration = duration
        self.word_extension = extension

    def __str__(self) -> str:
        if self.word_extension:
            return "".join(
                [
                    r"<{}>{}".format(time.to_lrc_timetag(), word)
                    for time, word in self.word_extension.items()
                ]
            )
        else:
            return self.context

    @classmethod
    def from_lrc_str_dict(cls, sentence: str, **extension):
        """从LRC时间标签字符串而组成的字典中获取附加信息"""
        word_extension = {}
        for time_str, word in extension.items():
            word_extension[TimeStamp.from_lrc_timetag(time_tag_str=time_str)] = word
        return cls(sentence, extension=word_extension)

    @classmethod
    def from_lrc_str_list(
        cls, sentence: str, time_str_list: List[str], word_list: List[str]
    ):
        """从LRC时间列表和单词列表中获取附加信息"""
        time_list_length = len(time_str_list)
        word_list_length = len(word_list)
        if time_list_length != word_list_length:
            raise WordTagError(
                word_list_length < time_list_length, time_str_list, word_list
            )
        word_extension = {}
        for i in range(time_list_length):
            # print("=====")
            # print(time_str_list[i],TimeStamp.from_lrc_time_tag(time_str_list[i]),word_list[i])
            word_extension[
                TimeStamp.from_lrc_timetag(time_tag_str=time_str_list[i])
            ] = word_list[i]
            # print("=====")
        return cls(sentence, extension=word_extension)

    def to_lrc_str(self, format_style: str = r"{mm}:{ss}.{xx}") -> str:
        """
        以特定样式的LRC格式的时间标签返回整句
        """
        if self.word_extension:
            return "".join(
                [
                    r"<{}>{}".format(
                        time.to_lrc_timetag(format_style=format_style), word
                    )
                    for time, word in self.word_extension.items()
                ]
            )
        else:
            return self.context


@dataclass(init=False)
class MetaInfo:
    """歌词元信息"""

    Singer: str
    Album: str
    Title: str
    LyricAuthor: str
    Composer: str
    Arranger: str
    Length: str
    Recorder: str
    Editor: str
    Version: str
    Offset: str
    Other: Dict[str, str]

    def __init__(
        self,
        Singer: str = "",
        Album: str = "",
        Title: str = "",
        LyricAuthor: str = "",
        Composer: str = "",
        Arranger: str = "",
        Length: str = "",
        Recorder: str = "",
        Editor: str = "",
        Version: str = "",
        Offset: str = "",
        Other: Dict[str, str] = {},
    ) -> None:
        """建立一歌之元"""
        self.Singer = Singer
        self.Album = Album
        self.Title = Title
        self.LyricAuthor = LyricAuthor
        self.Composer = Composer
        self.Arranger = Arranger
        self.Length = Length
        self.Recorder = Recorder
        self.Editor = Editor
        self.Version = Version
        self.Offset = Offset
        self.Other = Other

    def __dict__(self):
        result = {
            "Singer": self.Singer,
            "Album": self.Album,
            "Title": self.Title,
            "LyricAuthor": self.LyricAuthor,
            "Composer": self.Composer,
            "Arranger": self.Arranger,
            "Length": self.Length,
            "Recorder": self.Recorder,
            "Editor": self.Editor,
            "Version": self.Version,
            "Offset": self.Offset,
        }
        result.update(self.Other)
        return result

    def set_meta(self, meta_name: str, meta_value: str):
        """设置单个元信息"""
        if meta_name == "Singer":
            self.Singer = meta_value
        elif meta_name == "Album":
            self.Album = meta_value
        elif meta_name == "Title":
            self.Title = meta_value
        elif meta_name == "LyricAuthor":
            self.LyricAuthor = meta_value
        elif meta_name == "Composer":
            self.Composer = meta_value
        elif meta_name == "Arranger":
            self.Arranger = meta_value
        elif meta_name == "Length":
            self.Length = meta_value
        elif meta_name == "Recorder":
            self.Recorder = meta_value
        elif meta_name == "Editor":
            self.Editor = meta_value
        elif meta_name == "Version":
            self.Version = meta_value
        elif meta_name == "Offset":
            self.Offset = meta_value
        else:
            self.Other[meta_name.capitalize()] = meta_value

    def lrc_id_dict(self):
        """
        返回LRC文件中所需的ID字典
        """
        result = LRC_ID_TAG2META_NAME
        now_d = {
            "Singer": self.Singer,
            "Album": self.Album,
            "Title": self.Title,
            "LyricAuthor": self.LyricAuthor,
            "Composer": self.Composer,
            "Arranger": self.Arranger,
            "Length": self.Length,
            "Recorder": self.Recorder,
            "Editor": self.Editor,
            "Version": self.Version,
            "Offset": self.Offset,
        }
        for k in result.keys():
            result[k] = now_d[result[k]]
        result.update(self.Other)
        return result
