import tkinter as tk
import subprocess
import os
from tkinter import filedialog
from mp2c import Converter
converter=Converter()
def open_file(text):
    # filepath = filedialog.askopenfilename(filetypes=[("CPP Files", "*.cpp")])
    filepath = filedialog.askopenfilename()
    if filepath:
        with open(filepath, "r") as file:
            file_content = file.read()
            text.delete("1.0", tk.END)
            text.insert(tk.END, file_content)
            s_line_numbers.config(state=tk.NORMAL)
            s_line_numbers.delete("1.0", tk.END)
            lines = text.get("1.0", tk.END).split("\n")
            for i in range(1, len(lines)):
                if i != len(lines)-1:
                    s_line_numbers.insert(tk.END, str(i) + "\n")
                else:
                    s_line_numbers.insert(tk.END, str(i))
            s_line_numbers.config(state=tk.DISABLED)  

def update_line_numbers(event, lineTxt, text):
    lineTxt.config(state=tk.NORMAL)
    lineTxt.delete("1.0", tk.END)
    lines = text.get("1.0", tk.END).split("\n")
    for i in range(1, len(lines)):
        if i != len(lines)-1:
            lineTxt.insert(tk.END, str(i) + "\n")
        else:
            lineTxt.insert(tk.END, str(i))
    lineTxt.yview_moveto(text.yview()[0])
    lineTxt.config(state=tk.DISABLED)

def on_text_scroll(event, lineTxt, text):
    distance = event.delta
    lineTxt.yview_scroll(int(distance/-40), "units")
    #target = text.yview()[0]
    #lineTxt.yview_moveto(target)

def compile_txt(source, target):
    sourceStr = source.get("1.0", "end-1c")
    # 返回值：[是否编译成功, 字符串]
    tree, tokens, compileRes = converter(sourceStr)
    global compileSucceed
    if compileRes[0]:
        compileSucceed = True
        labelRight.config(text="编译状态：成功")
    else:
        compileSucceed = False
        labelRight.config(text="编译状态：失败")
    resString = compileRes[1]
    # 写入文本框
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

def output_txt(targetTxt):
    if(compileSucceed):
        string = targetTxt.get("1.0", "end-1c")
        folder_path = filedialog.askdirectory()
        if folder_path:
            file_path = folder_path + "/output.c"
            with open(file_path, 'w') as file:
                file.write(string)

def execute_txt(targetTxt):
    if(compileSucceed):
        code = targetTxt.get("1.0", "end-1c")
        # 使用gcc编译C代码
        compile_result = subprocess.run(['gcc', '-xc', '-', '-o', 'temp'], input=code, capture_output=True, text=True)
        # 检查编译是否成功
        if compile_result.returncode != 0:
            return None, compile_result.stderr
        # 运行编译后的可执行文件
        run_result = subprocess.run(['./temp'], capture_output=True, text=True)
        # 获取程序输出和错误信息
        output = run_result.stdout
        error = run_result.stderr
        return output, error


compileSucceed = False

# 创建主窗口
window = tk.Tk()
window.title("pascal2cpp")

# 创建容器框架
frameTop = tk.Frame(window)
frameTop.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
frameBottom = tk.Frame(window)
frameBottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
frameTopLeft = tk.Frame(frameTop)
frameTopLeft.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
frameTopLeftTop = tk.Frame(frameTopLeft)
frameTopLeftTop.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
frameTopLeftBottom = tk.Frame(frameTopLeft)
frameTopLeftBottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
frameTopRight = tk.Frame(frameTop)
frameTopRight.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
frameTopRightTop = tk.Frame(frameTopRight)
frameTopRightTop.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
frameTopRightBottom = tk.Frame(frameTopRight)
frameTopRightBottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

# 左边
labelLeft = tk.Label(frameTopLeftTop, text="源文件")
labelLeft.pack()
# 创建行号文本框
s_line_numbers = tk.Text(frameTopLeftTop, width=4)
s_line_numbers.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
s_line_numbers.config(state=tk.DISABLED)
# 源文件内容显示框
sourceTxt = tk.Text(frameTopLeftTop, wrap="none")
sourceTxt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

## 设置某行颜色变化
# start_line = 2
# end_line = 4
# start_index = f"{start_line}.0"
# end_index = f"{end_line + 1}.0"
# sourceTxt.tag_add("colored", start_index, end_index)
# sourceTxt.tag_config("colored", background="yellow")

# 更新行号，竖向滚动绑定
sourceTxt.bind("<Key>", lambda event:update_line_numbers(event, s_line_numbers, sourceTxt))
sourceTxt.bind("<MouseWheel>", lambda event:on_text_scroll(event, s_line_numbers, sourceTxt))
# 横向滚动
scrollbarL = tk.Scrollbar(frameTopLeftBottom, orient=tk.HORIZONTAL)
scrollbarL.pack(fill=tk.X)
sourceTxt.config(xscrollcommand=scrollbarL.set)
scrollbarL.config(command=sourceTxt.xview)

# 右边
labelRight = tk.Label(frameTopRightTop, text="编译状态：未编译")
labelRight.pack()
# 行号文本框
t_line_numbers = tk.Text(frameTopRightTop, width=4)
t_line_numbers.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
t_line_numbers.config(state=tk.DISABLED)
# 目标文件内容显示框
targetTxt = tk.Text(frameTopRightTop)
targetTxt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
targetTxt.config(state=tk.DISABLED)
# 更新行号
targetTxt.bind("<Key>", lambda event:update_line_numbers(event, t_line_numbers, targetTxt))
targetTxt.bind("<MouseWheel>", lambda event:on_text_scroll(event, t_line_numbers, targetTxt))
# 横向滚动
scrollbarR = tk.Scrollbar(frameTopRightBottom, orient=tk.HORIZONTAL)
scrollbarR.pack(fill=tk.X)
targetTxt.config(xscrollcommand=scrollbarR.set)
scrollbarR.config(command=targetTxt.xview)

# 先渲染一次
window.update()

# 打开文件按钮
buttonOpen = tk.Button(frameBottom, text="打开源文件", command=lambda: open_file(sourceTxt))
buttonOpen.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
buttonCompile = tk.Button(frameBottom, text="编译源文件", command=lambda: compile_txt(sourceTxt, targetTxt))
buttonCompile.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
buttonOutput = tk.Button(frameBottom, text="导出目标文件", command=lambda: output_txt(targetTxt))
buttonOutput.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
buttonExecute = tk.Button(frameBottom, text="编译运行目标文件", command=lambda: execute_txt(targetTxt))
buttonExecute.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 运行主循环
window.mainloop()

