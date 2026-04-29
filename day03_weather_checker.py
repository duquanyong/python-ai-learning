"""
Day 3 Project: 天气查询工具
功能：调用真实天气API，查询城市天气信息
作者：duquanyong
日期：2026-04-29
"""
import requests
import json
from datetime import datetime


class WeatherChecker:
    """天气查询工具"""
    
    def __init__(self, api_key=""):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.last_query = None
    
    def get_weather(self, city):
        """查询指定城市的天气"""
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                weather_data = response.json()
                self.last_query = weather_data
                return self._format_weather(weather_data)
            elif response.status_code == 404:
                return f"❌ 未找到城市: {city}"
            elif response.status_code == 401:
                return "❌ API密钥无效"
            else:
                return f"❌ 请求失败，状态码: {response.status_code}"
        
        except requests.exceptions.Timeout:
            return "❌ 请求超时"
        except requests.exceptions.ConnectionError:
            return "❌ 网络连接失败"
        except Exception as e:
            return f"❌ 发生错误: {e}"
    
    def _format_weather(self, data):
        """格式化天气数据"""
        city = data['name']
        country = data['sys']['country']
        temperature = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        
        return f"""
{'='*50}
🌤️  天气信息 - {city}, {country}
{'='*50}
🌡️  温度: {temperature}°C
🤔 体感温度: {feels_like}°C
📝 天气: {description}
💧 湿度: {humidity}%
💨 风速: {wind_speed} m/s
🕐 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}
"""


def demo_mode():
    """演示模式"""
    print("\n" + "="*50)
    print("🎭 演示模式 - 模拟天气数据")
    print("="*50)
    
    cities = {
        "beijing": {"name": "北京", "country": "CN", "temp": 22, "feels_like": 20, "description": "晴朗", "humidity": 45, "wind": 3.5},
        "shanghai": {"name": "上海", "country": "CN", "temp": 25, "feels_like": 27, "description": "多云", "humidity": 70, "wind": 2.0},
        "shenzhen": {"name": "深圳", "country": "CN", "temp": 28, "feels_like": 30, "description": "阴天", "humidity": 80, "wind": 1.5}
    }
    
    print("\n可用城市: Beijing, Shanghai, Shenzhen")
    city = input("请输入城市名: ").strip().lower()
    
    if city in cities:
        data = cities[city]
        print(f"""
{'='*50}
🌤️  天气信息 - {data['name']}, {data['country']}
{'='*50}
🌡️  温度: {data['temp']}°C
🤔 体感温度: {data['feels_like']}°C
📝 天气: {data['description']}
💧 湿度: {data['humidity']}%
💨 风速: {data['wind']} m/s
🕐 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}
""")
    else:
        print(f"❌ 演示模式不支持城市: {city}")


def main():
    """主程序"""
    print("="*50)
    print("🌤️  天气查询工具 - Day 3 学习成果")
    print("="*50)
    
    print("\n📝 说明：")
    print("1. 按回车使用演示模式（模拟数据）")
    print("2. 输入API密钥使用真实天气数据")
    print("3. 获取密钥: https://openweathermap.org/\n")
    
    api_key = input("请输入OpenWeather API密钥（或回车使用演示模式）: ").strip()
    
    if not api_key:
        demo_mode()
        return
    
    # 使用真实API
    checker = WeatherChecker(api_key)
    
    while True:
        print("\n" + "-"*50)
        print("🔧 操作菜单:")
        print("1. 查询天气")
        print("2. 退出")
        print("-"*50)
        
        choice = input("\n请选择操作 (1-2): ").strip()
        
        if choice == '1':
            city = input("请输入城市名（如: Beijing）: ").strip()
            if city:
                result = checker.get_weather(city)
                print(result)
        elif choice == '2':
            print("\n👋 再见！明天继续学习！")
            break
        else:
            print("❌ 无效的选择！")


if __name__ == "__main__":
    main()