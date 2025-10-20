"""
ChatGPT to Markdown Converter
将ChatGPT导出的对话转换为漂亮的Markdown文件
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .core import convert, main

__all__ = ["convert", "main"]