# -*- coding: UTF-8 -*-
import json
import requests
from Tkinter import *
import threading

def download(v,en):
    select = v.get()
    url = en.get(0.0, END).replace("\n", "")
    if 'yinyuetai.com' not in url:
        text.delete(0.0, END)
        text.insert(INSERT, u"必须输入音悦台MV链接！")
        return False
    if '?' in url:
        id = url.split('?')[0][-7:]
    else:
        id = url[-7:]
    url = "http://www.yinyuetai.com/insite/get-video-info?json=true&videoId=" + str(id)
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.113 Safari/537.36"
    headers = {'User-Agent':user_agent}
    html = requests.get(url,headers=headers).text
    video = json.loads(html)
    try:
        tmp_url = video['videoInfo']['coreVideoInfo']['videoUrlModels'][select]['videoUrl']
    except IndexError:
        text.delete(0.0, END)
        text.insert(INSERT, u"该视频没有你想要的分辨率，请换差一些的。")
        return False
    mvurl = tmp_url.split('?')[0]
    mvname = video['videoInfo']['coreVideoInfo']['videoName']
    author = video['videoInfo']['coreVideoInfo']['artistName']
    start_down = u"开始下载 " + mvname + '--'+ author +'.mp4 \n'
    text.delete(0.0, END)
    text.insert(INSERT, start_down)
    r = requests.get(mvurl)
    with open(mvname+'--'+author+'.mp4',"wb") as data:
        data.write(r.content)
    success_down = u"\n下载完成 :) "
    text.insert(INSERT, success_down)
def run():
    t = threading.Thread(target=download,args=(v,en))
    t.setDaemon(True)
    t.start()

def start():
    root = Tk()
    root.geometry("500x450")
    root.title("yinyuetai mv download by: Corleone")
    global v
    v = IntVar()
    v.set(1)
    frame = Frame(root).pack(side=TOP)
    global en
    en = Text(frame)
    en.config(width="100", height="2", font=(u"黑体", 15)) # 输入URL
    en.pack()
    # 单选按钮
    Radiobutton(root, variable=v, text='320p', value="0").pack()
    Radiobutton(root, variable=v, text='480p', value="1").pack()
    Radiobutton(root, variable=v, text='720p', value="2").pack()
    Radiobutton(root, variable=v, text='1080p', value="3").pack()
    Button(root, text=u"下载", width="8", bd=5, font=(u"黑体", 15),command=run).pack()   # 下载按钮
    global text
    text = Text(root)
    text.config(width=100, height=10 ,font=(u"黑体", 15))
    text.pack()
    root.mainloop()


start()
