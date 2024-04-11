import subprocess


def format_code(code: str) -> str:
    # clang-format命令
    command = ['clang-format', '-style=llvm']

    # 启动子进程
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)

    # 将代码写入stdin并获取格式化后的代码
    formatted_code, _ = process.communicate(code)

    return formatted_code
