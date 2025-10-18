#这段代码是 “API 配置 + 异步天气查询（含异常处理） + 数据格式化 + MCP 工具注册与服务启动” 的完整实现，核心是通过模块化设计，将天气数据的获取、处理与对外提供服务的逻辑分离。
# 既保证了请求的可靠性（异常处理）和数据的可读性（格式化），又通过 MCP 框架将功能封装为可通过标准输入输出调用的服务，实现了便捷的外部访问。
# 构建mcpserver  # 注释：表明当前代码的功能是构建一个MCP（可能是某种微服务或通信协议）服务器
# 导入依赖包  # 注释：引入程序所需的第三方库和模块
import json  # 导入json模块：用于处理JSON格式的数据（序列化和反序列化）
import httpx  # 导入httpx模块：用于发送异步HTTP请求（相比requests库支持异步操作）
import os  # 导入os模块：用于访问操作系统功能，如环境变量
from typing import Any  # 从typing模块导入Any类型：用于类型注解，表示任意类型
from mcp.server.fastmcp import FastMCP  # 从mcp.server.fastmcp模块导入FastMCP类：用于快速构建MCP服务器的核心类
from dotenv import load_dotenv  # 导入load_dotenv函数：用于从.env文件加载环境变量

# 加载环境变量 - 从.env文件读取配置
load_dotenv()

# OpenWeather API配置  # 注释：配置访问OpenWeather天气API的相关参数
mcp = FastMCP("WeatherServer")  # 创建FastMCP实例，命名为"WeatherServer"：作为当前MCP服务器的核心对象，用于注册工具和启动服务
#这行代码相当于 "你买了一套服务器硬件fastmcp，组装好后贴上'WeatherServer'的标签，然后把它的控制权交给一个叫'mcp'的管理员"—— 后续你想添加功能（注册工具）、开机（启动服务），都要跟这个 "管理员" 打招呼。
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5/weather"  # 定义OpenWeather API的基础URL：天气查询接口的固定地址
# 从环境变量读取API密钥，如果不存在则使用默认值（仅用于演示）
API_KEY = os.getenv("OPENWEATHER_API_KEY")  # 从环境变量获取API密钥：更安全的凭证管理方式
USER_AGENT = "weather-app/1.0"  # 定义用户代理：标识请求来源的应用信息，便于API服务统计和识别
#这行代码是 HTTP 请求的 “身份名片” —— 用于告诉外部 API（比如原代码中的 OpenWeather API）“我是谁”，避免被当成 “不明来源的请求” 拒绝。
# 定义一个查询天气的异步函数，用于向网站请求城市的天气信息，并对可能出现的异常进行处理  # 注释：说明函数的核心功能和异常处理设计
async def query_weather(city: str) -> dict[str, Any] | None:  # 定义异步函数query_weather，接收字符串类型的city参数，返回字典（键为str，值为Any）或None
    """
    从OpenWeather API查询的天气信息。
    :param city: 城市名称
    :return: 包含天气信息的字典,或error(如果查询失败)
    """  # 函数文档字符串：说明函数用途、参数和返回值
    
# http请求参数设置  # 注释：配置发送HTTP请求时的查询参数
    params = {  # 定义参数字典：用于构造API请求的查询字符串
            "q": city,  # "q"参数：指定要查询的城市名称（由函数参数传入）
            "appid": API_KEY,  # "appid"参数：传入API密钥，用于验证身份
            "units": "metric",  # "units"参数：设置温度单位为摄氏度（metric表示公制单位）
            "lang": "zh_cn"  # "lang"参数：设置返回结果的语言为中文
        }
    
# http请求头设置  # 注释：配置HTTP请求的头部信息

    headers = {  # 定义请求头字典：模拟浏览器或应用的请求标识
            "User-Agent": USER_AGENT  # 设置User-Agent：使用前面定义的应用标识
        }
    
# 创建http客户端  # 注释：初始化异步HTTP客户端
    async with httpx.AsyncClient() as client:  # 使用异步上下文管理器创建httpx客户端：自动管理连接的创建和关闭，避免资源泄露
# httpx.AsyncClient 是 httpx 库提供的异步版本的 HTTP 客户端，专门用于在异步函数（async def 定义的函数）中发送 HTTP 请求，异步客户端（AsyncClient）发送请求时不会阻塞，程序可以在等待响应的同时处理其他任务。
#as client 是把创建的 AsyncClient 实例赋值给变量 client，方便后续用 client.get(...) 发送请求。
#async with 是 Python 为异步操作设计的 “上下文管理器” 语法，作用类似同步代码中的 with（比如操作文件时的 with open(...) as f），但专门用于异步场景。
# 其核心功能是自动管理资源的生命周期：
# 进入 async with 块时，自动创建 AsyncClient 实例（建立连接所需的资源，比如网络套接字）；
# 退出 async with 块时（无论代码正常执行还是抛出异常），自动销毁 AsyncClient 实例（关闭连接、释放网络资源）。
#如果不使用 async with，而是手动创建客户端：
# client = httpx.AsyncClient()  # 手动创建
# response = await client.get(...)
# # 用完后需要手动关闭
# await client.aclose()
# 可能会出现问题：
# 如果代码在 get 之后、aclose 之前抛出异常，client.aclose() 可能不会执行，导致连接一直占用（资源泄露）；
# 大量未关闭的连接会耗尽系统资源（比如端口），导致后续请求失败。
# 而 async with 能保证无论代码正常执行还是出错，客户端都会被自动关闭，彻底避免这种问题。
        try:  # 尝试执行HTTP请求操作
            # 发送GET请求查询天气  # 注释：发送请求到API服务器
            response = await client.get(  # 调用客户端的get方法发送异步GET请求，等待响应结果
#await会让程序 “暂停等待” 这个请求完成（但不会阻塞整个程序，其他任务可以同时运行），直到服务器返回响应后再继续执行
                OPENWEATHER_API_BASE,  # 指定请求的URL（前面定义的API基础地址）
                params=params,  # 传入查询参数（前面定义的params字典）
                headers=headers,  # 传入请求头（前面定义的headers字典）
                timeout=30.0  # 设置超时时间为30秒：避免请求长时间无响应导致程序阻塞
            )
            # 检查响应状态码,不是2xx系列,则抛出异常  ,如果状态码是 2xx，这行代码什么都不做，继续执行后续逻辑
            response.raise_for_status()  # 调用raise_for_status方法：如果状态码是4xx或5xx（错误状态），会抛出HTTPStatusError异常
            #HTTPStatusError异常（被后面的except捕获），相当于 “主动报告错误”，避免错误的响应数据被后续代码误用。
            # 将响应的json数据解析为字典并返回  # 注释：处理成功响应的数据
            return response.json()  # 解析响应内容为JSON格式（字典类型）并返回;将服务器返回的 JSON 格式数据解析为 Python 可直接操作的字典（或列表等数据结构），并将其作为函数结果返回
#如果请求成功（状态码 2xx），这行代码会将服务器返回的原始数据解析为 Python 字典并返回，供后续格式化使用。
#API 返回的数据格式：OpenWeather API 返回的是 JSON 格式的字符串（比如{"name":"北京","main":{"temp":25}...}），这是网络接口常用的数据交换格式，结构清晰但需要解析才能被 Python 直接使用。
        # 处理http状态错误(如404等)  # 注释：捕获HTTP状态错误
        except httpx.HTTPStatusError as e:  # 捕获httpx库的HTTPStatusError异常（状态码错误）
            return {"error": f"HTTP错误: {e.response.status_code}"}  # 返回包含错误信息的字典，说明具体的HTTP状态码
# except httpx.HTTPStatusError 只处理 HTTP 状态错误，用 except TimeoutError 只处理超时错误，实现 “精准处理特定错误”。
#401：API 密钥错误（没权限）；404：请求的接口地址不存在；503：服务器暂时不可用）。
        # 处理其他可能的问题(如网络问题等)  # 注释：捕获其他异常
        except Exception as e:  # 捕获所有其他未预料到的异常（如网络中断、超时等）,Exception 是 Python 中所有 “可捕获的错误” 的基类
            return {"error": f"请求失败: {str(e)}"}  # 返回包含错误信息的字典，说明具体的错误原因,as e 就是把这个对象赋值给 e

# 数据格式化，将网站返回的复杂结构数据转化为用户易读的文本输出  # 注释：说明函数的功能是格式化数据
def format_weather_data(data: dict[str, Any] | str) -> str:  # 定义格式化函数，接收字典（键为str，值为Any）或字符串，返回格式化后的字符串
    """
    将OpenWeather API返回的天气数据格式化为易读的文本。
    :param data: 天气数据(可以使字典或者json字符串)
    :return: 格式化后的天气信息字符串
    """  # 函数文档字符串：说明函数用途、参数和返回值
    
    # 如果输入是字符串,则先解析为字典  # 注释：处理可能的字符串类型输入,这行代码的设计体现了函数的灵活性和容错性
    #即使在主流程中，也可能出现意外情况导致data变成字符串（比如数据传递过程中被序列化、或其他函数误传了字符串）。这行代码相当于 “加了一层保险”，确保即使输入是字符串，也能尝试解析成字典再处理，避免直接报错。
    if isinstance(data, str):  # 判断输入data是否为字符串类型
        try:  # 尝试解析字符串为JSON字典
            data = json.loads(data)  # 使用json.loads将字符串解析为字典;字符串必须是必须符合 JSON 语法，且最外层是 {}（JSON 对象），键用双引号，值是 JSON 支持的类型。
        except Exception as e:  # 捕获解析失败的异常（如格式错误）
            return f"无法解析天气数据: {e}"  # 返回解析错误信息
    

    # 检查是否包含错误信息  # 注释：处理查询失败的情况
    if "error" in data:  # 判断数据中是否包含"error"键（即查询过程中出现错误）
        return f"查询天气失败: {data['error']}"  # 返回错误信息，说明查询失败的原因
    
    # 提取数据时做容错处理,确保缺少数据也能正常工作  # 注释：安全提取数据，避免KeyError
    city = data.get("name", "未知")  # 从data中获取"name"字段（城市名），默认值为"未知"
    country = data.get("sys", {}).get("country", "未知")  # 从嵌套的"sys"字段中获取"country"（国家代码），默认值为"未知"
    temp = data.get("main", {}).get("temp", "N/A")  # 从嵌套的"main"字段中获取"temp"（温度），默认值为"N/A"
    humidity = data.get("main", {}).get("humidity", "N/A")  # 从嵌套的"main"字段中获取"humidity"（湿度），默认值为"N/A"
    wind_speed = data.get("wind", {}).get("speed", "N/A")  # 从嵌套的"wind"字段中获取"speed"（风速），默认值为"N/A"
    
    # weather可能是空列表，因此先提供默认字典  # 注释：处理可能的空列表情况
    weather_list = data.get("weather", [{}])  # 从data中获取"weather"列表，默认值为包含空字典的列表
    description = weather_list[0].get("description", "未知")  # 从weather列表的第一个元素中获取"description"（天气描述），默认值为"未知"
    
    #  f-string（格式化字符串），这是最简洁的 “拼接方式”。它的作用是：将{}里的动态变量（比如city、temp，值会随查询结果变化）和{}外的固定文本
    # （比如 “城市:”、“°C”，内容固定不变）“粘” 在一起，形成一句完整的话。  # 注释：组织最终的输出文本
    #\n换行
    # 格式化输出  # 注释：返回拼接后的字符串
    return (
        f"城市: {city} ({country})\n"  # 拼接城市和国家信息
        f"天气: {description}\n"  # 拼接天气描述信息
        f"温度: {temp}°C\n"  # 拼接温度信息（带摄氏度单位）
        f"湿度: {humidity}%\n"  # 拼接湿度信息（带百分号单位）
        f"风速: {wind_speed} m/s\n"  # 拼接风速信息（带单位）
    )

# 使用mcp装饰器封装query_weather函数为工具，实现天气的查询以及结果的格式化  # 注释：说明以下代码的功能是封装工具
# 使用mcp装饰器将其标记为一个工具  # 注释：说明装饰器的作用
@mcp.tool()  # 应用mcp的tool装饰器：将该函数query_weather_mcp注册为MCP服务器的一个可用工具，使其能被外部调用
# 定义一个异步函数并声明其用途  # 注释：说明函数的作用
async def query_weather_mcp(city: str) -> str:  # 定义异步函数query_weather_mcp，接收城市名参数，返回格式化后的字符串
    """
    输入指定城市的名称,查询该城市的天气信息。
    :param city: 城市名称(使用英文)
    :return: 格式化后的天气信息字符串
    """  # 函数文档字符串：说明工具的用途、参数要求和返回值
    
    # 调用查询天气函数,获取天气数据
    data = await query_weather(city)  # 调用天气查询函数，获取原始天气数据
    # 调用数据格式化函数,将数据转换为易读文本  # 注释：处理原始数据为可读格式
    return format_weather_data(data)  # 调用格式化函数处理原始数据，并返回结果

# 主程序入口，启动mcp服务器，并指定stdio为标准输入输出  # 注释：说明程序的启动逻辑
if __name__ == "__main__":  # 判断当前模块是否为主程序入口（即直接运行该脚本时）
    mcp.run(transport="stdio")  # 调用mcp实例的run方法启动服务器，指定传输方式为"stdio"（标准输入输出），使服务器能通过标准流接收和响应请求