
import time

from Lyric import Lyric, LRC_ID_TAG2META_NAME, TimeStamp, SingleLineLyric
import threading

lyric = Lyric()

for t in LRC_ID_TAG2META_NAME.values():
    lyric.meta_info.set_meta(t,input(t))

music_file = input("请输入音乐文件：")
print("请逐行输入歌词，以 *XE 表示结束")

lines = []
while line:= input() != "*XE":
    if line:
        lines.append(line)

from winsound import PlaySound, SND_FILENAME

input("按下回车后，你将听到你需要生成歌词的音频。以及一行歌词，按下回车表示这句歌词已结束。")

threading.Thread(target=PlaySound,args=(music_file,SND_FILENAME)).start()

start_time = time.time()

for line in lines:
    input(line)
    t = TimeStamp(seconds=time.time()-start_time)
    lyric.lyrics[t] = SingleLineLyric(line)
    print(t)

with open(lyric.meta_info.Title if lyric.meta_info.Title else input("保存文件名："),'w',encoding='utf-8') as f:
    lyric.to_lrc(f)

input("文件已保存。按下回车退出。")