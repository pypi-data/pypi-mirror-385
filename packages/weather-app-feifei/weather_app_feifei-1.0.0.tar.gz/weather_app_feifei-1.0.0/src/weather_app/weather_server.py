#构建mcpserver
#导入依赖包
import json
import httpx
import os
from typing import Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

#OpenWeather API配置
mcp = FastMCP("WeatherServer")
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5/weather"
# 从环境变量读取API密钥，如果不存在则使用默认值
API_KEY = os.getenv("OPENWEATHER_API_KEY")
USER_AGENT = "weather-app/1.0"
#定义一个查询天气的异步函数，用于向网站请求城市的天气信息，并对可能出现的异常进行处理
async def query_weather(city: str) -> dict[str, Any] | None:
    """
    从OpenWeather API查询的天气信息。
    :param city: 城市名称
    :return: 包含天气信息的字典,或error(如果查询失败)
    """
#http请求参数设置
    params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "lang": "zh_cn"
        }
#http请求头设置
    headers = {
            "User-Agent": USER_AGENT
        }
#创建http客户端
    async with httpx.AsyncClient() as client:
        try:
            #发送GET请求查询天气
            response = await client.get(OPENWEATHER_API_BASE, params=params, headers=headers, timeout=30.0)
            #检查响应状态码,不是2xx系列,则抛出异常
            response.raise_for_status()
            #将响应的json数据解析为字典并返回
            return response.json()
        #处理http状态错误(如404等)
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP错误: {e.response.status_code}"}
        #处理其他可能的问题(如网络问题等)
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}
#数据格式化，将网站返回的复杂结构数据转化为用户易读的文本输出
def format_weather_data(data: dict[str, Any] | str) -> str:
    """
    将OpenWeather API返回的天气数据格式化为易读的文本。
    :param data: 天气数据(可以使字典或者json字符串)
    :return: 格式化后的天气信息字符串
    """
    #如果输入是字符串,则先解析为字典
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            return f"无法解析天气数据: {e}"
    #检查是否包含错误信息
    if "error" in data:
        return f"查询天气失败: {data['error']}"
    #提取数据时做容错处理,确保缺少数据也能正常工作
    city = data.get("name", "未知")
    country = data.get("sys", {}).get("country", "未知")
    temp = data.get("main", {}).get("temp", "N/A")
    humidity = data.get("main", {}).get("humidity", "N/A")
    wind_speed = data.get("wind", {}).get("speed", "N/A")
    #weather可能是空列表，因此先提供默认字典
    weather_list = data.get("weather", [{}])
    description = weather_list[0].get("description", "未知")
    #使用f-string格式化输出,确保所有数据都有值
    #格式化输出
    return (
        f"城市: {city} ({country})\n"
        f"天气: {description}\n"
        f"温度: {temp}°C\n"
        f"湿度: {humidity}%\n"
        f"风速: {wind_speed} m/s\n"
    )
#使用mcp装饰器封装query_weather函数为工具，实现天气的查询以及结果的格式化
#使用mcp装饰器将其标记为一个工具
@mcp.tool()
#定义一个异步函数并声明其用途
async def query_weather_mcp(city: str) -> str:
    """
    输入指定城市的名称,查询该城市的天气信息。
    :param city: 城市名称(使用英文)
    :return: 格式化后的天气信息字符串
    """
    #调用查询天气函数,获取天气数据
    data = await query_weather(city)
    #调用数据格式化函数,将数据转换为易读文本
    return format_weather_data(data)
#主程序入口，启动mcp服务器，并指定stdio为标准输入输出
if __name__ == "__main__":
    try:
        # 打印启动成功信息
        print("天气服务器启动成功！")
        # 启动服务器，使用stdio传输并保持运行
        mcp.run(transport="stdio")
    except Exception as e:
        # 捕获并输出所有异常，避免无声崩溃
        print(f"服务器启动失败: {str(e)}")


