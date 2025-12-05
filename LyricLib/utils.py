# -*- coding: utf-8 -*-

"""
工具函数
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

from typing import Union, Tuple
from PIL import ImageColor

from .exceptions import ColourFormatError, ColourTypeError


def _normalize_color(colour: Union[str, Tuple[int, ...]]) -> Tuple[int, int, int, int]:
    """将颜色统一为 RGBA 元组 (0-255)"""

    if isinstance(colour, str):

        colour = ImageColor.getrgb(colour)

    if isinstance(colour, tuple):
        if len(colour) == 3:

            return (*colour, 255)

        elif len(colour) == 4:

            return colour

        else:

            raise ColourFormatError(colour)

    raise ColourTypeError(colour)
