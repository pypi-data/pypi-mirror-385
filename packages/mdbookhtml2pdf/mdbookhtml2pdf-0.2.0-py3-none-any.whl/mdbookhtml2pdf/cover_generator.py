import os
import toml
from datetime import datetime
from bs4 import BeautifulSoup

async def generate_cover(book_toml_path: str, soup: BeautifulSoup) -> None:
    """生成PDF封面"""
    try:
        # 读取book.toml文件
        with open(book_toml_path, 'r', encoding='utf-8') as f:
            book_config = toml.load(f)

        # 统计字数
        content_div = soup.find('div', id='content')
        word_count = 0
        if content_div:
            word_count = len(''.join(content_div.stripped_strings))

        # 创建封面容器
        cover_container = soup.new_tag('div')
        cover_container['class'] = 'cover-container'

        # 添加装饰元素
        corner_decoration = soup.new_tag('div')
        corner_decoration['class'] = 'corner-decoration'
        cover_container.append(corner_decoration)

        # 添加书名
        book_title = soup.new_tag('div')
        book_title['class'] = 'book-title'
        # 处理书名，如果包含换行符则分割
        title_text = book_config['book']['title']
        title_text = title_text.capitalize()
        if '\n' in title_text:
            title_lines = title_text.split('\n')
            for i, line in enumerate(title_lines):
                if i > 0:
                    book_title.append(soup.new_tag('br'))
                book_title.append(line)
        else:
            book_title.string = title_text
        cover_container.append(book_title)

        # 添加作者
        author = soup.new_tag('div')
        author['class'] = 'author'
        author.string = f"作者 · {', '.join(book_config['book']['authors'])}"
        cover_container.append(author)

        # 添加元信息容器
        meta_info = soup.new_tag('div')
        meta_info['class'] = 'meta-info'

        # 更新时间
        update_time = soup.new_tag('div')
        update_time['class'] = 'update-time'
        update_time.string = f"最后更新于 {datetime.now().strftime('%Y年%m月%d日')}"
        meta_info.append(update_time)

        # 字数统计
        word_count_div = soup.new_tag('div')
        word_count_div['class'] = 'word-count'
        word_count_div.string = f"全书共计 {word_count:,} 字"
        meta_info.append(word_count_div)

        cover_container.append(meta_info)

        # 在内容最前面插入封面
        content_div = soup.find('div', id='content')
        if content_div:
            content_div.insert(0, cover_container)

        # 添加封面样式
        cover_style = soup.new_tag('style')
        cover_style['class'] = 'cover-style'
        cover_style.string = """
        /* ==================== 封面容器样式 ==================== */
        .cover-container {
            width: 186mm;
            height: 263mm;
            background: white;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 30px;
            position: relative;
            overflow: hidden;
            border-radius: 2px;
            margin: 0 auto;
            page-break-after: always;
        }

        /* 顶部装饰条 */
        .cover-container::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 8px;
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        }

        /* ==================== 书名样式 ==================== */
        .book-title {
            font-size: 42pt;
            font-weight: 600;
            margin: 40px 0;
            color: #2c3e50;
            line-height: 1.3;
            letter-spacing: 2px;
            text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.05);
            font-family: "Noto Serif SC", "SimSun", serif;
            text-align: center;
        }

        /* ==================== 作者样式 ==================== */
        .author {
            font-size: 20pt;
            margin: 60px 0;
            color: #7f8c8d;
            letter-spacing: 3px;
            position: relative;
            display: inline-block;
            text-align: center;
        }

        .author::after {
            content: "";
            position: absolute;
            bottom: -15px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, #3498db 50%, transparent 100%);
        }

        /* ==================== 元信息样式 ==================== */
        .meta-info {
            margin-top: 80px;
            font-size: 13pt;
            color: #95a5a6;
            line-height: 1.8;
            text-align: center;
        }

        .update-time {
            font-weight: 300;
        }

        .word-count {
            font-style: italic;
            letter-spacing: 1px;
        }

        /* ==================== 装饰元素 ==================== */
        .corner-decoration {
            position: absolute;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            opacity: 0.1;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            clip-path: polygon(0 40%, 40% 40%, 40% 0, 100% 0, 100% 100%, 0 100%);
        }

        /* ==================== 封面页面设置 ==================== */
        @page cover {
            size: A4;
            margin: 0;
        }

        .cover-container {
            page: cover;
            break-after: page;
        }
        """

        if soup.head:
            soup.head.append(cover_style)
        else:
            print("文档没有 <head> 标签，无法插入封面样式")

    except Exception as e:
        print(f"生成封面时出错: {e}")
        import traceback
        print(traceback.format_exc())