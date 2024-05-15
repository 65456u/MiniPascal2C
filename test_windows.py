import os
import subprocess
import tempfile


def code_analyze(code: str) -> str:
    """
    使用 Clang Static Analyzer 对给定的 C 代码进行静态分析,
    返回分析结果的输出。
    """
    # 创建临时文件存储代码
    with tempfile.NamedTemporaryFile(mode = 'w', suffix = '.c', delete = False) as tmp_file:
        tmp_file.write(code)
        tmp_file_name = tmp_file.name

    # 确保路径格式在 Windows 上正确
    tmp_file_name = os.path.abspath(tmp_file_name)

    # 构建 Clang 命令
    command = ["clang", "-c", "--analyze", tmp_file_name]

    # 启动子进程
    process = subprocess.Popen(
        command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
    )

    # 获取输出
    stdout, stderr = process.communicate()

    # 删除临时文件
    try:
        os.remove(tmp_file_name)
    except Exception as e:
        print(f"Failed to delete temporary file: {e}")

    return stdout or stderr


# 示例用法
code = """
#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
"""
print(code_analyze(code))
