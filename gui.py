import os
import subprocess
import tkinter as tk
from tkinter import filedialog

from mp2c import Converter

converter = Converter()


def open_file(text):
    filepath = filedialog.askopenfilename()
    if filepath:
        with open(filepath, "r") as file:
            file_content = file.read()
            text.delete("1.0", tk.END)
            text.insert(tk.END, file_content)
            update_line_numbers("", s_line_numbers, text)


def update_line_numbers(event, line_txt, text):
    line_txt.configure(state = tk.NORMAL)
    line_txt.delete("1.0", tk.END)
    lines = text.get("1.0", tk.END).split("\n")
    for i in range(1, len(lines)):
        if i != len(lines) - 1:
            line_txt.insert(tk.END, str(i) + "\n")
        else:
            line_txt.insert(tk.END, str(i))
    line_txt.yview_moveto(text.yview()[0])
    line_txt.configure(state = tk.DISABLED)


def compile_txt(source, target):
    sourceStr = source.get("1.0", "end-1c")
    status, compileRes = converter(sourceStr)
    global compileSucceed
    if compileRes[0]:
        compileSucceed = True
        labelRight.configure(text = "编译状态：成功")
    else:
        compileSucceed = False
        labelRight.configure(text = "编译状态：失败")
    resString = compileRes[1]
    target.configure(state = tk.NORMAL)
    target.delete("1.0", tk.END)
    target.insert(tk.END, resString)
    target.configure(state = tk.DISABLED)
    update_line_numbers("", t_line_numbers, target)


def output_txt(target_txt):
    if compileSucceed:
        string = target_txt.get("1.0", "end-1c")
        folder_path = filedialog.askdirectory()
        if folder_path:
            file_path = folder_path + "/output.c"
            with open(file_path, "w") as file:
                file.write(string)


def execute_txt(target_txt):
    if compileSucceed:
        code = target_txt.get("1.0", "end-1c")
        # 如果没有，则创建temp文件夹
        os.makedirs("temp", exist_ok = True)
        # 使用gcc编译C代码
        compile_result = subprocess.run(['gcc', '-xc', '-', '-o', "./temp/output"], input = code, capture_output = True,
                                        text = True)
        # 检查编译是否成功
        if compile_result.returncode != 0:
            return None, compile_result.stderr
        # 运行编译后的可执行文件
        command = 'cd ./temp && output.exe'
        subprocess.Popen(["cmd.exe", '/k', command], creationflags = subprocess.CREATE_NEW_CONSOLE)


compileSucceed = False

window = tk.Tk()
window.title("pascal2cpp")

frameTop = tk.Frame(window)
frameTop.pack(side = tk.TOP, fill = tk.BOTH, expand = True, padx = 10, pady = 10)
frameBottom = tk.Frame(window)
frameBottom.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True, padx = 10, pady = 10)

frameTopLeft = tk.Frame(frameTop)
frameTopLeft.pack(side = tk.LEFT, fill = tk.BOTH, expand = True, padx = 10, pady = 10)
frameTopRight = tk.Frame(frameTop)
frameTopRight.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True, padx = 10, pady = 10)

labelLeft = tk.Label(frameTopLeft, text = "源文件")
labelLeft.pack()

s_line_numbers = tk.Text(frameTopLeft, width = 4)
s_line_numbers.pack(side = tk.LEFT, fill = tk.Y, padx = 10, pady = 10)
s_line_numbers.configure(state = tk.DISABLED)

sourceTxt = tk.Text(frameTopLeft, wrap = "none")
sourceTxt.pack(side = tk.LEFT, fill = tk.BOTH, expand = True, padx = 10, pady = 10)
sourceTxt.bind("<Key>", lambda event: update_line_numbers(event, s_line_numbers, sourceTxt))

scrollbarL = tk.Scrollbar(frameTopLeft, orient = tk.HORIZONTAL)
scrollbarL.pack(fill = tk.X)
sourceTxt.configure(xscrollcommand = scrollbarL.set)
scrollbarL.configure(command = sourceTxt.xview)

labelRight = tk.Label(frameTopRight, text = "编译状态：未编译")
labelRight.pack()

t_line_numbers = tk.Text(frameTopRight, width = 4)
t_line_numbers.pack(side = tk.LEFT, fill = tk.Y, padx = 10, pady = 10)
t_line_numbers.configure(state = tk.DISABLED)

targetTxt = tk.Text(frameTopRight)
targetTxt.pack(side = tk.LEFT, fill = tk.BOTH, expand = True, padx = 10, pady = 10)
targetTxt.configure(state = tk.DISABLED)
targetTxt.bind("<Key>", lambda event: update_line_numbers(event, t_line_numbers, targetTxt))

scrollbarR = tk.Scrollbar(frameTopRight, orient = tk.HORIZONTAL)
scrollbarR.pack(fill = tk.X)
targetTxt.configure(xscrollcommand = scrollbarR.set)
scrollbarR.configure(command = targetTxt.xview)

buttonOpen = tk.Button(frameBottom, text = "打开源文件", command = lambda: open_file(sourceTxt))
buttonOpen.pack(fill = tk.BOTH, expand = True, padx = 10, pady = 10)
buttonCompile = tk.Button(
    frameBottom, text = "编译源文件", command = lambda: compile_txt(sourceTxt, targetTxt)
)
buttonCompile.pack(fill = tk.BOTH, expand = True, padx = 10, pady = 10)
buttonOutput = tk.Button(
    frameBottom, text = "导出目标文件", command = lambda: output_txt(targetTxt)
)
buttonOutput.pack(fill = tk.BOTH, expand = True, padx = 10, pady = 10)
buttonExecute = tk.Button(frameBottom, text = "编译运行目标文件", command = lambda: execute_txt(targetTxt))
buttonExecute.pack(fill = tk.BOTH, expand = True, padx = 10, pady = 10)

# 运行主循环
window.mainloop()
