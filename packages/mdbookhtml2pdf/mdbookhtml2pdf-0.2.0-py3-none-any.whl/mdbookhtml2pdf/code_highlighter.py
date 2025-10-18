from bs4 import BeautifulSoup
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer, guess_lexer
from pygments.util import ClassNotFound

HIGHLIGHTJS_TO_PYGMENTS = {
    "gradle": "groovy",
    "bp": "blueprint",
    "sh": "shell",
}

async def process_code_block(code_block, soup):
    """处理代码高亮"""
    try:
        code = code_block.get_text()

        # 获取语言类型
        language = None
        if code_block.get('class'):
            for cls in code_block.get('class'):
                if cls.startswith('language-'):
                    language = cls.replace('language-', '')
                    break

        # 确定使用的样式 - 使用更适合打印的主题
        style_name = 'vs'  # 改为 vs 主题，更适合打印

        try:
            if language == "mermaid":
                # 跳过mermaid块
                return
            # 转换器, highlight.js to pygments, 这两个中的语言不太一样.
            if language in HIGHLIGHTJS_TO_PYGMENTS:
                mapped_lang = HIGHLIGHTJS_TO_PYGMENTS[language]
                lexer = get_lexer_by_name(mapped_lang)
            elif language:
                lexer = get_lexer_by_name(language)
            else:
                lexer = guess_lexer(code)
        except ClassNotFound as e:
            print(f"无法找到语言解析器: {e}")
            lexer = TextLexer()

        # 检查是否为块级元素
        is_block = code_block.parent.name == 'pre'

        # 使用特定的格式化选项
        formatter = HtmlFormatter(
            style=style_name,
            cssclass='highlight',  # 使用统一的基础类名
            nowrap=False if is_block else True,
            linenos=False,
            noclasses=False,  # 确保生成类名
        )

        highlighted = highlight(code, lexer, formatter)

        # 创建包装元素
        new_div = soup.new_tag('div' if is_block else 'span')
        new_div['class'] = f'highlight' if is_block else 'highlight-inline'

        # 直接使用 HTML 字符串创建新的标签
        new_code = BeautifulSoup(highlighted, 'html.parser')
        if new_code.contents:
            new_div.extend(new_code.contents)

        code_block.replace_with(new_div)

        # 添加样式（只添加一次）
        if not soup.find('style', class_='pygments-style'):
            style_tag = soup.new_tag('style')
            style_tag['class'] = 'pygments-style'

            # 生成基础高亮样式
            base_style = formatter.get_style_defs('.highlight')

            # 添加优化的容器样式
            container_style = """
            /* 代码块容器样式 */
            .highlight {
                break-inside: avoid;
                display: block;
                padding: 1em;
                font-size: 8pt;
                border-radius: 4px;
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                overflow-wrap: break-word;
                word-wrap: break-word;
                word-break: break-all;
                margin: 1em 0;
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            }

            /* 行内代码样式 */
            .highlight-inline {
                display: inline;
                border-radius: 3px;
                background-color: #f6f8fa;
                color: #24292e;
                border: 1px solid #e1e4e8;
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
                font-size: 85%;
            }

            /* 代码块内部样式 */
            .highlight pre {
                margin: 0;
                padding: 0;
                background: transparent;
            }

            .highlight span {
                white-space: pre-wrap;
                word-wrap: break-word;
                word-break: break-all;
                overflow-wrap: break-word;
            }

            /* 确保语法高亮颜色在PDF中正确显示 */
            .highlight .hll { background-color: #ffffcc }
            .highlight .c { color: #6a737d; font-style: italic } /* Comment */
            .highlight .err { color: #d73a49; background-color: #ffeef0 } /* Error */
            .highlight .k { color: #d73a49; font-weight: bold } /* Keyword */
            .highlight .o { color: #24292e; font-weight: bold } /* Operator */
            .highlight .ch { color: #6a737d; font-style: italic } /* Comment.Hashbang */
            .highlight .cm { color: #6a737d; font-style: italic } /* Comment.Multiline */
            .highlight .cp { color: #6a737d; font-style: italic } /* Comment.Preproc */
            .highlight .cpf { color: #6a737d; font-style: italic } /* Comment.PreprocFile */
            .highlight .c1 { color: #6a737d; font-style: italic } /* Comment.Single */
            .highlight .cs { color: #6a737d; font-style: italic } /* Comment.Special */
            .highlight .gd { color: #24292e; background-color: #ffeef0 } /* Generic.Deleted */
            .highlight .ge { color: #24292e; font-style: italic } /* Generic.Emph */
            .highlight .gi { color: #24292e; background-color: #f0fff4 } /* Generic.Inserted */
            .highlight .gs { color: #24292e; font-weight: bold } /* Generic.Strong */
            .highlight .gu { color: #6f42c1; font-weight: bold } /* Generic.Subheading */
            .highlight .kc { color: #d73a49; font-weight: bold } /* Keyword.Constant */
            .highlight .kd { color: #d73a49; font-weight: bold } /* Keyword.Declaration */
            .highlight .kn { color: #d73a49; font-weight: bold } /* Keyword.Namespace */
            .highlight .kp { color: #d73a49; font-weight: bold } /* Keyword.Pseudo */
            .highlight .kr { color: #d73a49; font-weight: bold } /* Keyword.Reserved */
            .highlight .kt { color: #d73a49; font-weight: bold } /* Keyword.Type */
            .highlight .m { color: #005cc5 } /* Literal.Number */
            .highlight .s { color: #032f62 } /* Literal.String */
            .highlight .na { color: #6f42c1 } /* Name.Attribute */
            .highlight .nb { color: #005cc5 } /* Name.Builtin */
            .highlight .nc { color: #6f42c1; font-weight: bold } /* Name.Class */
            .highlight .no { color: #005cc5 } /* Name.Constant */
            .highlight .nd { color: #6f42c1; font-weight: bold } /* Name.Decorator */
            .highlight .ni { color: #005cc5 } /* Name.Entity */
            .highlight .ne { color: #d73a49; font-weight: bold } /* Name.Exception */
            .highlight .nf { color: #6f42c1; font-weight: bold } /* Name.Function */
            .highlight .nl { color: #005cc5 } /* Name.Label */
            .highlight .nn { color: #6f42c1; font-weight: bold } /* Name.Namespace */
            .highlight .nx { color: #6f42c1 } /* Name.Other */
            .highlight .py { color: #005cc5 } /* Name.Property */
            .highlight .nt { color: #d73a49; font-weight: bold } /* Name.Tag */
            .highlight .nv { color: #005cc5 } /* Name.Variable */
            .highlight .ow { color: #d73a49; font-weight: bold } /* Operator.Word */
            .highlight .w { color: #24292e } /* Text.Whitespace */
            .highlight .mb { color: #005cc5 } /* Literal.Number.Bin */
            .highlight .mf { color: #005cc5 } /* Literal.Number.Float */
            .highlight .mh { color: #005cc5 } /* Literal.Number.Hex */
            .highlight .mi { color: #005cc5 } /* Literal.Number.Integer */
            .highlight .mo { color: #005cc5 } /* Literal.Number.Oct */
            .highlight .sa { color: #032f62 } /* Literal.String.Affix */
            .highlight .sb { color: #032f62 } /* Literal.String.Backtick */
            .highlight .sc { color: #032f62 } /* Literal.String.Char */
            .highlight .dl { color: #032f62 } /* Literal.String.Delimiter */
            .highlight .sd { color: #6a737d; font-style: italic } /* Literal.String.Doc */
            .highlight .s2 { color: #032f62 } /* Literal.String.Double */
            .highlight .se { color: #032f62 } /* Literal.String.Escape */
            .highlight .sh { color: #032f62 } /* Literal.String.Heredoc */
            .highlight .si { color: #032f62 } /* Literal.String.Interpol */
            .highlight .sx { color: #032f62 } /* Literal.String.Other */
            .highlight .sr { color: #032f62 } /* Literal.String.Regex */
            .highlight .s1 { color: #032f62 } /* Literal.String.Single */
            .highlight .ss { color: #032f62 } /* Literal.String.Symbol */
            .highlight .bp { color: #005cc5 } /* Name.Builtin.Pseudo */
            .highlight .fm { color: #6f42c1; font-weight: bold } /* Name.Function.Magic */
            .highlight .vc { color: #005cc5 } /* Name.Variable.Class */
            .highlight .vg { color: #005cc5 } /* Name.Variable.Global */
            .highlight .vi { color: #005cc5 } /* Name.Variable.Instance */
            .highlight .vm { color: #005cc5 } /* Name.Variable.Magic */
            .highlight .il { color: #005cc5 } /* Literal.Number.Integer.Long */
            """

            style_tag.string = base_style + container_style
            if soup.head:
                soup.head.append(style_tag)
            else:
                print("文档没有 <head> 标签，无法插入样式")

    except Exception as e:
        import traceback
        print(f"代码高亮处理失败: {e}")
        print(traceback.format_exc())