import threading
import time

from LyricLib import LRC_ID_TAG2META_NAME, Lyric, SingleLineLyric, TimeStamp

lyric = Lyric()

for t in LRC_ID_TAG2META_NAME.values():
    lyric.meta_info.set_meta(t, input(t + "："))

music_file = input("请输入音乐文件：")
print("请逐行输入歌词，以 *XE 表示结束")

lines = []
while (line := input()) != "*XE":
    if line:
        lines.append(line)

from winsound import SND_FILENAME, PlaySound

input("按下回车后，你将听到你需要生成歌词的音频。以及一行歌词，按下回车表示这句歌词已结束。")

threading.Thread(target=PlaySound, args=(music_file, SND_FILENAME)).start()

start_time = time.time()


# 这样的写法是有问题的
for line in lines:
    input(line)
    t = TimeStamp(seconds=time.time() - start_time)
    lyric.lyrics[t] = SingleLineLyric(line)
    print(t)

with open(
    lyric.meta_info.Title if lyric.meta_info.Title else input("保存文件名："),
    "w",
    encoding="utf-8",
) as f:
    lyric.to_lrc(f)

input("文件已保存。按下回车退出。")
