"""
mdBook HTML to PDF Converter

将 mdBook 生成的 HTML 文件转换为 PDF，支持：
- 自动生成目录（TOC）
- 代码高亮
- Mermaid 图表转换
"""

__version__ = "0.1.1"
__author__ = "min"
__email__ = "testmin@outlook.com"

from .processor import process_html_file
from .toc_generator import generate_toc
from .code_highlighter import process_code_block
from .mermaid_processor import process_mermaid
from .cover_generator import generate_cover
from .utils import check_mermaid_cli

# 导出主要函数
__all__ = [
    'process_html_file',
    'generate_toc', 
    'process_code_block',
    'process_mermaid',
    'generate_cover',
    'check_mermaid_cli'
]