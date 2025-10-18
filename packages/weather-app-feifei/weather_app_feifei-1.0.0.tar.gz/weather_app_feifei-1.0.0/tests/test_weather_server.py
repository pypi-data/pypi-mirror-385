import unittest
from unittest.mock import patch, MagicMock
import asyncio
import sys
import os

# 添加src目录到Python路径，以便能够导入weather_app模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入weather_app模块中的服务器功能
from weather_app.weather_server import query_weather, format_weather_data

class TestWeatherServer(unittest.TestCase):
    
    @patch('weather_app.weather_server.httpx.AsyncClient')
    def test_query_weather(self, mock_client):
        # 创建模拟的响应数据
        mock_response_data = {
            'name': 'Beijing',
            'sys': {'country': 'CN'},
            'main': {
                'temp': 25,
                'humidity': 60
            },
            'wind': {'speed': 3.5},
            'weather': [{'description': '晴'}]
        }
        
        # 创建模拟的响应对象
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        
        # 创建模拟的异步上下文管理器
        mock_client_instance = MagicMock()
        
        # 创建一个可以await的协程函数来模拟get方法
        async def mock_get(*args, **kwargs):
            return mock_response
        
        mock_client_instance.get = mock_get
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        mock_client.return_value.__aexit__.return_value = None
        
        # 测试查询功能
        async def run_test():
            result = await query_weather('Beijing')
            self.assertEqual(result['name'], 'Beijing')
            self.assertEqual(result['main']['temp'], 25)
            self.assertEqual(result['weather'][0]['description'], '晴')
        
        asyncio.run(run_test())
        
    def test_format_weather_data(self):
        # 测试数据格式化功能 - 使用符合OpenWeather API实际返回格式的数据
        weather_data = {
            'name': 'Beijing',
            'sys': {'country': 'CN'},
            'main': {
                'temp': 25,
                'humidity': 60
            },
            'wind': {'speed': 3.5},
            'weather': [{'description': '晴'}]  # 注意：weather是列表，包含字典
        }
        formatted = format_weather_data(weather_data)
        self.assertIn('城市', formatted)
        self.assertIn('天气', formatted)
        self.assertIn('温度', formatted)
        self.assertIn('湿度', formatted)

if __name__ == '__main__':
    unittest.main()