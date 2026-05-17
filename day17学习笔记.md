# 📝 Day 17: 网页爬虫Agent - 自主信息收集

**学习日期**: 2026-05-15  
**项目**: 网页爬虫Agent  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 3进阶，学习Agent自主收集网络信息

---

## 🎯 今天学到的内容

### 1. 什么是爬虫Agent？

**传统爬虫**：
- 程序员写死规则（爬哪些URL、提取哪些字段）
- 只能处理预设的网站结构
- 遇到变化需要人工修改代码

**爬虫Agent**：
- Agent自主决定爬取策略
- 智能分析页面内容，动态调整
- 能理解用户需求，针对性收集信息
- 自动汇总和整理结果

**类比**：传统爬虫像"按图索骥"，爬虫Agent像"智能探险家"。

---

### 2. 爬虫Agent架构

#### ✅ 核心组件

```
┌─────────────────────────────────────────┐
│           爬虫Agent系统                  │
│                                         │
│  ┌─────────┐    ┌─────────────────┐    │
│  │ 策略规划 │───▶│   网页爬虫工具   │    │
│  │ (LLM)   │    │  (Scraper)      │    │
│  └─────────┘    └────────┬────────┘    │
│       ▲                  │             │
│       │                  ▼             │
│  ┌────┴────┐    ┌─────────────────┐    │
│  │ 结果汇总 │◀───│  内容提取与分析  │    │
│  │ (LLM)   │    │  (Extractor)    │    │
│  └─────────┘    └─────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

#### ✅ 工作流程

```
用户: "帮我搜集Python学习资源"

1. 策略规划
   Agent思考: 用户需要Python学习资源
   → 应该访问Python官网、教程网站、GitHub等

2. 页面爬取
   → 访问 https://docs.python.org/zh-cn/3/
   → 获取HTML内容

3. 内容提取
   → 提取标题、正文、链接
   → 发现"教程"、"文档"、"示例"等关键词

4. 深入探索
   → 发现相关链接
   → 继续访问更多页面

5. 结果汇总
   → 整理所有收集到的信息
   → 生成结构化报告
```

---

### 3. 爬虫工具设计

#### ✅ 工具函数

```python
class WebScraper:
    def fetch(self, url: str) -> Tuple[bool, str]:
        """获取网页内容"""
        # 发送HTTP请求
        # 处理重试和错误
        # 返回 (成功标志, HTML内容)

    def extract_content(self, html: str, url: str) -> Dict:
        """提取网页关键信息"""
        # 解析HTML
        # 提取标题、正文、链接、图片
        # 返回结构化数据

    def search_links(self, html: str, base_url: str, keyword: str = "") -> List[Dict]:
        """搜索包含关键词的链接"""
        # 解析所有链接
        # 过滤匹配关键词的链接
        # 返回链接列表
```

#### ✅ 错误处理

```python
# 网络错误处理
try:
    response = requests.get(url, timeout=10)
except requests.exceptions.Timeout:
    return False, "请求超时"
except requests.exceptions.ConnectionError:
    return False, "连接失败"

# 状态码处理
if response.status_code == 200:
    return True, response.text
elif response.status_code == 404:
    return False, "页面不存在"
elif response.status_code == 403:
    return False, "访问被拒绝"
```

---

### 4. 自主爬取策略

#### ✅ 策略规划

```python
def plan_strategy(self, task: str) -> str:
    """让AI规划搜索策略"""
    prompt = f"""分析以下任务，给出简洁的搜索策略：

任务: {task}

搜索策略:"""

    response = llm.invoke(prompt)
    return response.content
```

#### ✅ URL选择

```python
def get_start_urls(self, task: str) -> List[str]:
    """根据任务选择起始URL"""
    url_mapping = {
        "python": [
            "https://docs.python.org/zh-cn/3/",
            "https://www.python.org/",
        ],
        "langchain": [
            "https://python.langchain.com/",
        ],
    }

    # 根据关键词匹配
    for keyword, urls in url_mapping.items():
        if keyword in task.lower():
            return urls

    return ["https://www.example.com/"]
```

---

### 5. 内容提取与整理

#### ✅ 使用BeautifulSoup提取内容

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')

# 移除不需要的元素
for script in soup(["script", "style"]):
    script.decompose()

# 提取标题
title = soup.title.string if soup.title else "无标题"

# 提取正文
paragraphs = []
for p in soup.find_all(['p', 'article', 'section']):
    text = p.get_text(strip=True)
    if len(text) > 20:
        paragraphs.append(text)

# 提取链接
links = []
for a in soup.find_all('a', href=True):
    links.append({
        'text': a.get_text(strip=True),
        'url': urljoin(base_url, a['href'])
    })
```

#### ✅ AI分析内容

```python
def analyze_content(self, task: str, content: Dict) -> str:
    """使用AI分析提取的内容"""
    prompt = f"""基于以下网页内容，回答用户的任务需求。

用户任务: {task}
网页标题: {content['title']}

内容:
{content['content'][:2000]}

请提取关键信息，以结构化方式回答。"""

    response = llm.invoke(prompt)
    return response.content
```

---

### 6. 批量爬虫

#### ✅ 批量处理多个URL

```python
class BatchScraperAgent:
    def scrape_urls(self, urls: List[str]) -> List[Dict]:
        results = []

        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] 处理: {url}")

            success, html = self.scraper.fetch(url)
            if success:
                content = self.scraper.extract_content(html, url)
                if content['success']:
                    results.append(content)
                    print(f"✅ 成功: {content['title']}")

        return results
```

---

## 🛠️ 实战项目：网页爬虫Agent

### 项目功能

✅ **自主爬取** - Agent自主决定爬取策略  
✅ **内容提取** - 提取标题、正文、链接、图片  
✅ **智能分析** - 使用AI分析提取的内容  
✅ **批量处理** - 同时处理多个URL  
✅ **错误处理** - 完善的网络和解析错误处理  
✅ **结果汇总** - 生成结构化报告  
✅ **演示模式** - 无API密钥也能体验  

### 核心代码结构

```python
class WebScraperAgent:
    def __init__(self, api_key=None, max_pages=5):
        self.scraper = WebScraper()
        self.llm = ChatOpenAI(...)

    def run(self, task: str, start_url=None):
        """运行爬虫Agent"""
        if start_url:
            return self._crawl_from_url(task, start_url)
        return self._autonomous_crawl(task)

    def _plan_strategy(self, task: str) -> str:
        """规划搜索策略"""

    def _get_start_urls(self, task: str) -> List[str]:
        """获取起始URL"""

    def _generate_report(self, task: str) -> str:
        """生成汇总报告"""
```

### 运行方式

```bash
python day17_web_scraper_agent.py
```

---

## 💡 今天的难点解析

### 难点1：反爬虫机制

```python
# 问题：网站可能阻止爬虫
# 解决：
# 1. 设置合理的User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 2. 控制请求频率
time.sleep(1)  # 每次请求间隔1秒

# 3. 处理重试
for attempt in range(max_retries):
    try:
        response = requests.get(url)
        break
    except:
        time.sleep(attempt * 2)
```

### 难点2：动态内容

```python
# 问题：现代网站使用JavaScript渲染内容
# 解决：
# 1. 使用Selenium或Playwright
# 2. 寻找API接口
# 3. 分析JavaScript代码找数据源
```

### 难点3：内容去重

```python
# 问题：多个页面可能包含重复内容
# 解决：
# 1. URL去重
visited_urls = set()

# 2. 内容哈希去重
import hashlib
def content_hash(text):
    return hashlib.md5(text.encode()).hexdigest()
```

---

## 🧪 动手实验

### 实验1：添加新网站

```python
# 在get_start_urls中添加新网站
def get_start_urls(self, task: str) -> List[str]:
    url_mapping = {
        "python": [
            "https://docs.python.org/zh-cn/3/",
            "https://realpython.com/",  # 新增
        ],
    }
```

### 实验2：自定义提取规则

```python
# 提取特定内容
def extract_specific(self, html: str, selector: str) -> List[str]:
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.select(selector)
    return [e.get_text(strip=True) for e in elements]

# 使用
results = extract_specific(html, "h2.title")
```

### 实验3：保存到不同格式

```python
# 保存为CSV
import csv

def save_to_csv(results, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'url', 'content'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- 爬虫Agent的核心概念和工作流程
- 自主爬取策略的规划
- 网页内容提取技术（BeautifulSoup）
- 批量爬虫的实现
- 错误处理和反爬虫应对

### 🤔 理解难点
- 爬虫Agent不是简单的"自动点击"，而是有策略的信息收集
- 策略规划是核心——决定访问哪些页面、提取什么信息
- 错误处理很重要——网络不稳定是常态
- 尊重网站的robots.txt和访问频率限制

### 🚀 实践成果
- ✅ 实现了爬虫Agent系统
- ✅ 支持自主爬取和批量爬取
- ✅ 集成了内容提取和AI分析
- ✅ 实现了结果汇总报告

---

## 📚 扩展阅读

### 爬虫框架
- [Scrapy](https://scrapy.org/) - Python爬虫框架
- [Selenium](https://www.selenium.dev/) - 浏览器自动化
- [Playwright](https://playwright.dev/) - 现代浏览器自动化

### 反爬虫应对
- [爬虫与反爬虫](https://github.com/wangshub/webdriver)
- [User-Agent列表](https://www.useragentstring.com/)

---

## 🎯 明日预告：代码生成Agent

**将学习**:
- 让Agent自动生成代码
- 代码审查和优化
- AI编程助手

**项目**: 代码生成Agent

---

## 💭 学习心得

> "Day 17学习了网页爬虫Agent，这是让AI能够自主获取信息的开始。
>
> 最大的感悟：信息收集是AI Agent的基础能力，没有信息输入，Agent就无法做出正确决策。
>
> 几个重要的领悟：
> 1. 策略规划是灵魂 → Agent需要知道"去哪里找"
> 2. 内容提取是技术 → 从HTML中提炼有用信息
> 3. 错误处理是保障 → 网络世界充满不确定性
> 4. 汇总报告是价值 → 将原始数据转化为洞察
>
> 明天学习代码生成Agent，让AI能写代码！"

---

**完整代码**: [`day17_web_scraper_agent.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day17_web_scraper_agent.py)

---

<div align="center">
  <p>⭐ Day 17 完成！AI会爬网页了！⭐</p>
  <p><em>"信息就是力量，爬虫就是获取力量的工具。"</em></p>
</div>
