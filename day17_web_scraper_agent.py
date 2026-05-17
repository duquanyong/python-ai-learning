"""
Day 17 Project: 网页爬虫Agent - 自主信息收集
功能：让Agent自主浏览网页、提取信息、收集数据，实现自动化信息获取
作者：duquanyong
日期：2026-05-15
"""

import json
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()


# ========== 基础爬虫工具 ==========

class WebScraper:
    """网页爬虫工具 - 用于Agent调用"""

    def __init__(self, delay=1, timeout=10, max_retries=3):
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch(self, url: str) -> Tuple[bool, str]:
        """获取网页内容"""
        if not self._is_valid_url(url):
            return False, f"无效的URL: {url}"

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    time.sleep(self.delay)
                    return True, response.text
                elif response.status_code == 404:
                    return False, "页面不存在(404)"
                elif response.status_code == 403:
                    return False, "访问被拒绝(403)"
                else:
                    return False, f"HTTP错误: {response.status_code}"

            except requests.exceptions.Timeout:
                if attempt == self.max_retries:
                    return False, "请求超时"
            except requests.exceptions.ConnectionError:
                if attempt == self.max_retries:
                    return False, "连接失败"
            except Exception as e:
                return False, f"请求异常: {e}"

            time.sleep(attempt * 2)

        return False, "重试次数耗尽"

    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """提取网页内容"""
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()

            # 提取标题
            title = soup.title.string if soup.title else "无标题"
            title = title.strip() if title else "无标题"

            # 提取正文
            paragraphs = []
            for p in soup.find_all(['p', 'article', 'section']):
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    paragraphs.append(text)

            # 提取链接
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(url, href)
                text = a.get_text(strip=True)
                if text and len(text) > 0:
                    links.append({'text': text, 'url': full_url})

            # 提取图片
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                full_url = urljoin(url, src)
                alt = img.get('alt', '无描述')
                images.append({'url': full_url, 'alt': alt})

            return {
                'success': True,
                'url': url,
                'title': title,
                'content': '\n\n'.join(paragraphs[:10]),
                'paragraphs_count': len(paragraphs),
                'links': links[:15],
                'images': images[:10],
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_links(self, html: str, base_url: str, keyword: str = "") -> List[Dict[str, str]]:
        """搜索包含关键词的链接"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            matching_links = []

            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                full_url = urljoin(base_url, href)

                # 过滤外部链接和无效链接
                if not self._is_valid_url(full_url):
                    continue

                # 如果有关键词，过滤匹配项
                if keyword and keyword.lower() not in text.lower():
                    continue

                matching_links.append({
                    'text': text[:50],
                    'url': full_url
                })

            return matching_links[:20]

        except Exception as e:
            return []

    def _is_valid_url(self, url: str) -> bool:
        """验证URL"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except:
            return False


# ========== 爬虫Agent ==========

class WebScraperAgent:
    """
    网页爬虫Agent - 自主信息收集

    核心能力：
    1. 自主决定爬取哪些页面
    2. 从页面提取关键信息
    3. 根据结果决定下一步行动
    4. 汇总收集到的信息

    工作流程：
    用户: "帮我搜集Python学习资源"

    Agent思考: 我需要搜索Python学习相关的网页
    Agent行动: 访问Python官网、教程网站
    Agent观察: 获取页面内容，提取链接
    Agent思考: 发现更多相关链接，继续深入
    Agent汇总: 整理所有收集到的资源
    """

    SYSTEM_PROMPT = """你是一个网页爬虫Agent，擅长自主浏览网页、提取信息。

你的职责：
1. 分析用户需求，确定搜索方向
2. 访问相关网页，提取关键信息
3. 发现更多相关链接，深入探索
4. 整理汇总收集到的信息

可用工具：
- fetch(url): 获取网页内容
- extract_content(html, url): 提取网页关键信息
- search_links(html, base_url, keyword): 搜索相关链接

工作原则：
- 每次只访问一个页面
- 提取关键信息，不要全文复制
- 发现相关链接时，选择性深入
- 最终输出结构化的汇总报告

输出格式：
Thought: 你的思考过程
Action: 工具调用
Observation: 观察结果

最终报告格式：
# 信息收集报告
## 来源列表
## 关键发现
## 详细内容
## 建议
"""

    def __init__(self, api_key: Optional[str] = None, max_pages: int = 5):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.max_pages = max_pages  # 最大爬取页面数
        self.llm: Optional[ChatOpenAI] = None
        self.scraper = WebScraper()
        self.visited_urls: set = set()
        self.collected_data: List[Dict[str, Any]] = []

        if self.api_key:
            self._init_llm()
            print("✅ 网页爬虫Agent初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _init_llm(self):
        """初始化LLM"""
        self.llm = ChatOpenAI(
            model="qwen-turbo",
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.3,
        )

    def run(self, task: str, start_url: Optional[str] = None) -> str:
        """
        运行爬虫Agent

        Args:
            task: 任务描述（如"搜集Python学习资源"）
            start_url: 起始URL（可选）

        Returns:
            收集到的信息汇总
        """
        print(f"\n{'='*60}")
        print(f"🕷️ 任务: {task}")
        print(f"{'='*60}")

        if not self.llm:
            return self._demo_run(task)

        # 如果有起始URL，直接开始
        if start_url:
            return self._crawl_from_url(task, start_url)

        # 否则让AI决定从哪开始
        return self._autonomous_crawl(task)

    def _crawl_from_url(self, task: str, url: str) -> str:
        """从指定URL开始爬取"""
        print(f"\n🌐 起始URL: {url}")

        # 获取页面
        success, html = self.scraper.fetch(url)
        if not success:
            return f"爬取失败: {html}"

        # 提取内容
        content = self.scraper.extract_content(html, url)
        if not content['success']:
            return f"解析失败: {content.get('error')}"

        # 使用AI分析内容
        return self._analyze_content(task, content)

    def _autonomous_crawl(self, task: str) -> str:
        """自主爬取 - Agent决定访问哪些页面"""
        print("\n🤖 Agent开始自主爬取...")

        # 第一步：分析任务，确定搜索策略
        strategy = self._plan_strategy(task)
        print(f"\n📋 搜索策略: {strategy}")

        # 第二步：根据策略执行爬取
        # 这里简化处理，使用预设的起始URL
        start_urls = self._get_start_urls(task)

        for url in start_urls[:self.max_pages]:
            if url in self.visited_urls:
                continue

            print(f"\n🌐 访问: {url}")
            success, html = self.scraper.fetch(url)

            if success:
                self.visited_urls.add(url)
                content = self.scraper.extract_content(html, url)

                if content['success']:
                    self.collected_data.append(content)
                    print(f"✅ 已收集: {content['title']}")

                    # 搜索更多链接
                    links = self.scraper.search_links(html, url)
                    print(f"🔗 发现 {len(links)} 个相关链接")

        # 第三步：汇总报告
        return self._generate_report(task)

    def _plan_strategy(self, task: str) -> str:
        """规划搜索策略"""
        if not self.llm:
            return "演示模式策略"

        prompt = f"""分析以下任务，给出简洁的搜索策略（2-3句话）：

任务: {task}

搜索策略:"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except:
            return "直接搜索相关信息"

    def _get_start_urls(self, task: str) -> List[str]:
        """根据任务获取起始URL"""
        # 预设一些常用网站
        url_mapping = {
            "python": [
                "https://docs.python.org/zh-cn/3/",
                "https://www.python.org/",
            ],
            "langchain": [
                "https://python.langchain.com/",
            ],
            "ai": [
                "https://www.tensorflow.org/",
                "https://pytorch.org/",
            ],
        }

        # 根据关键词匹配
        task_lower = task.lower()
        urls = []

        for keyword, keyword_urls in url_mapping.items():
            if keyword in task_lower:
                urls.extend(keyword_urls)

        # 默认URL
        if not urls:
            urls = ["https://www.example.com/"]

        return urls

    def _analyze_content(self, task: str, content: Dict[str, Any]) -> str:
        """使用AI分析内容"""
        if not self.llm:
            return self._format_content(content)

        prompt = f"""基于以下网页内容，回答用户的任务需求。

用户任务: {task}

网页标题: {content['title']}
网页URL: {content['url']}

内容:
{content['content'][:2000]}

请提取关键信息，以结构化方式回答。"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            return f"分析失败: {e}\n\n原始内容:\n{self._format_content(content)}"

    def _generate_report(self, task: str) -> str:
        """生成汇总报告"""
        if not self.collected_data:
            return "未收集到任何数据"

        print(f"\n{'='*60}")
        print("📊 生成汇总报告...")
        print(f"{'='*60}")

        # 构建报告
        report = f"""# 信息收集报告

## 任务
{task}

## 收集概况
- 访问页面数: {len(self.visited_urls)}
- 成功收集: {len(self.collected_data)} 条

## 来源列表
"""

        for i, data in enumerate(self.collected_data, 1):
            report += f"{i}. [{data['title']}]({data['url']})\n"

        report += "\n## 详细内容\n"

        for i, data in enumerate(self.collected_data, 1):
            report += f"\n### {i}. {data['title']}\n"
            report += f"URL: {data['url']}\n\n"
            content_preview = data['content'][:500] + "..." if len(data['content']) > 500 else data['content']
            report += f"{content_preview}\n"

        # 如果有AI，生成智能摘要
        if self.llm:
            summary = self._generate_summary()
            report += f"\n## AI摘要\n{summary}\n"

        return report

    def _generate_summary(self) -> str:
        """生成AI摘要"""
        if not self.llm or not self.collected_data:
            return ""

        # 收集所有内容
        all_content = "\n\n".join([
            f"标题: {d['title']}\n内容: {d['content'][:300]}"
            for d in self.collected_data
        ])

        prompt = f"""基于以下收集到的信息，给出简洁的摘要（3-5点关键发现）：

{all_content[:2000]}

关键发现:"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except:
            return "摘要生成失败"

    def _format_content(self, content: Dict[str, Any]) -> str:
        """格式化内容（无AI时使用）"""
        return f"""标题: {content['title']}
URL: {content['url']}
段落数: {content['paragraphs_count']}

内容预览:
{content['content'][:500]}..."""

    def _demo_run(self, task: str) -> str:
        """演示模式"""
        print("\n【演示模式】")
        print("模拟爬虫Agent工作流程:")
        print("1. 分析任务需求")
        print("2. 规划搜索策略")
        print("3. 访问目标网页")
        print("4. 提取关键信息")
        print("5. 生成汇总报告")

        # 模拟数据
        demo_data = {
            "title": "Python官方文档",
            "url": "https://docs.python.org/zh-cn/3/",
            "content": "Python是一种解释型、面向对象、动态数据类型的高级程序设计语言...",
        }

        return f"""# 演示模式报告

## 任务
{task}

## 模拟收集结果
- 访问页面: 3个
- 收集信息: 2条

## 示例数据
标题: {demo_data['title']}
URL: {demo_data['url']}
内容: {demo_data['content']}

【提示】设置 DASHSCOPE_API_KEY 以使用真实爬虫功能
"""


# ========== 批量爬虫Agent ==========

class BatchScraperAgent:
    """批量爬虫Agent - 同时处理多个URL"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.scraper = WebScraper()

    def scrape_urls(self, urls: List[str], extract_pattern: str = "") -> List[Dict[str, Any]]:
        """
        批量爬取URL列表

        Args:
            urls: URL列表
            extract_pattern: 提取内容的正则模式

        Returns:
            爬取结果列表
        """
        print(f"\n{'='*60}")
        print(f"🕷️ 批量爬取 {len(urls)} 个URL")
        print(f"{'='*60}")

        results = []

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 处理: {url}")

            success, html = self.scraper.fetch(url)
            if success:
                content = self.scraper.extract_content(html, url)
                if content['success']:
                    # 如果指定了提取模式，进行额外提取
                    if extract_pattern:
                        matches = re.findall(extract_pattern, html)
                        content['extracted'] = matches

                    results.append(content)
                    print(f"✅ 成功: {content['title']}")
                else:
                    print(f"❌ 解析失败")
            else:
                print(f"❌ 获取失败: {html}")

        print(f"\n📊 完成: 成功 {len(results)}/{len(urls)}")
        return results

    def save_results(self, results: List[Dict[str, Any]], filename: str = "scraped_results.json"):
        """保存结果到JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 结果已保存: {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")


# ========== 交互式演示 ==========

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("🕷️ Day 17: 网页爬虫Agent - 自主信息收集")
    print("=" * 60)
    print("1. 爬虫Agent - 自主爬取")
    print("2. 批量爬取 - 多个URL")
    print("3. 从指定URL开始")
    print("4. 查看爬虫工具说明")
    print("5. 退出")
    print("=" * 60)


def show_tools():
    """显示工具说明"""
    print("\n" + "=" * 60)
    print("🔧 爬虫Agent工具说明")
    print("=" * 60)
    print("""
1. fetch(url) - 获取网页内容
   • 自动处理重试和错误
   • 支持超时和延迟

2. extract_content(html, url) - 提取关键信息
   • 提取标题、正文、链接、图片
   • 自动清理脚本和样式

3. search_links(html, base_url, keyword) - 搜索链接
   • 查找包含关键词的链接
   • 自动补全相对URL

Agent工作流程:
  1. 分析用户需求
  2. 规划搜索策略
  3. 访问目标页面
  4. 提取关键信息
  5. 发现相关链接
  6. 生成汇总报告
""")


def main():
    """主程序"""
    print("=" * 60)
    print("🕷️ Day 17: 网页爬虫Agent - 自主信息收集")
    print("=" * 60)
    print("\n核心思想：让AI Agent自主浏览网页、提取信息")
    print("• 分析需求 → 规划策略 → 爬取页面 → 汇总报告")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示: 设置 DASHSCOPE_API_KEY 以使用完整AI功能")
        key = input("请输入API密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    # 初始化Agent
    agent = WebScraperAgent(api_key)
    batch_agent = BatchScraperAgent(api_key)

    while True:
        show_menu()
        choice = input("\n请选择 (1-5): ").strip()

        if choice == '1':
            task = input("\n请输入爬取任务（如'搜集Python学习资源'）: ").strip()
            if task:
                result = agent.run(task)
                print("\n" + "=" * 60)
                print("📋 爬取结果:")
                print("=" * 60)
                print(result)

        elif choice == '2':
            print("\n请输入URL列表（每行一个，输入空行结束）:")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)

            if urls:
                results = batch_agent.scrape_urls(urls)
                batch_agent.save_results(results)

                # 显示摘要
                print("\n📊 爬取摘要:")
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r['title']} - {r['url']}")

        elif choice == '3':
            url = input("\n请输入起始URL: ").strip()
            task = input("请输入任务描述: ").strip()
            if url and task:
                result = agent.run(task, start_url=url)
                print("\n" + "=" * 60)
                print("📋 爬取结果:")
                print("=" * 60)
                print(result)

        elif choice == '4':
            show_tools()

        elif choice == '5':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
