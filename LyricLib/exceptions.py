# -*- coding: utf-8 -*-

"""
报错类型
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




class LyricBaseException(Exception):
    """词幕库的所有错误均继承于此"""

    def __init__(self, *args):
        """词幕库的所有错误均继承于此"""
        super().__init__("词幕", *args)

    def aowu(
        self,
    ):
        for i in self.args:
            print(i + "嗷呜！")

    def crash_it(self):
        raise self

class InnerlyError(LyricBaseException):
    """内部错误"""

    def __init__(self, *args):
        """内部错误"""
        super().__init__("内部错误", *args)

class OuterlyError(LyricBaseException):
    """外部错误"""

    def __init__(self, *args):
        """外部错误"""
        super().__init__("外部错误", *args)


class InvalidFileError(OuterlyError):
    """文件损坏"""

    def __init__(self, *args):
        """文件损坏"""
        super().__init__("文件损坏", *args)

class TimeTooPreciseError(InnerlyError):
    """时间过于精确"""

    def __init__(self, *args):
        """时间过于精确"""
        super().__init__("时间过于精确", *args)

class ParseError(LyricBaseException):
    """解析错误"""

    def __init__(self, *args):
        """解析错误"""
        super().__init__("解析错误", *args)




class InvalidColourError(ParseError, InnerlyError):
    """颜色无效"""

    def __init__(self, *args):
        """颜色无效"""
        super().__init__("颜色无效", *args)


class ColourFormatError(InvalidColourError, ValueError):
    """颜色格式错误"""

    def __init__(self, *args):
        """颜色格式错误"""
        super().__init__("颜色格式错误", *args)

class ColourTypeError(InvalidColourError, TypeError):
    """颜色参数类型错误"""

    def __init__(self, *args):
        """颜色参数类型错误"""
        super().__init__("颜色参数类型错误", *args)


class LineSentenceFormatError(ParseError, TypeError, InnerlyError):
    """单行词句格式错误"""

    def __init__(self, *args):
        """行句子格式错误"""
        super().__init__("单行词句格式错误", *args)

