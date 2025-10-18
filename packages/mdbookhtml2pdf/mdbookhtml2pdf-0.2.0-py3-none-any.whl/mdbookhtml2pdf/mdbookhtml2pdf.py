import sys
import asyncio

from .processor import process_html_file

def main():
    """主函数 - 命令行入口点"""
    # 检查命令行参数个数
    if len(sys.argv) != 2:
        print("使用方法: python -m mdbookhtml2pdf <html文件>")  # 打印使用方法
        sys.exit(1)  # 退出脚本并返回错误代码

    html_file = sys.argv[1]  # 获取HTML文件名
    asyncio.run(process_html_file(html_file))  # 运行异步函数处理HTML文件

if __name__ == "__main__":
    main()  # 调用主函数执行脚本
