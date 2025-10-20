from .server import main

# __init__.py 和 __main__.py 执行顺序和作用
# __init__.py 文件作用：
# 将 weather 目录标记为 Python 包
# 从 server 模块导入 main 函数，使得包可以直接访问 main 函数
# 执行时机：当包被导入时执行
# __main__.py 文件作用：
# 允许包作为脚本直接运行（python -m weather）
# 导入并调用 main 函数启动应用程序
# 执行时机：当使用 python -m weather 命令时执行，-m是module的简称，指定要执行的模块
# 执行顺序
# 正常导入场景：只有 __init__.py 会被执行
# 模块运行场景：先执行 __init__.py（导入包时），再执行 __main__.py（运行模块时）
# 这两个文件共同支持不同的使用方式：
# 既可以通过 project.scripts 定义的命令行工具启动，也可以通过 python -m weather 直接运行包。

print("执行__init__")