import os
import subprocess

import customtkinter as ctk
from customtkinter import filedialog

from mp2c import Converter


class MP2CGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.target_txt = None
        self.t_line_numbers = None
        self.frame_target = None
        self.label_right = None
        self.source_txt = None
        self.frame_source = None
        self.frame_texts = None
        self.frame_buttons = None
        self.s_line_numbers = None
        self.label_left = None
        self.title("MiniPascal2C")
        self.geometry("1280x720")
        self.converter = Converter()
        self.compile_succeed = False
        self.cn_font = ctk.CTkFont(family = "思源黑体 CN", size = 15)
        self.create_frames()
        self.create_textbox(self.frame_source, "源文件", True)
        self.create_textbox(self.frame_target, "编译状态：未编译", False)
        self.create_buttons(self.frame_buttons)

    def run(self):
        self.mainloop()

    def create_frames(self):
        self.frame_texts = ctk.CTkFrame(self, width = 1080)
        self.frame_texts.pack(side = ctk.LEFT, fill = ctk.BOTH, expand = True, padx = 10, pady = 10)
        self.frame_buttons = ctk.CTkFrame(self, width = 0)
        self.frame_buttons.pack(side = ctk.BOTTOM, fill = ctk.X, expand = True, padx = 10, pady = 10)
        self.frame_source = ctk.CTkFrame(self.frame_texts, width = 540)
        self.frame_source.pack(side = ctk.LEFT, fill = ctk.BOTH, expand = True, padx = 10, pady = 10)
        self.frame_target = ctk.CTkFrame(self.frame_texts, width = 540)
        self.frame_target.pack(side = ctk.RIGHT, fill = ctk.BOTH, expand = True, padx = 10, pady = 10)

    def create_textbox(self, frame, label_text, is_source):
        label = ctk.CTkLabel(frame, text = label_text, font = self.cn_font)
        scrollbar = ctk.CTkScrollbar(frame)
        line_numbers = ctk.CTkTextbox(frame, width = 40, yscrollcommand = scrollbar.set, activate_scrollbars = False)
        text_box = ctk.CTkTextbox(frame, wrap = "none", yscrollcommand = scrollbar.set, activate_scrollbars = False)

        def multiple_yview(*args):
            if len(args) == 2 and args[0] == 'moveto' and args[1] != 'moveto':
                line_numbers.yview(*args)
                text_box.yview(*args)
            else:
                scrollbar.set(*args)

        scrollbar.configure(command = multiple_yview)
        if not is_source:
            text_box.configure(state = ctk.DISABLED)

        def bind_func(event, line_txt = line_numbers, text = text_box):
            self.update_line_numbers(event, line_txt, text)
            scrollbar.set(line_txt.yview()[0], line_txt.yview()[1])

        label.pack()
        line_numbers.pack(side = ctk.LEFT, fill = ctk.Y, padx = 10, pady = 10)
        line_numbers.configure(state = ctk.DISABLED)
        text_box.pack(side = ctk.LEFT, fill = ctk.BOTH, expand = True, padx = 0, pady = 10)
        text_box.bind("<Key>", bind_func)
        scrollbar.pack(fill = ctk.Y, side = ctk.RIGHT)
        if is_source:
            self.label_left = label
            self.s_line_numbers = line_numbers
            self.source_txt = text_box
        else:
            self.label_right = label
            self.t_line_numbers = line_numbers
            self.target_txt = text_box

    def create_buttons(self, frame):
        # CREATE A LABEL FOR THE BUTTONS
        label = ctk.CTkLabel(frame, text = "MiniPascal2C", font = self.cn_font)
        label.pack(fill = ctk.X, expand = True, padx = 10, pady = 10, side = ctk.TOP)
        buttons = [
            ("打开源文件", self.open_file),
            ("编译源文件", self.compile_txt),
            ("导出目标文件", self.output_txt),
            ("编译运行目标文件", self.execute_txt),
        ]
        for text, command in buttons:
            button = ctk.CTkButton(frame, text = text, command = command, font = self.cn_font)
            button.pack(fill = ctk.X, expand = True, padx = 10, pady = 10, side = ctk.TOP)

    def open_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, "r") as file:
                file_content = file.read()
                self.source_txt.delete("1.0", ctk.END)
                self.source_txt.insert(ctk.END, file_content)
                self.update_line_numbers("", self.s_line_numbers, self.source_txt)

    def update_line_numbers(self, event, line_txt, text):
        line_txt.configure(state = ctk.NORMAL)
        line_txt.delete("1.0", ctk.END)
        lines = text.get("1.0", ctk.END).split("\n")
        for i in range(1, len(lines)):
            if i != len(lines) - 1:
                line_txt.insert(ctk.END, str(i) + "\n")
            else:
                line_txt.insert(ctk.END, str(i))
        line_txt.yview_moveto(text.yview()[0])
        line_txt.configure(state = ctk.DISABLED)
        self.source_txt.tag_remove("colored", "1.0", ctk.END)

    def compile_txt(self):
        source_str = self.source_txt.get("1.0", "end-1c")
        if source_str == "":
            return
        compile_res = self.converter.convert(source_str)
        compile_succeeded = compile_res.success
        is_visiting_error = compile_res.code != ""
        res_string = compile_res.code
        error_msg = compile_res.error_info if is_visiting_error else compile_res.error_messages[0]

        def add_tags(txt, line_numbers, sid, eid):
            txt.tag_add("colored", sid, eid)
            txt.tag_config("colored", background = "red")
            line_numbers.tag_add("colored", sid, eid)
            line_numbers.tag_config("colored", background = "red")
            line_numbers.configure(state = ctk.DISABLED)

        if compile_succeeded:
            self.compile_succeed = True
            self.label_right.configure(text = "编译状态：成功", font = self.cn_font)
            self.target_txt.configure(state = ctk.NORMAL)
            self.target_txt.delete("1.0", ctk.END)
            self.target_txt.insert(ctk.END, res_string)
            self.target_txt.configure(state = ctk.DISABLED)
            self.update_target_line_numbers()

        elif is_visiting_error:
            self.compile_succeed = False
            self.label_right.configure(text = "编译状态：语义错误", font = self.cn_font)
            self.target_txt.configure(state = ctk.NORMAL)
            self.target_txt.delete("1.0", ctk.END)
            self.target_txt.insert(ctk.END, res_string)
            self.update_target_line_numbers()
            end_index = self.t_line_numbers.index(ctk.END)
            self.t_line_numbers.insert(ctk.END, "\n\n" + "err:")
            self.t_line_numbers.tag_add("coloredText", end_index, ctk.END)
            self.t_line_numbers.tag_config("coloredText", foreground = "red")
            output_error_msg = ""
            for errmsg in compile_res.error_messages:
                output_error_msg += errmsg + "\n"
            end_index = self.target_txt.index(ctk.END)
            self.target_txt.insert(ctk.END, "\n\n" + output_error_msg)
            self.target_txt.tag_add("coloredText", end_index, ctk.END)
            self.target_txt.tag_config("coloredText", foreground = "red")
            print(error_msg)
            line_num = int(error_msg.split(".c:", 1)[1].split(":", 1)[0])
            start_index = f"{line_num}.0"
            end_index = f"{line_num + 1}.0"
            add_tags(self.target_txt, self.t_line_numbers, start_index, end_index)
            self.target_txt.configure(state = ctk.DISABLED)

        elif not is_visiting_error:
            self.compile_succeed = False
            self.label_right.configure(text = "编译状态：词法/语法错误", font = self.cn_font)
            self.t_line_numbers.configure(state = ctk.NORMAL)
            self.t_line_numbers.delete("1.0", ctk.END)
            self.t_line_numbers.insert(ctk.END, "err:")
            self.t_line_numbers.tag_add("coloredText", "1.0", ctk.END)
            self.t_line_numbers.tag_config("coloredText", foreground = "red")
            self.t_line_numbers.configure(state = ctk.DISABLED)
            output_error_msg = error_msg.split(", at", 1)[0]
            self.target_txt.configure(state = ctk.NORMAL)
            self.target_txt.delete("1.0", ctk.END)
            self.target_txt.insert(ctk.END, output_error_msg)
            self.target_txt.tag_add("coloredText", "1.0", ctk.END)
            self.target_txt.tag_config("coloredText", foreground = "red")
            self.target_txt.configure(state = ctk.DISABLED)
            self.s_line_numbers.configure(state = ctk.NORMAL)
            line_num = int(error_msg.split("at line ", 1)[1].split(" ", 1)[0])
            start_index = f"{line_num}.0"
            end_index = f"{line_num + 1}.0"
            add_tags(self.source_txt, self.s_line_numbers, start_index, end_index)

    def update_target_line_numbers(self):
        self.t_line_numbers.configure(state = ctk.NORMAL)
        self.t_line_numbers.delete("1.0", ctk.END)
        lines = self.target_txt.get("1.0", ctk.END).split("\n")
        for i in range(1, len(lines)):
            if i != len(lines) - 1:
                self.t_line_numbers.insert(ctk.END, str(i) + "\n")
            else:
                self.t_line_numbers.insert(ctk.END, str(i))
        self.t_line_numbers.configure(state = ctk.DISABLED)

    def output_txt(self):
        if self.compile_succeed:
            string = self.target_txt.get("1.0", "end-1c")
            folder_path = filedialog.askdirectory()
            if folder_path:
                file_path = folder_path + "/output.c"
                with open(file_path, "w") as file:
                    file.write(string)

    def execute_txt(self):
        if self.compile_succeed:
            code = self.target_txt.get("1.0", "end-1c")
            os.makedirs("temp", exist_ok = True)
            compile_result = subprocess.run(['clang', '-lm', '-xc', '-', '-o', "./temp/output"], input = code,
                                            capture_output = True, text = True)
            if compile_result.returncode != 0:
                return None, compile_result.stderr
            command = 'cd ./temp && output.exe'
            subprocess.Popen(["cmd.exe", '/k', command], creationflags = subprocess.CREATE_NEW_CONSOLE)


if __name__ == "__main__":
    app = MP2CGUI()
    app.run()
