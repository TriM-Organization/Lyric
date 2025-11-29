# -*- coding: utf-8 -*-

"""
报错类型
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



class InvalidFileError(LyricBaseException):
    """文件损坏"""

    def __init__(self, *args):
        """文件损坏"""
        super().__init__("文件损坏", *args)

class TimeTooPreciseError(LyricBaseException):
    """时间过于精确"""

    def __init__(self, *args):
        """时间过于精确"""
        super().__init__("时间过于精确", *args)

class ParseError(LyricBaseException):
    """解析错误"""

    def __init__(self, *args):
        """解析错误"""
        super().__init__("解析错误", *args)