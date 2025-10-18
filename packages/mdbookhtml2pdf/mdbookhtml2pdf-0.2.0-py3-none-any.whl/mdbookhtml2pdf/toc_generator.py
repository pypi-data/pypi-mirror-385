import hashlib
import re
from bs4 import BeautifulSoup


def _to_chinese_numeral(number):
    """Convert a positive integer into simplified Chinese numerals."""
    if number <= 0:
        return str(number)

    digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    unit_map = {3: '千', 2: '百', 1: '十', 0: ''}
    big_units = ['', '万', '亿', '兆']

    def convert_section(section):
        if section == 0:
            return digits[0]
        result = []
        digit_seen = False
        remaining = section
        for power in range(3, -1, -1):
            divisor = 10 ** power
            digit = remaining // divisor
            if digit:
                result.append(digits[digit] + unit_map[power])
                digit_seen = True
            else:
                if digit_seen and remaining % divisor and (not result or result[-1] != '零'):
                    result.append('零')
            remaining %= divisor
        section_str = ''.join(result).rstrip('零')
        if section_str.startswith('一十'):
            section_str = section_str[1:]
        return section_str or digits[0]

    sections = []
    while number > 0:
        sections.append(number % 10000)
        number //= 10000

    result_parts = []
    for idx in range(len(sections) - 1, -1, -1):
        section = sections[idx]
        if section == 0:
            if result_parts and result_parts[-1] != '零':
                lower_has_content = any(sections[i] != 0 for i in range(idx))
                if lower_has_content:
                    result_parts.append('零')
            continue
        if result_parts and result_parts[-1] != '零' and section < 1000 and idx != len(sections) - 1:
            result_parts.append('零')
        section_text = convert_section(section)
        result_parts.append(section_text + big_units[idx])

    result = ''.join(result_parts)
    if result.startswith('一十'):
        result = result[1:]
    return result or digits[0]


def _slugify(text):
    """Generate a slug-like identifier from heading text."""
    cleaned = re.sub(r'\s+', '-', text.strip())
    cleaned = re.sub(r'[^0-9a-zA-Z\- _]', '', cleaned).replace(' ', '-')
    cleaned = cleaned.lower().strip('-')
    if not cleaned:
        cleaned = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
    return cleaned


def _ensure_heading_id(header, soup):
    """Guarantee that a heading has a unique id attribute."""
    if header.get('id'):
        return header['id']
    base = _slugify(header.get_text(strip=True) or 'section')
    candidate = base
    suffix = 1
    while soup.find(id=candidate):
        candidate = f"{base}-{suffix}"
        suffix += 1
    header['id'] = candidate
    return candidate


def _collect_headings(content_div, soup):
    """Collect heading metadata including numbering prefixes."""
    headings = []
    current_indices = [0] * 6
    for header in content_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = header.get_text(strip=True)
        if not text:
            continue
        heading_id = _ensure_heading_id(header, soup)
        level = int(header.name[1])
        current_indices[level - 1] += 1
        for idx in range(level, 6):
            current_indices[idx] = 0
        prefix = '.'.join(str(i) for i in current_indices if i > 0)
        if level == 1:
            display_prefix = f"第{_to_chinese_numeral(current_indices[0])}章"
        else:
            display_prefix = prefix
        headings.append({
            'tag': header,
            'level': level,
            'id': heading_id,
            'text': text,
            'prefix': prefix,
            'display_prefix': display_prefix,
        })
    return headings


def _build_nested_list(soup, items, base_class):
    """Create a nested unordered list for the provided heading items."""
    if not items:
        return None

    root_ul = soup.new_tag('ul')
    root_ul['class'] = [base_class]
    stack = [(0, root_ul)]

    for item in items:
        level = item['level']
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent_level, parent_ul = stack[-1]
        li = soup.new_tag('li')
        li['class'] = [f'{base_class}__item', f'level-{level}']
        link = soup.new_tag('a')
        link['href'] = f"#{item['id']}"
        link['class'] = [f'{base_class}__link']
        title = soup.new_tag('span')
        title['class'] = [f'{base_class}__title']
        prefix = item.get('display_prefix', item['prefix'])
        title.string = f"{prefix} {item['text']}".strip()
        page = soup.new_tag('span')
        page['class'] = [f'{base_class}__page']
        page['data-target'] = link['href']
        link.append(title)
        link.append(page)
        li.append(link)
        parent_ul.append(li)
        child_ul = soup.new_tag('ul')
        child_ul['class'] = [base_class]
        li.append(child_ul)
        stack.append((level, child_ul))

    for child_ul in root_ul.find_all('ul'):
        if not child_ul.contents:
            child_ul.decompose()

    return root_ul


def _build_global_toc(soup, headings):
    """Create the global table of contents section."""
    toc_section = soup.new_tag('section')
    toc_section['id'] = 'global-table-of-contents'
    title = soup.new_tag('div')
    title['class'] = ['toc-title']
    title.string = '目录'
    toc_section.append(title)
    nav = soup.new_tag('nav')
    nav['id'] = 'toc-global'
    nav['role'] = 'doc-toc'
    toc_list = _build_nested_list(soup, headings, 'toc-list')
    if toc_list:
        nav.append(toc_list)
    toc_section.append(nav)
    return toc_section


def _build_local_tocs(soup, headings):
    """Insert chapter-level TOCs directly after each h1 element."""
    for existing in soup.select('.chapter-toc'):
        existing.decompose()
    for index, heading in enumerate(headings):
        if heading['level'] != 1:
            continue
        child_items = []
        probe = index + 1
        while probe < len(headings) and headings[probe]['level'] != 1:
            child_items.append(headings[probe])
            probe += 1
        if not child_items:
            continue
        chapter_toc = soup.new_tag('aside')
        chapter_toc['class'] = 'chapter-toc'
        title = soup.new_tag('div')
        title['class'] = ['chapter-toc__title']
        title.string = '本章目录'
        chapter_toc.append(title)
        toc_list = _build_nested_list(soup, child_items, 'chapter-list')
        if toc_list:
            chapter_toc.append(toc_list)
            heading['tag'].insert_after(chapter_toc)


def _ensure_toc_styles(soup):
    """Inject styling for the global and chapter-level TOCs."""
    if not soup.head:
        return
    style_tag = soup.find('style', attrs={'data-generator': 'toc'})
    if not style_tag:
        style_tag = soup.new_tag('style')
        style_tag['data-generator'] = 'toc'
        soup.head.append(style_tag)
    toc_style = """
/* ==================== 页面分页样式 ==================== */
h2,
h3,
h4,
h5,
h6 {
  page-break-before: always;
  page-break-after: avoid;
}

/* ==================== 全局目录容器 ==================== */
#global-table-of-contents {
  break-before: page;
  page: no-chapter;
  padding: 2cm 0 1cm;
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  border-radius: 12px;
  margin: 1cm 0;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  page-break-after: always;
}

/* 目录标题 */
.toc-title {
  font-size: 26pt;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 1.8cm;
  text-align: center;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  padding: 1em 0;
}

.toc-title::after {
  content: '';
  position: absolute;
  bottom: -0.5cm;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
  border-radius: 2px;
}

/* ==================== 全局目录导航 ==================== */
#toc-global {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 2em 2.5em;
  margin: 0 1cm;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* 目录列表基础样式 */
#toc-global .toc-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

/* 嵌套列表样式 */
#toc-global .toc-list ul {
  list-style: none;
  margin: 0.5em 0 0.5em 1.2em;
  padding-left: 1.2em;
  border-left: 2px solid #e2e8f0;
  position: relative;
}

#toc-global .toc-list ul::before {
  content: '';
  position: absolute;
  left: -2px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #3498db 0%, #2980b9 100%);
  border-radius: 1px;
}

/* 目录项样式 */
#toc-global .toc-list__item {
  margin: 0.5em 0;
  position: relative;
  transition: all 0.3s ease;
}

#toc-global .toc-list__item.level-1 {
  margin-top: 1em;
  margin-bottom: 1.2em;
}

#toc-global .toc-list__item.level-1::before {
  content: '';
  position: absolute;
  left: -1.2em;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  background: #3498db;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 目录链接样式 */
#toc-global .toc-list__link {
  color: #2d3748;
  text-decoration: none;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1.5em;
  font-weight: 500;
  padding: 0.4em 0.6em;
  border-radius: 6px;
  transition: all 0.3s ease;
  position: relative;
}

#toc-global .toc-list__link:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  transform: translateX(2px);
}

/* 目录标题样式 */
#toc-global .toc-list__title {
  flex: 1;
  position: relative;
  padding-right: 1.5em;
  font-variant-numeric: tabular-nums;
}

#toc-global .toc-list__title::after {
  content: leader('.');
  color: rgba(102, 126, 234, 0.8);
  margin-left: 0.5em;
}

/* 页码样式 */
#toc-global .toc-list__page {
  min-width: 2em;
  text-align: right;
  font-weight: 600;
  color: #334155;
  font-variant-numeric: tabular-nums;
  background: rgba(102, 126, 234, 0.12);
  padding: 0.2em 0.5em;
  border-radius: 12px;
}

#toc-global .toc-list__page::before {
  content: target-counter(attr(data-target), page);
}

/* ==================== 章节目录样式 ==================== */
.chapter-toc {
  background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
  border-radius: 8px;
  margin: 1.5em 0 2.5em;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  position: relative;
  page-break-after: always;
}

.chapter-toc::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
}

/* 章节目录标题 */
.chapter-toc__title {
  color: #ffffff;
  font-size: 12pt;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 0;
  padding: 1em 1.4em;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  position: relative;
}

.chapter-toc__title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 1.4em;
  right: 1.4em;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
}

/* 章节目录列表 */
.chapter-toc .chapter-list {
  background: rgba(255, 255, 255, 0.95);
  margin: 0;
  padding: 1.2em 1.4em;
  backdrop-filter: blur(10px);
}

.chapter-toc .chapter-list ul {
  list-style: none;
  margin: 0.3em 0 0.3em 1em;
  padding-left: 1em;
  border-left: 2px solid #fed7e2;
  position: relative;
}

/* 章节目录链接 */
.chapter-toc .chapter-list__link {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  text-decoration: none;
  color: #0f172a;
  font-size: 10pt;
  padding: 0.3em 0;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.chapter-toc .chapter-list__link:hover {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
  transform: translateX(2px);
}

/* 章节目录标题 */
.chapter-toc .chapter-list__title {
  flex: 1;
  position: relative;
  padding-right: 1.2em;
}

.chapter-toc .chapter-list__title::after {
  content: leader('.');
  margin-left: 0.3em;
  color: rgba(10, 132, 255, 0.35);
}

/* 章节目录页码 */
.chapter-toc .chapter-list__page {
  min-width: 1.6em;
  text-align: right;
  font-weight: 600;
  color: #084c9b;
  font-variant-numeric: tabular-nums;
}

.chapter-toc .chapter-list__page::before {
  content: target-counter(attr(data-target), page);
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 768px) {
  #global-table-of-contents {
    margin: 0.5cm;
    padding: 1.5cm 0 0.8cm;
  }

  #toc-global {
    margin: 0;
    padding: 1.5em;
  }

  .chapter-toc {
    margin: 1em 0;
  }
}
"""
    style_tag.string = toc_style


async def generate_toc(soup):
    """Generate the global TOC and chapter-level TOCs."""
    content_div = soup.find('div', id='content')
    if not content_div:
        return
    for existing in soup.select('#global-table-of-contents'):
        existing.decompose()
    for existing in soup.select('#contents'):
        existing.decompose()
    headings = _collect_headings(content_div, soup)
    if not headings:
        return
    _build_local_tocs(soup, headings)
    toc_section = _build_global_toc(soup, headings)
    _ensure_toc_styles(soup)
    return toc_section