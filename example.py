from LyricLib import Lyric, TimeStamp
from rich.console import Console

MainConsole = Console()

l = Lyric().from_lrc(input("LRC地址: "))

MainConsole.print(l)

with open("clone.lrc",'w',encoding="utf-8") as f:
    l.to_lrc(f)

# print("ID:")
# for item in lrc.get_ids:
#     print(item)
# print("-" * 60)

# print("歌词:")
# for item in lrc.get_lyrics:
#     print(item)
#     if item["extends"] is not None:
#         print("  增强型格式：")
#         for key, val in item["extends"].items():
#             print(f"\t{key}: {val}")
# print("-" * 60)

# print("未知:")
# for item in lrc.get_unknowns:
#     print(item)
# print("-" * 60)

# print("解析时间戳:")
# # 解析时间戳
# time_tag_str = input("输入时间戳字符串：")
# h, m, s, ms = TimeStamp.parse_time_tag(time_tag_str)
# print(time_tag_str, "--->", h, m, s, ms)
