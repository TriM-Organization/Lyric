# -*- coding: utf-8 -*-

"""
针对 LRC 歌词文件类型的报错类型
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


from ..exceptions import InvalidFileError, ParseError


class LrcDestroyedError(InvalidFileError):
    """Lrc文件损坏"""

    def __init__(self, *args):
        """Lrc文件损坏"""
        super().__init__("LRC 文件", *args)


class WordTagError(ParseError):
    """字词标签错误"""

    def __init__(self, *args):
        """字词标签未一一对应"""
        super().__init__(
            "字词标签错误：字词数量与标签数不符", *args
        )


class TimeTagError(ParseError):
    """时间标签错误"""

    def __init__(self, sth: str = "", *args):
        """未匹配到时间标签"""
        super().__init__("无法在 {} 中匹配时间标签。".format(sth), *args)
