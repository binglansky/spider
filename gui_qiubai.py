#-*- coding: UTF-8 -*-
# author : Corleone
from Tkinter import *
import urllib2,re

def load(page):
        url="http://www.qiushibaike.com/text/page/"+str(page)+"/?s=4937798"
        user_agent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.113 Safari/537.36"
        headers={'User-Agent':user_agent}
        res=urllib2.Request(url,headers = headers)
        html = urllib2.urlopen(res).read()
        reg=re.compile(r'<div.*?class="content">(.*?)</div>',re.S)
        duanzi=reg.findall(html)
        return duanzi
i=0
page=1
def get():
    if i==0:
        txtlist=load(page)
        page+=1
    if i<20:
        txt.delete(1.0,END)
        txt.insert(1.0,txtlist[i].replace("<span>","").replace("</span>","").replace("</br>","").replace("\n","").replace("<br/>",""))
        i+=1
        global i
        global page
        global txtlist
    else:
        i=0

def main():
    root=Tk()   # 定义一个窗口
    root.title("Corleone") # 定义窗口标题
    root.geometry('500x500')  # 定义窗口大小
    b=Button(root,text="next",width=25,bg="red",command=get)  # 定义一个按钮
    b.pack(side=BOTTOM)  # 按钮的布局 放在窗口最下面
    global txt
    txt=Text(root,font=(u"黑体",20)) # 定义一个编辑界面
    txt.pack(expand=YES,fill=BOTH)  # 编辑界面布局 随窗口大小自动改变
    root.mainloop()   # 让窗口一直在屏幕上显示出来 


main()
