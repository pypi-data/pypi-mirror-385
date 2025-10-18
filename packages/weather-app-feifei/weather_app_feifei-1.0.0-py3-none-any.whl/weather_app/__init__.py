# 天气应用核心包
"""
weather_app 包 - 基于MCP框架的天气查询应用
包含客户端和服务器组件
"""

# 包版本
__version__ = "1.0.0"

# 控制导入行为
__all__ = [
    "weather_client",
    "weather_server", 
    "weather_client_detail",
    "weather_server_detail"
]

# 导入关键模块，使外部可以直接 from weather_app import weather_client
from . import weather_client
from . import weather_server