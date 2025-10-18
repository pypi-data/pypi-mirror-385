import asyncio
import os
import tempfile
import hashlib
from bs4 import BeautifulSoup

async def process_mermaid(mermaid_block, soup, index, output_dir):
    """处理mermaid图表"""
    mermaid_content = mermaid_block.get_text().strip()

    print('处理mermaid内容:', mermaid_content)

    # 检查mermaid内容是否为空
    if not mermaid_content:
        print(f"警告: 空的mermaid块 #{index}")
        return

    # 使用MD5生成唯一的文件名
    content_hash = hashlib.md5(mermaid_content.encode('utf-8')).hexdigest()
    output_file = os.path.join(output_dir, f'mermaid_{content_hash}.png')

    # 检查文件是否已存在
    print('检查文件是否存在:', output_file)
    if os.path.exists(output_file):
        print(f"使用缓存的mermaid图片 #{index}: {os.path.basename(output_file)}")
        # 直接使用已存在的图片
        img = soup.new_tag('img')
        img['src'] = f'{output_dir}/mermaid_{content_hash}.png'
        img['class'] = 'mermaid'
        mermaid_block.replace_with(img)
        return

    # 创建临时文件存储mermaid内容
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
        f.write(mermaid_content)
        mmd_file = f.name

    print('检查mmd文件是否存在:', mmd_file)
    if not os.path.exists(mmd_file):
        print(f"错误: 无法创建临时的mermaid文件 #{index}")
        return

    # 创建Puppeteer配置文件，解决Linux系统上的浏览器启动问题
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"args": ["--no-sandbox"]}')
        puppeteer_config = f.name

    try:
        # 使用python subprocess调用mmdc命令，添加超时设置
        process = await asyncio.create_subprocess_exec(
            'mmdc',
            '-i', mmd_file,
            '-o', output_file,
            '-t', 'default',  # 使用默认主题
            '-b', 'transparent',  # 透明背景
            '-w', '2048',  # 设置宽度（可以根据需要调整）
            '-s', '2',  # 设置缩放比例为2（提高清晰度）
            '--pdfFit',  # 适应PDF大小
            '-q',  # 静默模式
            '-p', puppeteer_config,  # 使用Puppeteer配置文件，包含--no-sandbox参数
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)

            if process.returncode == 0 and os.path.exists(output_file):
                print(f"生成新的mermaid图片 #{index}: {os.path.basename(output_file)}")
                # 创建新的img标签，使用相对路径
                img = soup.new_tag('img')
                img['src'] = f'{output_dir}/mermaid_{content_hash}.png'
                img['class'] = 'mermaid'
                mermaid_block.replace_with(img)
            else:
                print(f"Mermaid转换失败 #{index}: {stderr.decode()}")
                # 保留原始mermaid块
                print(f"原始内容: {mermaid_content[:100]}...")
        except asyncio.TimeoutError:
            print(f"Mermaid转换超时 #{index}")
            process.kill()

    except Exception as e:
        print(f"处理Mermaid图表时出错 #{index}: {e}")
    finally:
        # 清理临时文件
        try:
            os.unlink(mmd_file)
            os.unlink(puppeteer_config)
        except:
            pass