# 📝 Day 5: Python错误处理与日志 - 网页爬虫

**学习日期**: 2026-05-01  
**项目**: 网页爬虫（Web Scraper）  
**预计时间**: 15分钟实践 + 20分钟理论学习

---

## 🎯 今天学到的内容

### 1. 异常处理进阶

#### ✅ try-except-else-finally 完整结构

```python
try:
    # 可能出错的代码
    result = 10 / 0
except ZeroDivisionError:
    # 捕获特定异常
    print("除数不能为0")
except Exception as e:
    # 捕获其他所有异常
    print(f"发生错误: {e}")
else:
    # 没有异常时执行
    print("计算成功")
finally:
    # 无论有无异常都执行
    print("清理资源")
```

**执行流程**：
- 出错 → 执行 except → 执行 finally
- 没出错 → 执行 else → 执行 finally

#### ✅ 捕获多个异常

```python
try:
    # 网络请求
    response = requests.get(url, timeout=5)
    data = response.json()
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.ConnectionError:
    print("连接失败")
except json.JSONDecodeError:
    print("JSON解析失败")
```

#### ✅ 获取异常信息

```python
try:
    int("abc")
except ValueError as e:
    print(f"错误类型: {type(e).__name__}")  # ValueError
    print(f"错误信息: {e}")                  # invalid literal for int()
```

---

### 2. 自定义异常

#### ✅ 创建自定义异常类

```python
# 继承Exception创建自定义异常
class WebScraperError(Exception):
    """爬虫异常基类"""
    pass

class NetworkError(WebScraperError):
    """网络相关错误"""
    pass

class ParseError(WebScraperError):
    """解析相关错误"""
    pass

# 使用自定义异常
def fetch_page(url):
    if not url.startswith('http'):
        raise NetworkError(f"无效的URL: {url}")
    # ...
```

**为什么要自定义异常？**
- 更清晰的错误分类
- 调用者可以精确捕获
- 代码可读性更好

---

### 3. 日志模块 logging

#### ✅ 基础配置

```python
import logging

# 基础配置
logging.basicConfig(
    level=logging.INFO,  # 记录INFO及以上级别
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 使用日志
logger.debug("调试信息")    # 最详细
logger.info("普通信息")     # 一般信息
logger.warning("警告")      # 需要注意
logger.error("错误")        # 发生错误
logger.critical("严重错误") # 系统崩溃
```

#### ✅ 日志级别

| 级别 | 数值 | 用途 |
|------|------|------|
| DEBUG | 10 | 调试细节 |
| INFO | 20 | 正常运行信息 |
| WARNING | 30 | 警告，但程序继续 |
| ERROR | 40 | 错误，功能受影响 |
| CRITICAL | 50 | 严重错误，程序可能终止 |

**规则**：设置 `level=INFO` 后，只有 INFO 及以上级别（WARNING、ERROR、CRITICAL）会被记录。

#### ✅ 同时输出到文件和屏幕

```python
import logging
import os

# 创建日志目录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),  # 写入文件
        logging.StreamHandler()                                  # 输出屏幕
    ]
)
```

---

### 4. 重试机制

#### ✅ 简单的重试逻辑

```python
def fetch_with_retry(url, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=5)
            return response
        except requests.exceptions.Timeout:
            if attempt == max_retries:
                raise  # 最后一次也失败，抛出异常
            print(f"第{attempt}次超时，重试...")
            time.sleep(2)  # 等待后重试
```

#### ✅ 指数退避（Exponential Backoff）

```python
import time

for attempt in range(1, max_retries + 1):
    try:
        response = requests.get(url)
        break  # 成功，跳出循环
    except:
        wait_time = 2 ** attempt  # 2, 4, 8秒...
        print(f"等待{wait_time}秒后重试...")
        time.sleep(wait_time)
```

---

### 5. BeautifulSoup 网页解析

#### ✅ 安装和导入

```bash
pip install beautifulsoup4
```

```python
from bs4 import BeautifulSoup

# 解析HTML
soup = BeautifulSoup(html, 'html.parser')
```

#### ✅ 常用解析方法

```python
# 获取标题
title = soup.title.string

# 查找所有段落
paragraphs = soup.find_all('p')
for p in paragraphs:
    text = p.get_text(strip=True)

# 查找所有链接
links = soup.find_all('a', href=True)
for a in links:
    url = a['href']
    text = a.get_text(strip=True)

# 查找特定class
divs = soup.find_all('div', class_='content')

# 查找特定id
element = soup.find(id='header')
```

---

## 🛠️ 实战项目：网页爬虫

### 项目功能

✅ **网页爬取** - 发送HTTP请求获取网页内容  
✅ **错误处理** - 网络超时、连接失败、状态码错误  
✅ **重试机制** - 失败自动重试，指数退避  
✅ **HTML解析** - 提取标题、段落、链接、图片  
✅ **日志记录** - 完整记录运行过程  
✅ **自定义异常** - 清晰的错误分类  
✅ **演示模式** - 无需网络即可运行

### 核心代码结构

```python
import logging
import requests
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScraperError(Exception):
    pass

class NetworkError(WebScraperError):
    pass

class WebScraper:
    def __init__(self, delay=1, timeout=10, max_retries=3):
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
    
    def fetch_page(self, url):
        """获取页面，带重试"""
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    return response.text
                else:
                    raise NetworkError(f"HTTP {response.status_code}")
            except requests.exceptions.Timeout:
                if attempt == self.max_retries:
                    raise NetworkError("超时")
                time.sleep(attempt * 2)
    
    def parse_html(self, html, url):
        """解析HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        return {
            'title': soup.title.string if soup.title else '无标题',
            'paragraphs': [p.get_text(strip=True) for p in soup.find_all('p')],
            'links': [{'text': a.get_text(), 'url': a['href']} for a in soup.find_all('a', href=True)]
        }
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 运行程序
python day05_web_scraper.py
```

**操作提示**：
- 输入URL爬取真实网页
- 输入 `demo` 使用演示模式（无需网络）
- 输入 `quit` 退出

---

## 📊 错误处理流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   发送请求   │────▶│  是否成功？  │────▶│  解析内容    │
│             │     │             │     │             │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌────────┐  ┌────────┐  ┌────────┐
         │ 超时    │  │ 连接失败│  │ 状态码错误│
         │ 重试    │  │ 重试    │  │ 记录日志  │
         │ 3次后放弃│  │ 3次后放弃│  │ 跳过     │
         └────────┘  └────────┘  └────────┘
```

---

## 🎓 关键知识点总结

### 异常处理结构

| 结构 | 作用 |
|------|------|
| `try` | 包裹可能出错的代码 |
| `except` | 捕获并处理异常 |
| `else` | 没有异常时执行 |
| `finally` | 无论有无异常都执行 |
| `raise` | 主动抛出异常 |

### 日志级别使用场景

| 级别 | 使用场景 |
|------|----------|
| DEBUG | 变量值、函数调用细节 |
| INFO | 程序启动、操作完成 |
| WARNING | 配置缺失、性能下降 |
| ERROR | 功能失败、请求错误 |
| CRITICAL | 系统崩溃、数据丢失 |

### BeautifulSoup常用方法

| 方法 | 作用 |
|------|------|
| `soup.find(tag)` | 查找第一个匹配标签 |
| `soup.find_all(tag)` | 查找所有匹配标签 |
| `element.get_text()` | 获取标签文本内容 |
| `element['attr']` | 获取属性值 |
| `soup.select(css)` | CSS选择器查找 |

---

## 💡 今天的难点解析

### 难点1：什么时候用自定义异常？

```python
# 不推荐：直接返回错误信息
def fetch(url):
    if not url.startswith('http'):
        return "错误：URL无效"  # 调用者需要判断返回值类型

# 推荐：抛出异常
def fetch(url):
    if not url.startswith('http'):
        raise NetworkError("URL无效")  # 调用者用try-except捕获
```

**原则**：错误情况用异常，正常结果用返回值。

### 难点2：日志和print的区别

| | print | logging |
|--|-------|---------|
| 输出目标 | 屏幕 | 文件+屏幕 |
| 级别控制 | 无 | 有 |
| 时间戳 | 无 | 有 |
| 生产环境 | 不合适 | 推荐 |

### 难点3：重试的注意事项

```python
# 错误：立即重试
except Timeout:
    fetch()  # 服务器还没恢复，大概率又失败

# 正确：等待后重试
except Timeout:
    time.sleep(2)  # 给服务器恢复时间
    fetch()
```

---

## 🧪 动手实验

### 实验1：自定义异常
```python
class ValidationError(Exception):
    pass

def validate_age(age):
    if not isinstance(age, int):
        raise ValidationError("年龄必须是整数")
    if age < 0 or age > 150:
        raise ValidationError("年龄范围错误")
    return True

# 测试
try:
    validate_age(200)
except ValidationError as e:
    print(f"验证失败: {e}")
```

### 实验2：日志记录
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("myapp")

logger.info("程序启动")
logger.debug("配置加载完成")
logger.warning("配置文件缺失，使用默认配置")
```

### 实验3：解析本地HTML
```python
from bs4 import BeautifulSoup

html = """
<html>
<body>
    <h1>标题</h1>
    <p class="content">第一段</p>
    <p class="content">第二段</p>
    <a href="https://example.com">链接</a>
</body>
</html>
"""

soup = BeautifulSoup(html, 'html.parser')
print(soup.h1.get_text())  # 标题
for p in soup.find_all('p', class_='content'):
    print(p.get_text())
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- try-except-else-finally 完整结构
- 自定义异常类
- logging 日志配置和使用
- 重试机制设计
- BeautifulSoup 网页解析

### 🤔 理解难点
- 自定义异常让错误处理更清晰
- 日志比 print 更适合生产环境
- 重试需要等待时间，不能立即重试

### 🚀 实践成果
- ✅ 完成了带完整错误处理的网页爬虫
- ✅ 实现了自动重试机制
- ✅ 配置了日志记录到文件和屏幕
- ✅ 学会了解析HTML提取数据

---

## 📚 扩展阅读

### 异常处理
- [官方文档 - 异常](https://docs.python.org/zh-cn/3/tutorial/errors.html)

### 日志模块
- [logging 官方文档](https://docs.python.org/zh-cn/3/library/logging.html)

### BeautifulSoup
- [BeautifulSoup 文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

## 🎯 明日预告：OOP项目 - 图书管理系统

**将学习**:
- 类的继承和多态
- 更复杂的类设计
- 数据持久化（JSON）
- 完整的CRUD操作

**项目**: 简易图书管理系统

---

## 💭 学习心得

> "今天学习了错误处理和日志，这是写出'健壮'程序的关键。
>
> 以前写代码只考虑正常情况，现在学会了：
> - 网络可能超时 → 加try-except
> - 服务器可能失败 → 加重试
> - 需要排查问题 → 加日志
>
> 爬虫程序最能体现这些技能，因为网络环境最不可控。
>
> 明天要学习OOP项目设计，期待能做出更复杂的程序！"

---

**完整代码**: [`day05_web_scraper.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day05_web_scraper.py)  
**日志文件**: `logs/scraper_YYYYMMDD.log`

---

<div align="center">
  <p>⭐ Day 5 完成！继续加油！ ⭐</p>
  <p><em>"好的程序不是不出错，而是出错后能优雅处理。"</em></p>
</div>
