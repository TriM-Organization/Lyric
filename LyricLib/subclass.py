# -*- coding: utf-8 -*-

"""
词幕库下属子类
"""

"""
版权所有 © 2022-2025 金羿ELS
Copyright © 2022-2025 Eilles

开源相关声明请见 仓库根目录下的 License.md
Terms & Conditions: License.md in the root directory
"""

# 睿乐组织 开发交流群 861684859
# Email TriM-Organization@hotmail.com
# 若需转载或借鉴 许可声明请查看仓库目录下的 License.md


from enum import Enum
from dataclasses import dataclass
from typing import (
    Dict,
    List,
    Tuple,
    Union,
    Optional,
    Literal,
    Callable,
    Any,
    Pattern,
    Sequence,
    Iterable,
    Mapping,
)

import re
from PIL import ImageColor, Image, ImageFont
from datetime import time, timedelta

from .types import CopyableSequence
from .utils import _normalize_color
from .exceptions import TimeTooPreciseError, LineSentenceFormatError
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
            return TimeStamp(
                hour=self.hours + other.hours,
                min=self.minutes + other.minutes,
                sec=self.seconds + other.seconds,
                ms=self.milliseconds + other.milliseconds,
            )
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

    def __dict__(self) -> Dict[str, Literal[-1, 0, 1]]:
        return {"x-anchor": self.value[0], "y-anchor": self.value[1]}

    def __tuple__(self) -> Tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]]:
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

    def __init__(
        self, archer: Union[LocationAnchor, Tuple[int, int]], offset: Tuple[int, int]
    ):
        """创建一个歌词行位置

        Parameters
        ----------
        archer: LocationAnchor
            定位点位置
        offset: Tuple[int, int]
            偏移量，屏幕百分比
        """
        self.archer = (
            archer if isinstance(archer, LocationAnchor) else LocationAnchor(archer)
        )
        self.offset = offset

    def __dict__(self) -> Dict[str, Union[LocationAnchor, Tuple[int, int]]]:
        return {"archer": self.archer, "offset": self.offset}

    def __tuple__(self) -> Tuple[LocationAnchor, Tuple[int, int]]:
        return self.archer, self.offset

    # 打包支持 Pickle
    def _getstate(self):
        return self.__tuple__()

    def __reduce__(self):
        return (self.__class__, self._getstate())


class StyledString(str):
    """带样式的文本内容"""

    font: Optional[str]
    """字体名称"""
    size: Optional[int]
    """字体大小"""

    _bold: bool
    """是否加粗"""
    _italic: bool
    """是否斜体"""
    _underline: bool
    """是否下划线"""
    _strikethrough: bool
    """是否删除线"""
    _colour: Tuple[int, int, int, int]
    """字体颜色"""

    _outline: Tuple[int, Tuple[int, int, int, int]]
    """描边样式（宽度、颜色）"""

    _background_cover: Tuple[int, int, int, int]
    """背景填充颜色"""

    def __new__(
        cls,
        line_text: str = "",
        is_bold: bool = False,
        is_italic: bool = False,
        is_underline: bool = False,
        is_strikethrough: bool = False,
        text_colour: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = (
            255,
            255,
            255,
            255,
        ),
        outline_px: int = 0,
        outline_colour: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = (
            0,
            0,
            0,
            0,
        ),
        background_cover_colour: Union[
            str, Tuple[int, int, int], Tuple[int, int, int, int]
        ] = (0, 0, 0, 0),
        font_name: Optional[str] = None,
        font_size: Optional[int] = None,
    ):
        """创建一个样式化字符串

        Parameters
        ----------
        line_text: str
            歌词行内容
        is_bold: bool
            是否加粗
        is_italic: bool
            是否斜体
        is_underline: bool
            是否下划线
        is_strikethrough: bool
            是否删除线
        text_colour: str | Tuple[int, int, int] | Tuple[int, int, int, int]
            文字颜色（可含透明度，RGBA顺序）
        outline_px: int
            描边宽度
        outline_colour: str | Tuple[int, int, int] | Tuple[int, int, int, int]
            描边颜色（可含透明度，RGBA顺序）
        background_cover_colour: str | Tuple[int, int, int] | Tuple[int, int, int, int]
            背景填充颜色（可含透明度，RGBA顺序）
        font_name: str
            字体名称
        font_size: int
            字体大小
        """
        instance = super().__new__(cls, line_text)

        instance.font = font_name
        instance.size = font_size

        instance._bold = is_bold
        instance._italic = is_italic
        instance._underline = is_underline
        instance._strikethrough = is_strikethrough

        instance._colour = _normalize_color(text_colour)

        instance._outline = (outline_px, _normalize_color(outline_colour))

        instance._background_cover = _normalize_color(background_cover_colour)

        return instance

    # 附加属性

    @property
    def is_bold(self) -> bool:
        """是否加粗"""
        return self._bold

    def bold(self, enable: bool = True) -> "StyledString":
        """加粗"""
        return StyledString(
            str(self),
            is_bold=enable,
            is_italic=self.is_italic,
            is_underline=self.is_underline,
            is_strikethrough=self.is_strikethrough,
            text_colour=self._colour,
            outline_px=self._outline[0],
            outline_colour=self._outline[1],
            background_cover_colour=self._background_cover,
            font_name=self.font,
            font_size=self.size,
        )

    @property
    def is_italic(self) -> bool:
        """是否斜体"""
        return self._italic

    def italic(self, enable: bool = True) -> "StyledString":
        """斜体"""
        return StyledString(
            str(self),
            is_bold=self.is_bold,
            is_italic=enable,
            is_underline=self.is_underline,
            is_strikethrough=self.is_strikethrough,
            text_colour=self._colour,
            outline_px=self._outline[0],
            outline_colour=self._outline[1],
            background_cover_colour=self._background_cover,
            font_name=self.font,
            font_size=self.size,
        )

    @property
    def is_underline(self) -> bool:
        """是否下划线"""
        return self._underline

    def underline(self, enable: bool = True) -> "StyledString":
        """下划线"""
        return StyledString(
            str(self),
            is_bold=self.is_bold,
            is_italic=self.is_italic,
            is_underline=enable,
            is_strikethrough=self.is_strikethrough,
            text_colour=self._colour,
            outline_px=self._outline[0],
            outline_colour=self._outline[1],
            background_cover_colour=self._background_cover,
            font_name=self.font,
            font_size=self.size,
        )

    @property
    def is_strikethrough(self) -> bool:
        """是否删除线"""
        return self._strikethrough

    def strikethrough(self, enable: bool = True) -> "StyledString":
        """删除线"""
        return StyledString(
            str(self),
            is_bold=self.is_bold,
            is_italic=self.is_italic,
            is_underline=self.is_underline,
            is_strikethrough=enable,
            text_colour=self._colour,
            outline_px=self._outline[0],
            outline_colour=self._outline[1],
            background_cover_colour=self._background_cover,
            font_name=self.font,
            font_size=self.size,
        )

    @property
    def text_colour(self) -> Tuple[int, int, int, int]:
        """文字颜色"""
        return self._colour

    def coloured(
        self, new_colour: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]
    ):
        """上色"""
        return StyledString(
            str(self),
            is_bold=self.is_bold,
            is_italic=self.is_italic,
            is_underline=self.is_underline,
            is_strikethrough=self.is_strikethrough,
            text_colour=new_colour,
            outline_px=self._outline[0],
            outline_colour=self._outline[1],
            background_cover_colour=self._background_cover,
            font_name=self.font,
            font_size=self.size,
        )

    @property
    def outline_size(self) -> int:
        """描边宽度"""
        return self._outline[0]

    @property
    def outline_colour(self) -> Tuple[int, int, int, int]:
        """描边颜色"""
        return self._outline[1]

    def outline(
        self,
        width: Optional[int] = None,
        colour: Optional[
            Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]
        ] = None,
    ) -> "StyledString":
        """描边"""
        return StyledString(
            str(self),
            is_bold=self.is_bold,
            is_italic=self.is_italic,
            is_underline=self.is_underline,
            is_strikethrough=self.is_strikethrough,
            text_colour=self._colour,
            outline_px=self._outline[0] if width is None else width,
            outline_colour=(
                self._outline[1] if colour is None else _normalize_color(colour)
            ),
            background_cover_colour=self._background_cover,
            font_name=self.font,
            font_size=self.size,
        )

    @property
    def background_cover_colour(self) -> Tuple[int, int, int, int]:
        """背景填充颜色"""
        return self._background_cover

    def cover(
        self, colour: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]
    ):
        """背景填充"""
        return StyledString(
            str(self),
            is_bold=self.is_bold,
            is_italic=self.is_italic,
            is_underline=self.is_underline,
            is_strikethrough=self.is_strikethrough,
            text_colour=self._colour,
            outline_px=self._outline[0],
            outline_colour=self._outline[1],
            background_cover_colour=_normalize_color(colour),
            font_name=self.font,
            font_size=self.size,
        )

    def refont(self, name: str):
        """重新设置字体"""
        return StyledString(
            str(self),
            is_bold=self.is_bold,
            is_italic=self.is_italic,
            is_underline=self.is_underline,
            is_strikethrough=self.is_strikethrough,
            text_colour=self._colour,
            outline_px=self._outline[0],
            outline_colour=self._outline[1],
            background_cover_colour=self._background_cover,
            font_name=name,
            font_size=self.size,
        )

    def resize(self, value: int):
        """重新设置文字大小"""
        return StyledString(
            str(self),
            is_bold=self.is_bold,
            is_italic=self.is_italic,
            is_underline=self.is_underline,
            is_strikethrough=self.is_strikethrough,
            text_colour=self._colour,
            outline_px=self._outline[0],
            outline_colour=self._outline[1],
            background_cover_colour=self._background_cover,
            font_name=self.font,
            font_size=value,
        )

    def with_styles(self, **kwargs):
        """批量更新样式，返回新实例"""
        # 当前所有参数的默认值
        defaults = {
            "is_bold": self._bold,
            "is_italic": self._italic,
            "is_underline": self._underline,
            "is_strikethrough": self._strikethrough,
            "text_colour": self._colour,
            "outline_px": self._outline[0],
            "outline_colour": self._outline[1],
            "background_cover_colour": self._background_cover,
            "font_name": self.font,
            "font_size": self.size,
        }
        defaults.update(kwargs)
        return StyledString(str(self), **defaults)

    def _with_same_style(self, new_text: str) -> "StyledString":
        """使用当前样式创建一个新的 StyledString 实例

        Parameters
        ----------
        new_text: str
            新的字符串内容

        Returns
        -------
        StyledString
            应用了当前实例样式的新的 StyledString 实例
        """
        return StyledString(
            new_text,
            is_bold=self._bold,
            is_italic=self._italic,
            is_underline=self.is_underline,
            is_strikethrough=self.is_strikethrough,
            text_colour=self._colour,
            outline_px=self._outline[0],
            outline_colour=self._outline[1],
            background_cover_colour=self._background_cover,
            font_name=self.font,
            font_size=self.size,
        )

    # 相等、哈希、比较
    def __eq__(self, other):

        if not isinstance(other, StyledString):

            return NotImplemented

        return (
            str(self) == str(other)
            and self.font == other.font
            and self.size == other.size
            and self._bold == other._bold
            and self._italic == other._italic
            and self._underline == other._underline
            and self._strikethrough == other._strikethrough
            and self._colour == other._colour
            and self._outline == other._outline
            and self._background_cover == other._background_cover
        )

    def __hash__(self):

        return hash(
            (
                str(self),
                self.font,
                self.size,
                self._bold,
                self._italic,
                self._underline,
                self._strikethrough,
                self._colour,
                self._outline,
                self._background_cover,
            )
        )

    # 外读

    def __repr__(self):
        """
        输出格式：
        StyledString(
            text,
            styles=(bold, italic, underline, strikethrough),
            colour=(R, G, B, A),
            outline=(px, (R, G, B, A)),
            background_cover=(R, G, B, A),
            font=name,
            font_size=size,
        )
        """

        styles = []

        if self._bold:
            styles.append("bold")

        if self._italic:
            styles.append("italic")

        if self._underline:
            styles.append("underline")

        if self._strikethrough:
            styles.append("strikethrough")

        style_str = ", styles=({})".format(", ".join(styles)) if styles else ""

        if (self._colour[-1] != 0) and (self._colour != (255, 255, 255, 255)):
            style_str += ", colour={}".format(self._colour)

        if (self._outline[0] != 0) and (self._outline[1][-1] != 0):
            style_str += ", outline={}".format(self._outline)

        if (self._background_cover[-1] != 0) and (
            self._background_cover != (0, 0, 0, 0)
        ):
            style_str += ", background_cover={}".format(self._background_cover)

        if self.font:
            style_str += ", font={!r}".format(self.font)

        if self.size:
            style_str += ", size={}".format(self.size)

        return "StyledString({}{})".format(super().__repr__(), style_str)

    def __str__(self) -> str:
        """返回纯纯的字符串"""
        return super().__str__()

    def __iter__(self):
        """迭代串内元素

        Yields
        ------
        StyledString
            每个字符作为一个保留原始样式的 StyledString 实例
        """
        for char in str(self):
            yield self._with_same_style(char)

    def join(self, iterable: Iterable[Union[str, "StyledString"]]) -> "StyledString":
        """使用当前字符串作为分隔符，连接可迭代对象中的元素

        Parameters
        ----------
        iterable: Iterable[str | StyledString]
            要连接的字符串序列

        Returns
        -------
        StyledString
            连接后的新字符串，保留当前实例（分隔符）的样式
        """
        return self._with_same_style(super().join([str(item) for item in iterable]))

    # 索引和切片
    def __getitem__(self, key):
        """支持通过索引或切片获取子字符串，并保留原始样式

        Parameters
        ----------
        key: int | slice
            索引位置或切片对象

        Returns
        -------
        StyledString | str
            若结果为字符串（如切片或单字符），则返回带有原始样式的 StyledString；
            其他情况（如超出范围等）按原生行为处理
        """
        result = super().__getitem__(key)
        if isinstance(result, str):
            return self._with_same_style(result)
        return result

    # 操作

    def split(
        self, sep: Optional[str] = None, maxsplit: int = -1
    ) -> List["StyledString"]:
        """拆分字符串，返回一个列表，包含根据指定分隔符分割后的子字符串

        Parameters
        ----------
        sep: str, optional
            分隔符，默认为空格
        maxsplit: int, optional
            最大拆分数，默认为-1，表示不限制

        Returns
        -------
        List[StyledString]
            包含拆分后子字符串的新列表，每个元素保留原始样式
        """
        return [self._with_same_style(part) for part in super().split(sep, maxsplit)]

    def rsplit(
        self, sep: Optional[str] = None, maxsplit: int = -1
    ) -> List["StyledString"]:
        """从右边开始拆分字符串，返回一个列表，包含根据指定分隔符分割后的子字符串

        Parameters
        ----------
        sep: str, optional
            分隔符，默认为空格
        maxsplit: int, optional
            最大拆分数，默认为-1，表示不限制

        Returns
        -------
        List[StyledString]
            包含从右向左拆分后子字符串的新列表，每个元素保留原始样式
        """
        return [self._with_same_style(part) for part in super().rsplit(sep, maxsplit)]

    def strip(self, chars: Optional[str] = None) -> "StyledString":
        """移除字符串首尾指定字符或空白，默认移除空白

        Parameters
        ----------
        chars: str, optional
            要移除的字符集合，默认为空白

        Returns
        -------
        StyledString
            移除了指定字符的新字符串，保留原始样式
        """
        return self._with_same_style(super().strip(chars))

    def lstrip(self, chars: Optional[str] = None) -> "StyledString":
        """移除字符串左侧指定字符或空白，默认移除空白

        Parameters
        ----------
        chars: str, optional
            要从左侧移除的字符集合，默认为空白字符

        Returns
        -------
        StyledString
            移除了左侧指定字符的新字符串，保留原始样式
        """
        return self._with_same_style(super().lstrip(chars))

    def rstrip(self, chars: Optional[str] = None) -> "StyledString":
        """移除字符串右侧指定字符或空白，默认移除空白

        Parameters
        ----------
        chars: str, optional
            要从右侧移除的字符集合，默认为空白字符

        Returns
        -------
        StyledString
            移除了右侧指定字符的新字符串，保留原始样式
        """
        return self._with_same_style(super().rstrip(chars))

    def upper(self) -> "StyledString":
        """转换字符串中所有的小写字母为大写

        Returns
        -------
        StyledString
            转换为大写的新字符串，保留原始样式
        """
        return self._with_same_style(super().upper())

    def lower(self) -> "StyledString":
        """转换字符串中的所有大写字母为小写

        Returns
        -------
        StyledString
            转换为小写的新字符串，保留原始样式
        """
        return self._with_same_style(super().lower())

    def replace(self, old: str, new: str, count: int = -1) -> "StyledString":
        """将字符串中的旧子串替换为新子串

        Parameters
        ----------
        old: str
            要被替换的子串
        new: str
            用于替换的新子串
        count: int, optional
            替换的最大次数，默认为-1，表示全部替换

        Returns
        -------
        StyledString
            执行替换后的新字符串，保留原始样式
        """
        return self._with_same_style(super().replace(old, new, count))

    def title(self) -> "StyledString":
        """将字符串中每个单词的首字母大写，其余字母小写

        Returns
        -------
        StyledString
            转换为首字母大写格式的新字符串，保留原始样式
        """
        return self._with_same_style(super().title())

    def capitalize(self) -> "StyledString":
        """将字符串的首字母大写，其余字母转为小写

        Returns
        -------
        StyledString
            首字母大写、其余小写的新字符串，保留原始样式
        """
        return self._with_same_style(super().capitalize())

    def swapcase(self) -> "StyledString":
        """将字符串中的大写字母转为小写，小写字母转为大写

        Returns
        -------
        StyledString
            大小写互换后的新字符串，保留原始样式
        """
        return self._with_same_style(super().swapcase())

    def center(self, width: int, fillchar: str = " ") -> "StyledString":
        """返回一个指定宽度的居中对齐字符串，两侧用指定字符填充

        Parameters
        ----------
        width: int
            目标字符串总宽度
        fillchar: str, optional
            填充字符，默认为空格

        Returns
        -------
        StyledString
            居中对齐并填充后的新字符串，保留原始样式
        """
        return self._with_same_style(super().center(width, fillchar))

    def ljust(self, width: int, fillchar: str = " ") -> "StyledString":
        """返回一个左对齐的字符串，右侧用指定字符填充至指定宽度

        Parameters
        ----------
        width: int
            目标字符串总宽度
        fillchar: str, optional
            填充字符，默认为空格

        Returns
        -------
        StyledString
            左对齐并填充后的新字符串，保留原始样式
        """
        return self._with_same_style(super().ljust(width, fillchar))

    def rjust(self, width: int, fillchar: str = " ") -> "StyledString":
        """返回一个右对齐的字符串，左侧用指定字符填充至指定宽度

        Parameters
        ----------
        width: int
            目标字符串总宽度
        fillchar: str, optional
            填充字符，默认为空格

        Returns
        -------
        StyledString
            右对齐并填充后的新字符串，保留原始样式
        """
        return self._with_same_style(super().rjust(width, fillchar))

    def zfill(self, width: int) -> "StyledString":
        """在字符串左侧用 '0' 填充至指定宽度，适用于数字字符串的补零操作

        Parameters
        ----------
        width: int
            目标字符串总宽度

        Returns
        -------
        StyledString
            左侧补零后的新字符串，保留原始样式
        """
        return self._with_same_style(super().zfill(width))

    def partition(
        self, sep: str
    ) -> Tuple["StyledString", "StyledString", "StyledString"]:
        """根据指定分隔符将字符串分割为三部分：(前缀, 分隔符, 后缀)

        Parameters
        ----------
        sep: str
            用作分割的分隔符

        Returns
        -------
        Tuple[StyledString, StyledString, StyledString]
            一个包含三个元素的元组：
            - 第一部分：分隔符前的子串
            - 第二部分：分隔符本身（若未找到则为空字符串）
            - 第三部分：分隔符后的子串
            所有部分均保留原始样式
        """
        a, b, c = super().partition(sep)
        return (
            self._with_same_style(a),
            self._with_same_style(b),
            self._with_same_style(c),
        )

    def rpartition(
        self, sep: str
    ) -> Tuple["StyledString", "StyledString", "StyledString"]:
        """从右侧开始，根据指定分隔符将字符串分割为三部分：(前缀, 分隔符, 后缀)

        Parameters
        ----------
        sep: str
            用作分割的分隔符

        Returns
        -------
        Tuple[StyledString, StyledString, StyledString]
            一个包含三个元素的元组：
            - 第一部分：最后一个分隔符前的子串
            - 第二部分：分隔符本身（若未找到则为空字符串）
            - 第三部分：最后一个分隔符后的子串
            所有部分均保留原始样式
        """
        a, b, c = super().rpartition(sep)
        return (
            self._with_same_style(a),
            self._with_same_style(b),
            self._with_same_style(c),
        )

    # 格式化支持

    def __mod__(self, args):
        """支持 % 格式化，使用 {} 或 {name} 的格式来标识替换位置。

        Parameters
        ----------
        args: tuple
            位置参数

        Raises
        ------
        ValueError
            如果格式化字符串中包含无效的格式字符
        TypeError
            如果格式化字符串中包含无效的格式字符

        Returns
        -------
        StyledString
            格式化后的新字符串，保留原始样式
        """
        result = super().__mod__(args)
        if isinstance(result, str):
            return self._with_same_style(result)
        return result

    def format(self, *args, **kwargs) -> "StyledString":
        """返回一个格式化的字符串，在原串中用 {} 或 {name} 的格式来标识替换位置。

        Parameters
        ----------
        args: tuple
            位置参数
        kwargs: dict
            关键字参数

        Raises
        ------
        ValueError
            如果格式化字符串中包含无效的格式字符
        TypeError
            如果格式化字符串中包含无效的格式字符

        Returns
        -------
        StyledString
            格式化后的新字符串，保留原始样式
        """
        return self._with_same_style(super().format(*args, **kwargs))

    def format_map(self, mapping) -> "StyledString":
        """使用键值对填充格式字符串。

        Parameters
        ----------
        mapping: dict
            键值对映射表

        Raises
        ------
        KeyError
            如果格式字符串中包含无效的格式字符

        Returns
        -------
        StyledString
            格式化后的新字符串，保留原始样式
        """
        return self._with_same_style(super().format_map(mapping))

    # 运算符

    def __add__(self, other: Union[str, "StyledString"]) -> "StyledString":
        """连接当前字符串与另一个字符串

        Parameters
        ----------
        other: str | StyledString
            要连接的字符串

        Returns
        -------
        StyledString
            连接后的新字符串，保留当前实例的样式
        """
        if isinstance(other, StyledString):
            # 若 other 也是 StyledString，仍以 self 的样式为准
            return self._with_same_style(str(self) + str(other))
        elif isinstance(other, str):
            return self._with_same_style(str(self) + other)
        return NotImplemented

    def __radd__(self, other: str) -> "StyledString":
        """反向连接（当 StyledString 在右侧时）

        Parameters
        ----------
        other: str
            左侧的普通字符串

        Returns
        -------
        StyledString
            连接后的新字符串，保留当前实例的样式
        """
        if isinstance(other, StyledString):
            # 若 other 也是 StyledString，仍以 self 的样式为准
            return self._with_same_style(str(self) + str(other))
        elif isinstance(other, str):
            return self._with_same_style(other + str(self))
        return NotImplemented

    def __mul__(self, n: int) -> "StyledString":
        """重复当前字符串 n 次

        Parameters
        ----------
        n: int
            重复次数

        Returns
        -------
        StyledString
            重复后的新字符串，保留原始样式
        """
        if isinstance(n, int):
            return self._with_same_style(str(self) * n)
        return NotImplemented

    def __rmul__(self, n: int) -> "StyledString":
        """反向重复（支持 3 * s）

        Parameters
        ----------
        n: int
            重复次数

        Returns
        -------
        StyledString
            重复后的新字符串，保留原始样式
        """
        return self.__mul__(n)

    def __contains__(self, item: Union[str, "StyledString"]) -> bool:
        """检查子字符串是否存在于当前字符串中

        Parameters
        ----------
        item: str | StyledString
            要检查的子字符串

        Returns
        -------
        bool
            如果存在则返回 True，否则 False
        """
        return str(item) in str(self)

    def __bool__(self) -> bool:
        """当字符串非空时为 True"""
        return len(self) > 0

    # 兼容正则匹配

    def sub(
        self,
        pattern: Union[str, Pattern],
        repl: Union[str, Callable],
        count: int = 0,
    ) -> "StyledString":
        """使用正则表达式替换匹配项，返回新 StyledString（保留原始样式）

        Parameters
        ----------
        pattern: str | re.Pattern
            正则表达式模式
        repl: str | Callable
            替换字符串或替换函数
        count: int, optional
            最大替换次数，默认为 0（全部替换）

        Returns
        -------
        StyledString
            执行正则替换后的新字符串，保留原始样式
        """
        new_text = re.sub(pattern, repl, str(self), count=count)
        return self._with_same_style(new_text)

    def split_re(
        self, pattern: Union[str, Pattern], maxsplit: int = 0
    ) -> List["StyledString"]:
        """使用正则表达式分割字符串

        Parameters
        ----------
        pattern: str | re.Pattern
            正则表达式分隔符
        maxsplit: int, optional
            最大分割次数，默认为 0（不限制）

        Returns
        -------
        List[StyledString]
            分割后的子字符串列表，每个元素保留原始样式
        """
        parts = re.split(pattern, str(self), maxsplit=maxsplit)
        return [self._with_same_style(part) for part in parts]

    def findall(self, pattern: Union[str, Pattern]) -> List["StyledString"]:
        """查找所有与正则表达式匹配的子串

        Parameters
        ----------
        pattern: str | re.Pattern
            正则表达式模式

        Returns
        -------
        List[StyledString]
            所有匹配的子字符串列表，每个元素保留原始样式
        """
        matches = re.findall(pattern, str(self))
        # 注意：findall 返回的是 str 列表（除非有分组）
        if not matches:
            return []
        # 如果是元组（因分组），我们只取完整匹配（但 re.findall 不直接给完整匹配）
        # 所以建议用户用 finditer 或确保无捕获组
        return [
            (
                self._with_same_style(m)
                if isinstance(m, str)
                else self._with_same_style(str(m))
            )
            for m in matches
        ]

    def search(self, pattern: Union[str, Pattern]) -> Optional[re.Match]:
        """在字符串中搜索第一个匹配项（返回 re.Match，不带样式）

        Parameters
        ----------
        pattern: str | re.Pattern
            正则表达式模式

        Returns
        -------
        re.Match | None
            匹配对象或 None
        """
        return re.search(pattern, str(self))

    def match(self, pattern: Union[str, Pattern]) -> Optional[re.Match]:
        """从字符串开头匹配正则表达式

        Parameters
        ----------
        pattern: str | re.Pattern
            正则表达式模式

        Returns
        -------
        re.Match | None
            匹配对象或 None
        """
        return re.match(pattern, str(self))


@dataclass(init=False)
class SubtitleBlock:
    """一块词，包括类似中西对照的多行字幕"""

    location: LineLocation
    context: List[List[StyledString]]
    """```
    [
        ["A quick ", "**fox**"],
        ["一只矫健的", "**狐狸**"],
    ]
    ```"""
    duration: Optional[TimeStamp]
    word_extension: Optional[List[Dict[TimeStamp, List[StyledString]]]]
    """语速可能不一样，因此用列表在外，字典在内。
    ```
    [
        {
            TimeStamp(0): ["A quick ", "**fox**"],
            TimeStamp(1): [" jumps"],
            TimeStamp(2): [" over"],
            TimeStamp(3): [" the lazy dog."],
        },
        {
            TimeStamp(0): ["一只矫健的", ],
            TimeStamp(1): ["**狐狸**", "跳过了"],
            TimeStamp(3): ["那懒惰的狗。"],
        },
    ]
    ```
    """

    def __init__(
        self,
        sentence: Union[
            StyledString, Sequence[StyledString], Sequence[Sequence[StyledString]]
        ],
        duration: Optional[TimeStamp] = None,
        extension: Optional[
            Sequence[Mapping[TimeStamp, Sequence[StyledString]]]
        ] = None,
    ):
        """
        建立一条词句

        Parameters
        ----------
        sentence: StyledString | Sequence[StyledString] | Sequence[Sequence[StyledString]]
            词句
            - 当是字符串时，将自动以换行拆分并创建 StyledString 对象
            - 当是单层序列时，认为表示分为当前词句的多行
            - 当是双层序列时，第一层用以分行，第二行用以分词区别样式
        duration: TimeStamp, optional
            词句的持续时间
        extension: Sequence[Mapping[TimeStamp, Sequence[StyledString]]], optional
            词句的扩展

        Raises
        ------
        LineSentenceFormatError
            如果 sentence 的格式不正确，将抛出内部错误
        """

        if isinstance(sentence, str):
            if "\n" in sentence:
                self.context = [StyledString(sentence).split("\n")]
            self.context = [[StyledString(sentence)]]
        elif isinstance(sentence, Sequence):
            if all(isinstance(item, StyledString) for item in sentence):
                self.context = [[item] for item in sentence]  # type: ignore
            elif all(isinstance(item, Sequence) for item in sentence):
                self.context = [list(item) for item in sentence]  # type: ignore
        else:
            raise LineSentenceFormatError("类型：", type(sentence), "内容：", sentence)

        self.duration = duration
        self.word_extension = (
            extension
            if extension is None
            else [{k: list(v) for k, v in line.items()} for line in extension]
        )

    def __str__(self) -> str:
        return "\n".join("".join(row) for row in self.context)

    @classmethod
    def from_lrc_str_dict(
        cls,
        sentence: str,
        **extension: Sequence[str],
    ):
        """从LRC时间标签字符串而组成的字典中获取附加信息"""

        time_str_per_word, words_per_line = zip(*extension.items())

        return cls.from_lrc_str_list(
            sentence, time_str_list=time_str_per_word, splited_sentence=words_per_line
        )

        # (
        #     sentence,
        #     extension=[
        #         {
        #             TimeStamp.from_lrc_timetag(
        #                 time_tag_str=time_str_per_word[i]
        #             ): line_words[i]
        #             for i in range(len(time_str_per_word))
        #         }
        #         for line_words in words_per_line
        #     ],
        # )

    @classmethod
    def from_lrc_str_list(
        cls,
        sentence: str,
        time_str_list: Sequence[str],
        splited_sentence: Sequence[str],
    ):
        """从LRC时间列表和单词列表中读入词句

        Parameters
        ----------
        sentence: str
            词句，会自动以换行拆分，并创建 StyledString 对象存入
        time_str_list: Sequence[str]
            LRC时间标签列表
        splited_sentence: Sequence[str]
            分词列表，表示依照时间标签进行分词的单行词句
        """
        time_list_length = len(time_str_list)
        word_list_length = len(splited_sentence)

        if time_list_length == word_list_length:
            print("数量相同的时间与字词")
            duration_time = None
        elif time_list_length == word_list_length + 1:
            print("时间标签比字词多一个")
            duration_time = TimeStamp.from_lrc_timetag(time_str_list[-1])
        else:
            raise WordTagError(
                word_list_length < time_list_length,
                time_str_list,
                splited_sentence,
            )
        # SubtitleBlock(sentence=StyledString(sentence),duration=)

        return cls(
            sentence=StyledString(sentence),
            duration=duration_time,
            extension=[
                {
                    TimeStamp.from_lrc_timetag(time_tag_str=time_str_list[i]): [
                        StyledString(line[i]),
                    ]
                    for line in splited_sentence
                }
                for i in range(time_list_length)
            ],
        )

    def to_lrc_str(self, format_style: str = STABLE_LRC_TIME_FORMAT_STYLE) -> str:
        """
        以特定样式的LRC格式的时间标签返回整句
        """
        if self.word_extension:
            return "\n".join(
                "".join(
                    "<{}>{}".format(
                        time.to_lrc_timetag(format_style=format_style),
                        "".join(word for word in words),
                    )
                    for time, words in line.items()
                )
                + (
                    "<{}>".format(
                        self.duration.to_lrc_timetag(format_style=format_style)
                        if self.duration
                        else ""
                    )
                )
                for line in self.word_extension
            )
        else:
            return "\n".join("".join(row) for row in self.context)


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
