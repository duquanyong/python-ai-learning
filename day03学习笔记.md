# 📝 Day 3: Python API调用与网络请求 - 天气查询工具

**学习日期**: 2026-04-29  
**项目**: 天气查询工具（Weather Checker）  
**预计时间**: 10分钟实践 + 15分钟理论学习

---

## 🎯 今天学到的内容

### 1. HTTP请求基础

#### ✅ 什么是API？
API（Application Programming Interface，应用程序接口）是不同软件之间交换数据的方式。通过API，我们可以获取外部服务的数据（如天气、股票、地图等）。

**类比理解**：
API就像餐厅的服务员，你点菜（发送请求），服务员去厨房取餐（服务器处理），然后端给你（返回数据）。🍽️

#### ✅ HTTP请求方法

| 方法 | 作用 | 示例 |
|------|------|------|
| `GET` | 获取数据 | 查询天气信息 |
| `POST` | 提交数据 | 注册用户 |
| `PUT` | 更新数据 | 修改用户信息 |
| `DELETE` | 删除数据 | 删除账户 |

今天主要使用 `GET` 请求获取天气数据。

---

### 2. requests库

#### ✅ 安装与导入

```python
import requests
```

requests是Python最流行的HTTP库，比标准库的urllib更简洁易用。

#### ✅ 发送GET请求

```python
import requests

# 基本GET请求
response = requests.get("https://api.example.com/data")

# 带参数的GET请求
params = {
    "q": "Beijing",      # 城市名
    "appid": "your_key", # API密钥
    "units": "metric",   # 摄氏度
    "lang": "zh_cn"      # 中文语言
}
response = requests.get(url, params=params, timeout=10)
```

#### ✅ 处理响应

```python
# 状态码
print(response.status_code)  # 200成功, 404未找到, 401未授权

# 获取JSON数据
data = response.json()

# 获取文本内容
text = response.text
```

**常见HTTP状态码**：

| 状态码 | 含义 | 处理方式 |
|--------|------|----------|
| 200 | 请求成功 | ✅ 正常处理数据 |
| 404 | 资源未找到 | 检查城市名或URL |
| 401 | 未授权 | 检查API密钥 |
| 500 | 服务器错误 | 稍后重试 |

---

### 3. 异常处理进阶

#### ✅ requests专用异常

```python
import requests

try:
    response = requests.get(url, params=params, timeout=10)
    
except requests.exceptions.Timeout:
    print("❌ 请求超时，网络可能不稳定")
    
except requests.exceptions.ConnectionError:
    print("❌ 网络连接失败，检查网络设置")
    
except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP错误: {e}")
    
except Exception as e:
    print(f"❌ 其他错误: {e}")
```

#### ✅ 根据状态码处理不同情况

```python
response = requests.get(url, params=params)

if response.status_code == 200:
    # 成功，处理数据
    data = response.json()
elif response.status_code == 404:
    # 城市不存在
    print("未找到该城市")
elif response.status_code == 401:
    # API密钥错误
    print("API密钥无效")
else:
    # 其他错误
    print(f"请求失败: {response.status_code}")
```

---

### 4. JSON数据解析

#### ✅ 解析嵌套JSON

API返回的JSON通常是嵌套结构，需要逐层访问：

```python
# 示例天气API响应结构
{
    "name": "Beijing",           # 城市名
    "sys": {
        "country": "CN"           # 国家代码
    },
    "main": {
        "temp": 22,               # 温度
        "feels_like": 20,         # 体感温度
        "humidity": 45            # 湿度
    },
    "weather": [
        {"description": "晴朗"}    # 天气描述
    ],
    "wind": {
        "speed": 3.5              # 风速
    }
}
```

```python
# 逐层访问嵌套数据
city = data['name']                           # 第一层
country = data['sys']['country']              # 第二层
temperature = data['main']['temp']            # 第二层
description = data['weather'][0]['description']  # 列表+字典
wind_speed = data['wind']['speed']            # 第二层
```

#### ✅ 安全访问（避免KeyError）

```python
# 方式1：使用get()方法
city = data.get('name', '未知城市')

# 方式2：使用try-except
try:
    humidity = data['main']['humidity']
except KeyError:
    humidity = None
```

---

### 5. 类方法设计

#### ✅ 私有方法（约定俗成）

```python
class WeatherChecker:
    def get_weather(self, city):
        """公共方法：对外提供的接口"""
        response = requests.get(...)
        data = response.json()
        return self._format_weather(data)  # 调用私有方法
    
    def _format_weather(self, data):
        """私有方法：内部使用，格式化数据"""
        # 下划线开头表示"建议内部使用"
        return f"温度: {data['main']['temp']}°C"
```

**命名约定**：
- 单下划线 `_method()`：提示为内部方法，但外部仍可访问
- 双下划线 `__method()`：Python名称修饰，强制私有（不推荐过度使用）

---

### 6. 演示模式设计

#### ✅ 无网络也能运行的程序

```python
def demo_mode():
    """演示模式 - 使用模拟数据"""
    cities = {
        "beijing": {"name": "北京", "temp": 22, ...},
        "shanghai": {"name": "上海", "temp": 25, ...}
    }
    # 不调用真实API，使用本地数据
```

**设计思路**：
1. 用户没有API密钥时，提供演示模式
2. 有API密钥时，调用真实数据
3. 两种模式保持相同的输出格式

---

## 🛠️ 实战项目：天气查询工具

### 项目功能

✅ **查询天气** - 输入城市名获取实时天气  
✅ **演示模式** - 无需API密钥，使用模拟数据  
✅ **真实API** - 支持OpenWeatherMap API  
✅ **错误处理** - 网络超时、城市不存在、密钥无效等  
✅ **格式化输出** - 美观的天气信息展示

### 核心代码结构

```python
import requests

class WeatherChecker:
    def __init__(self, api_key=""):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city):
        """查询指定城市的天气"""
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",    # 摄氏度
            "lang": "zh_cn"       # 中文
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                return self._format_weather(response.json())
            elif response.status_code == 404:
                return "❌ 未找到城市"
            elif response.status_code == 401:
                return "❌ API密钥无效"
                
        except requests.exceptions.Timeout:
            return "❌ 请求超时"
        except requests.exceptions.ConnectionError:
            return "❌ 网络连接失败"
    
    def _format_weather(self, data):
        """格式化天气数据为可读文本"""
        return f"""
🌤️  {data['name']}
🌡️  温度: {data['main']['temp']}°C
💧 湿度: {data['main']['humidity']}%
📝 天气: {data['weather'][0]['description']}
"""
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 运行程序
python day03_weather_checker.py

# 演示模式：直接回车
# 真实API：输入OpenWeatherMap API密钥
```

---

## 📊 API请求流程图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户输入   │────▶│  构建请求参数 │────▶│ 发送HTTP请求 │
│  (城市名)    │     │ (params)     │     │ (requests)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                       ┌────────────────────────┘
                       ▼
              ┌─────────────────┐
              │   服务器响应      │
              │  (JSON数据)      │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ 200成功  │  │ 404未找到│  │ 401错误  │
    │解析JSON  │  │提示检查 │  │提示密钥  │
    │格式化输出│  │城市名   │  │错误     │
    └─────────┘  └─────────┘  └─────────┘
```

---

## 🎓 关键知识点总结

### requests库核心方法

| 方法 | 作用 |
|------|------|
| `requests.get(url)` | 发送GET请求 |
| `requests.post(url, data)` | 发送POST请求 |
| `response.status_code` | 获取HTTP状态码 |
| `response.json()` | 解析JSON响应 |
| `response.text` | 获取文本响应 |

### 请求参数

| 参数 | 说明 |
|------|------|
| `params` | URL查询参数（?key=value） |
| `timeout` | 超时时间（秒） |
| `headers` | 请求头信息 |
| `data` | POST请求体数据 |

### 异常处理层次

```
Exception（所有异常的基类）
  ├── requests.exceptions.RequestException
  │     ├── Timeout（超时）
  │     ├── ConnectionError（连接错误）
  │     └── HTTPError（HTTP错误）
  └── 其他Python异常
```

---

## 💡 今天的难点解析

### 难点1：为什么需要API密钥？

API密钥是服务的"身份证"：
- 识别调用者身份
- 限制请求频率（防止滥用）
- 统计使用量
- 收费依据（部分API）

**获取OpenWeatherMap密钥**：
1. 访问 https://openweathermap.org/
2. 注册免费账户
3. 在API Keys页面获取密钥
4. 免费版每分钟最多60次请求

### 难点2：params参数如何变成URL？

```python
params = {"q": "Beijing", "appid": "123", "units": "metric"}

# requests自动转换为：
# https://api.openweathermap.org/data/2.5/weather?q=Beijing&appid=123&units=metric
```

### 难点3：如何处理嵌套JSON？

```python
data = {
    "main": {"temp": 22, "humidity": 45},
    "weather": [{"description": "晴朗"}]
}

# 逐层访问
temp = data["main"]["temp"]           # 22
desc = data["weather"][0]["description"]  # "晴朗"

# 理解结构：
# data["main"] 是字典 → 继续 ["temp"] 取值
# data["weather"] 是列表 → [0] 取第一个元素 → ["description"] 取值
```

---

## 🧪 动手实验

### 实验1：查看原始API响应
```python
import requests

url = "https://api.openweathermap.org/data/2.5/weather"
params = {"q": "Beijing", "appid": "你的密钥", "units": "metric", "lang": "zh_cn"}

response = requests.get(url, params=params)
print(response.status_code)  # 200
print(response.json())       # 查看完整JSON结构
```

### 实验2：测试不同错误情况
```python
# 测试超时（设置很短的时间）
try:
    response = requests.get(url, timeout=0.001)
except requests.exceptions.Timeout:
    print("超时了！")

# 测试错误的城市名
params["q"] = "不存在的城市XYZ"
response = requests.get(url, params=params)
print(response.status_code)  # 404
```

### 实验3：添加更多天气信息
```python
# 在_format_weather中添加更多字段
def _format_weather(self, data):
    pressure = data['main']['pressure']      # 气压
    visibility = data.get('visibility', 0)    # 能见度
    # ...添加到输出中
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- HTTP请求的基本概念（GET、POST、状态码）
- requests库的安装和使用
- 发送带参数的GET请求
- 解析嵌套JSON数据
- 网络请求的异常处理
- API密钥的使用方式

### 🤔 理解难点
- 嵌套JSON的逐层访问方法
- 不同HTTP状态码的含义和处理
- 演示模式 vs 真实API的设计思路

### 🚀 实践成果
- ✅ 完成了天气查询工具
- ✅ 支持演示模式和真实API两种运行方式
- ✅ 实现了完整的错误处理
- ✅ 学会了调用第三方API服务

---

## 📚 扩展阅读

### requests库文档
- [官方文档](https://requests.readthedocs.io/)
- [中文快速入门](https://docs.python-requests.org/zh_CN/latest/user/quickstart.html)

### HTTP协议基础
- [HTTP状态码详解](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status)
- [RESTful API设计](https://restfulapi.net/)

### OpenWeatherMap API
- [官方文档](https://openweathermap.org/api)
- [当前天气API](https://openweathermap.org/current)

---

## 🎯 明日预告：数据分析与可视化

**将学习**:
- pandas库基础
- CSV文件读取与处理
- matplotlib数据可视化
- 数据统计与分析

**项目**: 读取CSV数据，生成统计图表

---

## 💭 学习心得

> "今天第一次让Python连接到了真实的世界！通过API获取天气数据，感觉程序突然有了'眼睛'和'耳朵'。
>
> 最惊喜的是requests库的简洁——一行代码就能发送HTTP请求，比我想象的简单多了。
>
> 异常处理也很重要，网络不稳定、城市名输错、API密钥过期...各种情况都要考虑到，这是写出健壮程序的关键。
>
> 明天要学习pandas和matplotlib，期待能用Python画出漂亮的图表！"

---

**完整代码**: [`day03_weather_checker.py`](./day03_weather_checker.py)  
**API文档**: https://openweathermap.org/api

---

<div align="center">
  <p>⭐ Day 3 完成！继续加油！ ⭐</p>
  <p><em>"让程序连接世界，数据就在指尖。"</em></p>
</div>
