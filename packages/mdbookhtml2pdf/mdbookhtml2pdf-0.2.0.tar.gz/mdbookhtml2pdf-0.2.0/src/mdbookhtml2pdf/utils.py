import asyncio
from bs4 import BeautifulSoup
import os
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer, guess_lexer
from pygments.util import ClassNotFound
import subprocess
from weasyprint import HTML
import tempfile
import re
import time
import toml
from datetime import datetime
import hashlib
import shutil
import sys

async def check_mermaid_cli():
    """检查是否安装了mermaid-cli工具"""
    if not shutil.which('mmdc'):
        return False
    return True