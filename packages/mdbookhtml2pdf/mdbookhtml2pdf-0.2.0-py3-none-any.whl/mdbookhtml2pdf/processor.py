import os
import time
import asyncio
from bs4 import BeautifulSoup
from weasyprint import HTML

from .toc_generator import generate_toc
from .code_highlighter import process_code_block
from .mermaid_processor import process_mermaid
from .cover_generator import generate_cover
from .utils import check_mermaid_cli

async def process_html_file(html_file):
    start_time = time.time()

    # 获取book.toml路径
    book_toml_path = os.path.join(os.path.dirname(html_file), '..', 'book.toml')

    # 获取输入文件的目录
    output_dir = os.path.dirname(os.path.abspath(html_file))
    mermaid_dir = os.path.join(output_dir, 'mermaid_images')
    os.makedirs(mermaid_dir, exist_ok=True)  # 提前创建mermaid目录

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    parse_time = time.time() - start_time
    print(f"HTML解析耗时: {parse_time:.2f}秒")

    # 清理多余的UI元素（菜单栏、搜索框等）
    cleanup_start = time.time()

    # 移除菜单栏
    menu_bar = soup.find('div', class_='menu-bar')
    if menu_bar:
        menu_bar.decompose()

    # 移除菜单栏占位符
    menu_placeholder = soup.find('div', id='menu-bar-hover-placeholder')
    if menu_placeholder:
        menu_placeholder.decompose()

    # 移除搜索框
    search_wrapper = soup.find('div', id='search-wrapper')
    if search_wrapper:
        search_wrapper.decompose()

    # 移除不必要的脚本（特别是处理菜单栏交互的脚本）
    for script in soup.find_all('script'):
        script_text = script.get_text()
        if script_text and ('sidebar-toggle' in script_text or 'menu-bar' in script_text):
            script.decompose()

    cleanup_time = time.time() - cleanup_start
    print(f"UI元素清理耗时: {cleanup_time:.2f}秒")

    # 检查是否存在mermaid图表
    mermaid_blocks = soup.find_all('pre', class_='mermaid')
    if mermaid_blocks:
        # 如果存在mermaid图表，检查是否安装了mermaid-cli
        if not await check_mermaid_cli():
            print("\n错误: 检测到文档中包含 Mermaid 图表，但未安装 mermaid-cli 工具")
            print("请按照以下步骤安装 mermaid-cli:")
            print("\n1. 首先确保已安装 Node.js 和 npm")
            print("2. 然后运行以下命令安装 mermaid-cli:")
            print("\n   npm install -g @mermaid-js/mermaid-cli")
            print("\n安装完成后重新运行本程序")
            import sys
            sys.exit(1)

    # 获取或创建content div
    content_div = soup.find('div', id='content')
    if not content_div:
        content_div = soup.new_tag('div')
        content_div['id'] = 'content'
        if soup.body:
            soup.body.append(content_div)

    # 先生成目录
    toc_start = time.time()
    toc = await generate_toc(soup)
    if toc:  # 确保目录生成成功
        content_div.insert(0, toc)  # 先插入目录
    toc_time = time.time() - toc_start
    print(f"目录生成耗时: {toc_time:.2f}秒")

    # 再生成封面（在目录之前）
    cover_time = 0
    if os.path.exists(book_toml_path):
        cover_start = time.time()
        await generate_cover(book_toml_path, soup)
        cover_time = time.time() - cover_start
        print(f"封面生成耗时: {cover_time:.2f}秒")

    # 处理代码高亮
    code_start = time.time()
    code_blocks = soup.find_all('code')
    code_tasks = [process_code_block(block, soup) for block in code_blocks]
    await asyncio.gather(*code_tasks)
    code_time = time.time() - code_start
    print(f"代码高亮处理耗时: {code_time:.2f}秒 (处理了{len(code_blocks)}个代码块)")

    # 处理mermaid图表
    mermaid_time = 0
    if mermaid_blocks:
        mermaid_start = time.time()
        semaphore = asyncio.Semaphore(2)
        async def process_mermaid_with_semaphore(block, soup, i, mermaid_dir):
            async with semaphore:
                return await process_mermaid(block, soup, i, mermaid_dir)

        mermaid_tasks = [process_mermaid_with_semaphore(block, soup, i, mermaid_dir) for i, block in enumerate(mermaid_blocks)]
        await asyncio.gather(*mermaid_tasks)
        mermaid_time = time.time() - mermaid_start
        print(f"Mermaid图表处理耗时: {mermaid_time:.2f}秒 (处理了{len(mermaid_blocks)}个图表)")

    # 添加CSS样式和保存HTML
    save_start = time.time()
    style = soup.new_tag('style')
    style.string = """
    /* ==================== 页面样式 ==================== */
    @page {
        /* 右下角页码 */
        @bottom-right {
            background: #3498db;
            content: counter(page);
            height: 1cm;
            margin-left: 0.3em;
            text-align: center;
            width: 1cm;
            border-radius: 50%;
            line-height: 1cm;
            font-weight: bold;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
            margin-top: 7pt;
        }

        /* 顶部装饰线 */
        @top-center {
            background: #3498db;
            content: '';
            display: block;
            height: .05cm;
            opacity: .5;
            width: 100%;
            margin-bottom: 7pt;
        }

        /* 底部装饰线 */
        @bottom-center {
            background: #3498db;
            content: '';
            display: block;
            height: .05cm;
            opacity: .5;
            width: 100%;
            margin-top: 7pt;
        }

        /* 左上角章节标题 */
        @top-left {
            content: string(chapter_title);
            font-size: 9pt;
            height: 1cm;
            vertical-align: middle;
            width: 100%;
            margin-bottom: 7pt;
        }

        /* 右上角章节编号 */
        @top-right {
            content: string(chapter);
            font-size: 9pt;
            height: 1cm;
            vertical-align: middle;
            width: 100%;
            margin-left: 0.3em;
            margin-bottom: 7pt;
        }
    }

    /* ==================== 基础样式 ==================== */
    html {
        color: #393939;
        font-family: Fira Sans;
        font-size: 11pt;
        font-weight: 300;
        line-height: 1.5;
    }

    /* ==================== Mermaid图表样式 ==================== */
    .mermaid {
        max-width: 100%;
        break-inside: avoid;
        width: auto;
        height: auto;
        image-rendering: high-quality;
        -webkit-image-rendering: high-quality;
        -ms-image-rendering: high-quality;
    }

    /* ==================== 标题样式 ==================== */
    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        string-set: chapter content();
        break-after: avoid;
    }

    h1 {
        string-set: chapter_title content();
    }

    img {
        max-width: 100%;
        max-height: 90vh;
    }

    /* ==================== 打印样式 ==================== */
    @media print {
        table {
            page-break-after: auto;
        }

        tr {
            page-break-inside: avoid;
            page-break-after: auto;
        }

        td {
            page-break-inside: avoid;
            page-break-after: auto;
        }

        thead {
            display: table-header-group;
        }

        tfoot {
            display: table-footer-group;
        }
    }
    """
    soup.head.append(style)

    output_html = html_file.replace('.html', '_processed.html')
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    save_time = time.time() - save_start
    print(f"HTML保存耗时: {save_time:.2f}秒")

    print(f"开始生成PDF, 时间较长，请耐心等待...")

    # 生成PDF并统计页数
    pdf_start = time.time()
    pdf_path = html_file.replace('.html', '.pdf')

    # 添加动态耗时显示
    import threading

    def show_progress():
        start = time.time()
        while True:
            elapsed = time.time() - start
            print(f"\rPDF生成中... 已耗时: {elapsed:.1f}秒", end="", flush=True)
            time.sleep(1)

    # 启动进度显示线程
    progress_thread = threading.Thread(target=show_progress, daemon=True)
    progress_thread.start()

    try:
        html = HTML(output_html)
        pdf_document = html.write_pdf(pdf_path)

        # 使用WeasyPrint计算页数
        total_pages = len(html.render().pages)
        pdf_time = time.time() - pdf_start

        # 停止进度显示并输出最终结果
        print(f"\rPDF生成完成! 总耗时: {pdf_time:.2f}秒")
        print(f"PDF总页数: {total_pages}页")
        print(f"平均每页处理时间: {pdf_time/total_pages:.2f}秒")
        print(f"\nPDF文件已生成: {os.path.abspath(pdf_path)}")

    except Exception as e:
        print(f"\rPDF生成失败: {e}")
        raise

    total_time = time.time() - start_time
    print(f"\n总耗时统计:")
    print(f"{'处理步骤':<15} {'耗时(秒)':<10} {'占比':<10}")
    print("-" * 35)
    print(f"{'HTML解析':<15} {parse_time:>10.2f} {parse_time/total_time*100:>9.1f}%")
    print(f"{'封面生成':<15} {cover_time:>10.2f} {cover_time/total_time*100:>9.1f}%")
    print(f"{'目录生成':<15} {toc_time:>10.2f} {toc_time/total_time*100:>9.1f}%")
    print(f"{'代码高亮':<15} {code_time:>10.2f} {code_time/total_time*100:>9.1f}%")
    print(f"{'Mermaid处理':<15} {mermaid_time:>10.2f} {mermaid_time/total_time*100:>9.1f}%")
    print(f"{'HTML保存':<15} {save_time:>10.2f} {save_time/total_time*100:>9.1f}%")
    print(f"{'PDF生成':<15} {pdf_time:>10.2f} {pdf_time/total_time*100:>9.1f}%")
    print("-" * 35)
    print(f"{'总计':<15} {total_time:>10.2f} {'100.0':>9}%")
    print(f"平均每页耗时: {total_time/total_pages:.2f}秒")