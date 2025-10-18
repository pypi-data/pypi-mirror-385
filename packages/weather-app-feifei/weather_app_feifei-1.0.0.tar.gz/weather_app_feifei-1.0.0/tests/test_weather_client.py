import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio  # 确保导入asyncio
from contextlib import AsyncExitStack
import sys
import os

# 添加src目录到Python路径，以便能够导入weather_app模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入被测试的MCPClient
from weather_app.weather_client import MCPClient

# 恢复继承默认的unittest.TestCase（无需AsyncTestCase）
class TestWeatherClient(unittest.TestCase):
    
    def setUp(self):
        # 在创建MCPClient之前，先模拟环境变量
        with patch.dict('os.environ', {
            'DEEPSEEK_API_KEY': 'test_api_key',
            'base_url': 'http://test.example.com',
            'model': 'test-model'
        }):
            self.client = MCPClient()
    
    # 测试连接服务器方法
    @patch('weather_app.weather_client.stdio_client')
    @patch('weather_app.weather_client.ClientSession')
    def test_connect_to_server(self, mock_session, mock_stdio_client):
        # 定义内部异步函数，封装原异步测试逻辑
        async def async_test_logic():
            # 模拟stdio_client返回的传输对象
            mock_transport = (AsyncMock(), AsyncMock())
            mock_stdio_client.return_value.__aenter__.return_value = mock_transport
            
            # 模拟ClientSession
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            # 模拟list_tools响应
            mock_session_instance.list_tools.return_value = AsyncMock(tools=[])
            
            # 测试连接服务器
            server_script_path = "test_server.py"
            await self.client.connect_to_server(server_script_path)
            
            # 验证session被正确设置
            self.assertEqual(self.client.session, mock_session_instance)
        
        # 用asyncio.run()执行异步逻辑
        asyncio.run(async_test_logic())
    
    # 测试查询处理方法 - 简化版本，只测试基本逻辑
    def test_process_query_basic(self):
        """测试process_query方法的基本逻辑（不涉及真实API调用）"""
        # 定义内部异步函数
        async def async_test_logic():
            # 模拟session和list_tools
            self.client.session = AsyncMock()
            mock_tool = AsyncMock()
            mock_tool.name = "weather_query"
            mock_tool.description = "查询天气信息"
            mock_tool.inputSchema = {"type": "object", "properties": {"city": {"type": "string"}}}
            self.client.session.list_tools.return_value = AsyncMock(tools=[mock_tool])
            
            # 模拟OpenAI客户端响应
            mock_choice = MagicMock()
            mock_choice.message.content = "测试响应"
            mock_choice.finish_reason = "stop"
            
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            
            # 直接模拟client.chat.completions.create方法
            self.client.client.chat.completions.create = MagicMock(return_value=mock_response)
            
            # 测试查询处理
            query = "查询北京天气"
            result = await self.client.process_query(query)
            
            # 验证结果
            self.assertEqual(result, "测试响应")
            # 验证API调用参数
            self.client.client.chat.completions.create.assert_called_once()
        
        # 用asyncio.run()执行异步逻辑
        asyncio.run(async_test_logic())
    
    # 测试工具调用场景
    def test_process_query_with_tool_call(self):
        """测试process_query方法在需要工具调用时的逻辑"""
        # 定义内部异步函数
        async def async_test_logic():
            # 模拟session和list_tools
            self.client.session = AsyncMock()
            mock_tool = AsyncMock()
            mock_tool.name = "weather_query"
            mock_tool.description = "查询天气信息"
            mock_tool.inputSchema = {"type": "object", "properties": {"city": {"type": "string"}}}
            self.client.session.list_tools.return_value = AsyncMock(tools=[mock_tool])
            
            # 模拟第一次API调用（触发工具调用）
            mock_tool_call = MagicMock()
            mock_tool_call.function.name = "weather_query"
            mock_tool_call.function.arguments = '{"city": "北京"}'
            mock_tool_call.id = "test_tool_call_id"
            
            mock_message = MagicMock()
            mock_message.tool_calls = [mock_tool_call]
            mock_message.model_dump.return_value = {"role": "assistant", "content": None, "tool_calls": [{"function": {"name": "weather_query", "arguments": '{"city": "北京"}'}, "id": "test_tool_call_id"}]}
            
            mock_choice_tool = MagicMock()
            mock_choice_tool.message = mock_message
            mock_choice_tool.finish_reason = "tool_calls"
            
            mock_response_tool = MagicMock()
            mock_response_tool.choices = [mock_choice_tool]
            
            # 模拟工具调用结果
            mock_tool_result = MagicMock()
            mock_tool_result.content = [MagicMock(text="北京天气：晴，25℃")]
            self.client.session.call_tool = AsyncMock(return_value=mock_tool_result)
            
            # 模拟第二次API调用（返回最终结果）
            mock_choice_final = MagicMock()
            mock_choice_final.message.content = "北京天气：晴，25℃"
            mock_choice_final.finish_reason = "stop"
            
            mock_response_final = MagicMock()
            mock_response_final.choices = [mock_choice_final]
            
            # 设置API调用的顺序
            self.client.client.chat.completions.create = MagicMock(side_effect=[mock_response_tool, mock_response_final])
            
            # 测试查询处理
            query = "查询北京天气"
            result = await self.client.process_query(query)
            
            # 验证结果
            self.assertEqual(result, "北京天气：晴，25℃")
            # 验证API被调用了两次
            self.assertEqual(self.client.client.chat.completions.create.call_count, 2)
            # 验证工具调用
            self.client.session.call_tool.assert_called_once_with("weather_query", {"city": "北京"})
        
        # 用asyncio.run()执行异步逻辑
        asyncio.run(async_test_logic())

if __name__ == '__main__':
    unittest.main()