

class LyricBaseException(Exception):
    """歌词库的所有错误均继承于此"""

    def __init__(self, *args):
        """歌词库的所有错误均继承于此"""
        super().__init__(*args)

    def aowu(
            self,
    ):
        for i in self.args:
            print(i + "嗷呜！")

    def crash_it(self):
        raise self




class LrcDestroyedError(LyricBaseException):
    """Lrc文件损坏"""

    def __init__(self, *args):
        """Lrc文件损坏"""
        super().__init__("Lrc文件损坏", *args)



class TimeTooPreciseError(LyricBaseException):
    """时间过于精确"""

    def __init__(self, *args):
        """时间过于精确"""
        super().__init__("时间过于精确", *args)


class WordTagError(LyricBaseException):
    """字词标签错误"""

    def __init__(self, words_less_than_tags: bool = True, *args):
        """字词标签未一一对应"""
        super().__init__("字词标签错误：字词{}标签个数".format("小于" if words_less_than_tags else "大于"), *args)

