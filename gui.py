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
    sourceTxt.tag_remove("colored", "1.0", tk.END)


def compile_txt(source, target):
    sourceStr = source.get("1.0", "end-1c")
    if sourceStr == "":
        return
    compileRes = converter.convert(sourceStr)
    compileSucceeded = compileRes.success
    isVisitingError = compileRes.code != ""
    resString = compileRes.code
    errorMsg = compileRes.error_info if isVisitingError else compileRes.error_messages[0]
    global compileSucceed

    if compileSucceeded:
        compileSucceed = True
        labelRight.config(text="编译状态：成功")
        # c代码写入target文本框
        target.config(state=tk.NORMAL)
        target.delete("1.0", tk.END)
        target.insert(tk.END, resString)
        target.config(state=tk.DISABLED)
        # 处理行号
        t_line_numbers.config(state=tk.NORMAL)
        t_line_numbers.delete("1.0", tk.END)
        lines = target.get("1.0", tk.END).split("\n")
        for i in range(1, len(lines)):
            if i != len(lines)-1:
                t_line_numbers.insert(tk.END, str(i) + "\n")
            else:
                t_line_numbers.insert(tk.END, str(i))
        t_line_numbers.config(state=tk.DISABLED)

    # 语义错误
    elif isVisitingError:
        compileSucceed = False
        labelRight.config(text="编译状态：语义错误")
        # c代码写入target文本框
        target.config(state=tk.NORMAL)
        target.delete("1.0", tk.END)
        target.insert(tk.END, resString)
        # 处理行号，写入错误信息
        t_line_numbers.config(state=tk.NORMAL)
        t_line_numbers.delete("1.0", tk.END)
        lines = target.get("1.0", tk.END).split("\n")
        for i in range(1, len(lines)):
            if i != len(lines)-1:
                t_line_numbers.insert(tk.END, str(i) + "\n")
            else:
                t_line_numbers.insert(tk.END, str(i))
        end_index = t_line_numbers.index(tk.END)
        t_line_numbers.insert(tk.END, "\n\n" + "err:")
        t_line_numbers.tag_add("coloredText", end_index, tk.END)
        t_line_numbers.tag_config("coloredText", foreground="red")
        # 错误信息写入target文本框
        outputErrorMsg = errorMsg.split(":", 5)[4]
        end_index = target.index(tk.END)
        target.insert(tk.END, "\n\n" + outputErrorMsg)
        target.tag_add("coloredText", end_index, tk.END)
        target.tag_config("coloredText", foreground="red")
        # 标红错误行
        lineNum = int(errorMsg.split(":", 2)[1])
        start_index = f"{lineNum}.0"
        end_index = f"{lineNum + 1}.0"
        target.tag_add("colored", start_index, end_index)
        target.tag_config("colored", background="red")
        t_line_numbers.tag_add("colored", start_index, end_index)
        t_line_numbers.tag_config("colored", background="red")
        t_line_numbers.config(state=tk.DISABLED)
        target.config(state=tk.DISABLED)

    # 语法错误
    elif not isVisitingError:
        compileSucceed = False
        labelRight.config(text="编译状态：词法/语法错误")
        # 行号写入错误信息
        t_line_numbers.config(state=tk.NORMAL)
        t_line_numbers.delete("1.0", tk.END)
        t_line_numbers.insert(tk.END, "err:")
        t_line_numbers.tag_add("coloredText", "1.0", tk.END)
        t_line_numbers.tag_config("coloredText", foreground="red")
        t_line_numbers.config(state=tk.DISABLED)
        # target文本框写入错误信息
        outputErrorMsg = errorMsg.split(", at", 1)[0]
        target.config(state=tk.NORMAL)
        target.delete("1.0", tk.END)
        target.insert(tk.END, outputErrorMsg)
        target.tag_add("coloredText", "1.0", tk.END)
        target.tag_config("coloredText", foreground="red")
        target.config(state=tk.DISABLED)
        # 标红错误行
        s_line_numbers.config(state=tk.NORMAL)
        lineNum = int(errorMsg.split("at line ", 1)[1].split(" ", 1)[0])
        start_index = f"{lineNum}.0"
        end_index = f"{lineNum + 1}.0"
        source.tag_add("colored", start_index, end_index)
        source.tag_config("colored", background="red")
        s_line_numbers.tag_add("colored", start_index, end_index)
        s_line_numbers.tag_config("colored", background="red")
        s_line_numbers.config(state=tk.DISABLED)
        
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
