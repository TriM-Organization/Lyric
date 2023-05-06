import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Union

from .constants import *
from .exceptions import *


class TagType(Enum):
    """标签类型类"""

    ID = 0  # ID标签
    TIME = 1  # 时间戳标签
    UNKNOWN = 2  # 未知标签


@dataclass(init=False)
class TimeStamp:
    """时间类"""

    hours: int
    minutes: int
    seconds: int
    microseconds: int

    def __init__(
        self,
        hours: Union[float, int] = 0,
        minutes: Union[float, int] = 0,
        seconds: Union[float, int] = 0,
        ms: int = 0,
    ):
        """
        定义一个时间戳

        Parameters
        ----------
        hours, minutes, seconds, ms 正如其名
        分别是距离开始时的 时、分、秒、毫秒
        """

        if ms != int(ms):
            raise TimeTooPreciseError("毫秒不应为小数。")

        microseconds = ms + seconds * 1000 + minutes * 60000 + hours * 360000

        self.microseconds = int(microseconds % 1000)
        self.seconds = int(microseconds / 1000 % 60)
        self.minutes = int(microseconds / 60000 % 60)
        self.hours = int(microseconds / 360000)

    @classmethod
    def from_lrc_time_tag(cls, time_tag_str: str):
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
                *cls.parse_time_tag(time_tag_str.replace("[", "").replace("]", ""))
            )
        except TimeTooPreciseError:
            raise LrcDestroyedError("时间标签出现错误: {}".format(time_tag_str), time_tag_str)

    @staticmethod
    def parse_time_tag(time_tag_str):
        """
        将字符串格式的时间戳解析为 时、分、秒、毫秒

        Parameters
        ----------
        time_tag_str: int
            时间戳字符串

        Returns
        -------

        tuple(int时, int分, int秒, int毫秒)
        """

        m = re.match(LRC_TIME_PATTERN, time_tag_str)
        time_parts = m.groupdict()

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

    @property
    def get_hours(self) -> int:
        """时间戳中的小时部分"""
        return self.hours

    @property
    def in_hours(self) -> int:
        """以小时为单位的时间戳"""
        return (
            self.hours
            + self.minutes / 60
            + self.seconds / 360
            + self.microseconds / 360000
        )

    @property
    def get_minutes(self) -> int:
        """时间戳中的分钟部分"""
        return self.minutes

    @property
    def in_minutes(self) -> int:
        """以分钟为单位的时间戳"""
        return (
            self.hours * 60
            + self.minutes
            + self.seconds / 60
            + self.microseconds / 60000
        )

    @property
    def get_seconds(self) -> int:
        """时间戳中的秒数部分"""
        return self.seconds

    @property
    def in_seconds(self) -> int:
        """以秒为单位的时间戳"""
        return (
            self.hours * 360
            + self.minutes * 60
            + self.seconds
            + self.microseconds / 1000
        )

    @property
    def get_microseconds(self) -> int:
        """时间戳中的毫秒部分"""
        return self.microseconds

    @property
    def in_microseconds(self) -> int:
        """以毫秒为单位的时间戳"""
        return (
            self.hours * 360000
            + self.minutes * 60000
            + self.seconds * 1000
            + self.microseconds
        )

    def __dict__(self) -> Dict[str, int]:
        """由此库定义的歌词时间戳中的所有表示时间的表达式样式所对应的值"""
        return {
            "hh": self.get_hours,
            "mm": self.get_minutes,
            "ss": self.get_seconds,
            "xx": int(self.microseconds / 10),
            "fff": self.microseconds,
        }

    def __hash__(self) -> int:
        return hash(
            "{}{}{}{}".format(
                self.get_hours,
                self.get_minutes,
                self.get_seconds,
                self.get_microseconds,
            )
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__str__() == other.__str__()

    def __str__(self) -> str:
        """
        直接以最完整的格式输出字符串
        """
        return "{}:{}:{}.{}".format(
            self.get_hours, self.get_minutes, self.get_seconds, self.get_microseconds
        )
    
    def __lt__(self, other) -> bool:
        """
        判小于
        """
        return self.in_microseconds < other.in_microseconds

    def __cmp__(self, other) -> int:
        """
        比较
        """
        return self.in_microseconds - other.in_microseconds

    def to_lrc_str(self, format_style: str = STABLE_LRC_TIME_FORMAT_STYLE) -> str:
        """
        以特定样式的LRC格式的时间标签返回字符串
        """
        now_exp = self.__dict__()
        rep_exp = {}
        for expression in now_exp.keys():
            if expression in format_style:
                rep_exp[expression] = "{:0>2d}".format(now_exp[expression])

        return format_style.format(**rep_exp)


@dataclass(init=False)
class SingleLineLyric:
    """一句歌词"""

    whole_context: str
    word_extension: Dict[TimeStamp, str]

    def __init__(self, sentence: str, extension: Dict[TimeStamp, str] = {}):
        """建立一句歌词"""
        self.whole_context = sentence
        self.word_extension = extension

    @classmethod
    def from_lrc_str_dict(cls, sentence: str, **extension):
        """从lrc时间标签字符串而组成的字典中获取附加信息"""
        word_extension = {}
        for time_str, word in extension.items():
            word_extension[TimeStamp.from_lrc_time_tag(time_tag_str=time_str)] = word
        return cls(sentence, word_extension)

    @classmethod
    def from_lrc_str_list(
        cls, sentence: str, time_str_list: List[str], word_list: List[str]
    ):
        """从lrc时间列表和单词列表中获取附加信息"""
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
                TimeStamp.from_lrc_time_tag(time_tag_str=time_str_list[i])
            ] = word_list[i]
            # print("=====")
        return cls(sentence, word_extension)

    def __str__(self) -> str:
        if self.word_extension:
            "".join(
                [
                    r"<{}>{}".format(time.to_lrc_str(), word)
                    for time, word in self.word_extension.items()
                ]
            )
        else:
            return self.whole_context

    def to_lrc_str(self, format_style: str = r"{mm}:{ss}.{xx}") -> str:
        """
        以特定样式的LRC格式的时间标签返回整句
        """
        if self.word_extension:
            return "".join(
                [
                    r"<{}>{}".format(time.to_lrc_str(format_style=format_style), word)
                    for time, word in self.word_extension.items()
                ]
            )
        else:
            return self.whole_context


@dataclass(init=False)
class LyricMetaInfo:
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

    def __dict__(self):
        return {
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

    def set_meta(self, meta_name: str, meta_value: str):
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

    def lrc_id_dict(self):
        """
        返回LRC文件中所需的ID字典
        """
        result = LRC_ID_TAG2META_NAME
        now_d = self.__dict__()
        for k in result.keys():
            result[k] = now_d[result[k]]
        return result
