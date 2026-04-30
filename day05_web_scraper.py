"""
Day 5 Project: 网页爬虫与错误处理
功能：爬取网页内容，处理各种异常情况，记录日志
作者：duquanyong
日期：2026-05-01
"""
import logging
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# 配置日志
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"scraper_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebScraperError(Exception):
    """自定义爬虫异常基类"""
    pass


class NetworkError(WebScraperError):
    """网络相关错误"""
    pass


class ParseError(WebScraperError):
    """解析相关错误"""
    pass


class WebScraper:
    """网页爬虫 - 带完整错误处理和日志记录"""

    def __init__(self, delay=1, timeout=10, max_retries=3):
        self.delay = delay          # 请求间隔（秒）
        self.timeout = timeout      # 超时时间
        self.max_retries = max_retries  # 最大重试次数
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        })
        self.results = []
        logger.info("爬虫初始化完成")

    def fetch_page(self, url):
        """获取网页内容，带重试机制"""
        logger.info(f"开始获取页面: {url}")

        for attempt in range(1, self.max_retries + 1):
            try:
                # 发送请求
                response = self.session.get(url, timeout=self.timeout)

                # 检查状态码
                if response.status_code == 200:
                    logger.info(f"成功获取页面: {url}")
                    return response.text
                elif response.status_code == 404:
                    raise NetworkError(f"页面不存在: {url}")
                elif response.status_code == 403:
                    raise NetworkError(f"访问被拒绝: {url}")
                elif response.status_code >= 500:
                    raise NetworkError(f"服务器错误: {response.status_code}")
                else:
                    raise NetworkError(f"HTTP错误: {response.status_code}")

            except requests.exceptions.Timeout:
                logger.warning(f"第{attempt}次请求超时: {url}")
                if attempt == self.max_retries:
                    raise NetworkError(f"请求超时，已重试{self.max_retries}次: {url}")

            except requests.exceptions.ConnectionError:
                logger.warning(f"第{attempt}次连接失败: {url}")
                if attempt == self.max_retries:
                    raise NetworkError(f"连接失败，已重试{self.max_retries}次: {url}")

            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常: {e}")
                raise NetworkError(f"请求失败: {e}")

            # 等待后重试
            if attempt < self.max_retries:
                wait_time = attempt * 2
                logger.info(f"等待{wait_time}秒后重试...")
                time.sleep(wait_time)

        return None

    def parse_html(self, html, url):
        """解析HTML，提取标题、链接、段落"""
        if not html:
            raise ParseError("HTML内容为空")

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # 提取标题
            title = soup.title.string if soup.title else "无标题"
            title = title.strip() if title else "无标题"

            # 提取所有段落
            paragraphs = []
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if text and len(text) > 10:  # 过滤短文本
                    paragraphs.append(text)

            # 提取所有链接
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(url, href)
                text = a.get_text(strip=True)
                if text and len(text) > 0:
                    links.append({
                        'text': text,
                        'url': full_url
                    })

            # 提取图片
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                full_url = urljoin(url, src)
                alt = img.get('alt', '无描述')
                images.append({
                    'url': full_url,
                    'alt': alt
                })

            result = {
                'url': url,
                'title': title,
                'paragraphs': paragraphs[:5],  # 只取前5段
                'links': links[:10],           # 只取前10个链接
                'images': images[:5],          # 只取前5张图片
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            logger.info(f"解析完成: {title} (段落:{len(paragraphs)}, 链接:{len(links)}, 图片:{len(images)})")
            return result

        except Exception as e:
            logger.error(f"解析HTML失败: {e}")
            raise ParseError(f"解析失败: {e}")

    def scrape_url(self, url):
        """爬取单个URL"""
        try:
            # 验证URL
            if not self._is_valid_url(url):
                raise ValueError(f"无效的URL: {url}")

            # 获取页面
            html = self.fetch_page(url)

            # 解析内容
            result = self.parse_html(html, url)

            # 保存结果
            self.results.append(result)

            # 礼貌等待
            logger.info(f"等待{self.delay}秒...")
            time.sleep(self.delay)

            return result

        except WebScraperError as e:
            logger.error(f"爬虫错误: {e}")
            return None
        except Exception as e:
            logger.error(f"未预期的错误: {e}")
            return None

    def scrape_multiple(self, urls):
        """批量爬取多个URL"""
        logger.info(f"开始批量爬取，共{len(urls)}个URL")
        successful = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            logger.info(f"[{i}/{len(urls)}] 处理: {url}")
            result = self.scrape_url(url)
            if result:
                successful += 1
            else:
                failed += 1

        logger.info(f"批量爬取完成: 成功{successful}个, 失败{failed}个")
        return successful, failed

    def save_results(self, filename="scraped_data.json"):
        """保存爬取结果到JSON文件"""
        import json
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            logger.info(f"结果已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存失败: {e}")

    def show_summary(self):
        """显示爬取摘要"""
        print("\n" + "=" * 60)
        print("📊 爬取摘要")
        print("=" * 60)
        print(f"总URL数: {len(self.results)}")

        for i, result in enumerate(self.results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   段落: {len(result['paragraphs'])}个")
            print(f"   链接: {len(result['links'])}个")
            print(f"   图片: {len(result['images'])}个")
            print(f"   时间: {result['scraped_at']}")

    def _is_valid_url(self, url):
        """验证URL格式"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except:
            return False


def demo_scrape():
    """演示模式 - 使用本地HTML"""
    logger.info("进入演示模式")

    # 创建示例HTML
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Python学习网站</title></head>
    <body>
        <h1>欢迎学习Python</h1>
        <p>Python是一种简单易学、功能强大的编程语言。</p>
        <p>它广泛应用于Web开发、数据分析、人工智能等领域。</p>
        <p>Python的语法简洁清晰，非常适合初学者。</p>
        <a href="/tutorial">Python教程</a>
        <a href="/examples">代码示例</a>
        <a href="https://python.org">Python官网</a>
        <img src="/logo.png" alt="Python Logo">
    </body>
    </html>
    """

    scraper = WebScraper()

    # 直接解析HTML（不发送网络请求）
    try:
        result = scraper.parse_html(sample_html, "https://example.com")
        scraper.results.append(result)
        scraper.show_summary()
    except Exception as e:
        logger.error(f"演示模式出错: {e}")


def main():
    """主程序 - 网页爬虫"""
    print("=" * 60)
    print("🕷️ 网页爬虫工具 - Day 5 学习成果")
    print("=" * 60)

    print("\n📝 说明：")
    print("1. 输入URL爬取真实网页")
    print("2. 输入 'demo' 使用演示模式")
    print("3. 输入 'quit' 退出")

    scraper = WebScraper()

    while True:
        print("\n" + "-" * 60)
        url = input("\n请输入URL (或 'demo'/'quit'): ").strip()

        if url.lower() == 'quit':
            print("\n👋 再见！")
            break

        if url.lower() == 'demo':
            demo_scrape()
            continue

        # 爬取URL
        result = scraper.scrape_url(url)

        if result:
            print("\n✅ 爬取成功！")
            print(f"标题: {result['title']}")
            print(f"段落数: {len(result['paragraphs'])}")
            print(f"链接数: {len(result['links'])}")

            # 显示前3段内容
            if result['paragraphs']:
                print("\n📄 内容预览:")
                for i, p in enumerate(result['paragraphs'][:3], 1):
                    print(f"  {i}. {p[:100]}...")
        else:
            print("\n❌ 爬取失败，请查看日志")

    # 保存结果
    if scraper.results:
        scraper.save_results()
        scraper.show_summary()


if __name__ == "__main__":
    main()
