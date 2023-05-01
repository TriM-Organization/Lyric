# HOUR = "hours"
# """时"""

# MIN = "minutes"
# """分"""

# SEC = "seconds"
# """秒"""

# MS = "microseconds"
# """毫秒"""

LRC_ID_TAG2META_NAME = {
    "ar": "Singer",
    "al": "Album",
    "ti": "Title",
    "au": "LyricAuthor",
    "length": "Length",
    "by": "Recorder",
    "re": "Editor",
    "ve": "Version",
    "offset": "Offset",
}
'''LRC歌词ID标签转元信息名称'''

STABLE_LRC_TIME_FORMAT_STYLE = r"{mm}:{ss}.{xx}"
'''标准LRC时间格式'''

# 正则表达式

# 标签匹配模式
LRC_TAG_PATTERN = r"\[.*?\]"

# 时间戳标签匹配模式
# (hh:)mm:ss(.xxx)
# hh:mm:ss(.xxx)时, hh可为任意整数, mm和ss在0~59之间, xxx在0~999之间或省略;
# mm:ss(.xxx)时, mm可为任意整数, ss在0~59之间, xxx在0~999之间或省略;
# TIME_PATTERN = r"^(\d+:){0,1}([0-5][0-9]:){0,1}([0-5][0-9])(\.[\d]{1,3}){0,1}$"
LRC_TIME_PATTERN = r"^(?P<p1>\d+:){0,1}(?P<p2>[0-5][0-9]:){0,1}(?P<p3>[0-5][0-9])(?P<p4>\.[\d]{1,3}){0,1}$"
"""命名分组"""

LRC_ENHANCE_TIME_PATTERN_C = (
    r"\<(\d+\:){0,1}([0-5][0-9]\:){0,1}([0-5][0-9])(\.[\d]{1,3}){0,1}\>"
)
"""捕获分组"""

LRC_ENHANCE_TIME_PATTERN_N = (
    r"\<(?:\d+\:){0,1}(?:[0-5][0-9]\:){0,1}(?:[0-5][0-9])(?:\.[\d]{1,3}){0,1}\>"
)
"""非捕获分组"""
