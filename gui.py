# -*- coding: utf-8 -*-
#GUI功能
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk,Image
import threading,io
import core,clipboard

#全局变量

#当前角色
current_role='sherri'
#主窗口
root = tk.Tk()
root.title("魔裁，启动！！")
roles=list(core.mahoshojo.keys())
