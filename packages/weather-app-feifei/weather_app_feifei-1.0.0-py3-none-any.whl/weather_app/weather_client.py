# 导入依赖包
import asyncio
import os
import sys
import json
from typing import Optional
from contextlib import AsyncExitStack
from openai import OpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 加载.env文件中的环境变量
load_dotenv()
#定义 MCP 客户端类，封装了与 MCP Server 通信、大语言模型交互、工具调用、交互式聊天等核心逻辑。
class MCPClient:
    # 初始化MCP客户端，设置OpenAI API密钥、基础URL、模型名称等参数。
    def __init__(self):
        """初始化MCP客户端"""
        # 用于管理异步上下文
        self.exit_stack = AsyncExitStack()
        # 读取api_key
        self.openai_api_key = os.getenv("DEEPSEEK_API_KEY")
        # 读取base_url
        self.base_url = os.getenv("base_url")
        # 读取model
        self.model = os.getenv("model")
        # 检查api_key
        if not self.openai_api_key:
            raise ValueError("DEEPSEEK_API_KEY 未设置")
        # 创建OpenAI Client
        self.client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.base_url,
        )
        # 初始化对话
        self.session: Optional[ClientSession] = None
    # 判断MCP Server的文件类型是.py或.js，并运行相应的命令
    async def connect_to_server(self, server_script_path: str):
        """连接到MCP Server 并列出可用工具"""
        # 判断MCP Server的文件类型是.py或.js
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        # 根据文件类型运行不同的命令
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        # 与mcpserver通信，并列出mcpserver上的工具
        # 启动 MCP Server 并建立通信
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        # 将 stdio_transport 对象解包为两个部分
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        # 初始化会话
        await self.session.initialize()
        # 列出 MCP Server 上的工具
        response = await self.session.list_tools()
        tools = response.tools
        print("\n已连接到服务器,支持以下工具：", [tool.name for tool in tools])
    #使用大语言模型处理查询并调用可用的 MCP 工具(Function Calling)
    async def process_query(self, query: str) -> str:
        """
        使用大语言模型处理查询并调用可用的 MCP 工具(Function Calling)
        """
        # 构建一个消息列表
        messages = [{"role": "user", "content": query}]
        
        # 获取 MCP Server 上的工具列表
        response = await self.session.list_tools()
        
        # 格式化工具列表（适配大模型 Function Calling 格式）
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in response.tools]
        
        # 发送 API 请求（调用大模型）
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=available_tools
        )
        
        # 处理返回的内容
        # 获取模型的响应内容
        content = response.choices[0]
        
        # 判断是否需要调用 MCP Server（是否触发工具调用）
        if content.finish_reason == "tool_calls":
            # 解析工具调用信息
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # 执行 MCP Server 上的工具
            result = await self.session.call_tool(tool_name, tool_args)
            
            # 输出工具调用的调试信息
            print(f"\n\nCalling tool {tool_name} with args {tool_args}\n\n")
            
            # 记录"工具调用请求"和"工具执行结果"到对话历史
            messages.append(content.message.model_dump())
            messages.append({
                "role": "tool",
                "content": result.content[0].text if result.content else "工具执行完成",
                "tool_call_id": tool_call.id,
            })
            
            # 将工具结果回传给大模型，生成最终回答
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            
            # 返回大模型生成的最终结果
            final_content = response.choices[0].message.content
            return final_content if final_content else "处理完成"
        
        # 如果不需要调用工具，直接返回大模型的回答
        final_content = content.message.content
        return final_content if final_content else "查询完成"
    #运行交互式聊天循环
    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n 🤖 MCP 客户端已启动! 输入 'quit' 退出")
        
        # 无限循环实现连续对话
        while True:
            try:
                query = input("\n你： ").strip()
                
                # 输入 'quit' 则退出对话
                if query.lower() == 'quit':
                    break
                
                # 处理用户查询并获取响应
                response = await self.process_query(query)
                print(f"\n 🤖 OpenAI: {response}")
                
            # 捕获并打印异常
            except Exception as e:
                print(f"\n ⚠️ 发生错误: {str(e)}")
    # 退出时清理资源（如关闭异步上下文）
    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()
#定义异步主函数，用于统筹整个程序流程（包括命令行参数检查、MCP 客户端实例化、连接服务器、启动聊天循环等）。
async def main():
    # 检查命令行参数（确保指定了 MCP Server 脚本路径）
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
    
    # 创建 MCP 客户端实例
    client = MCPClient()
    
    try:
        # 连接服务器
        await client.connect_to_server(sys.argv[1])
        # 开始聊天循环
        await client.chat_loop()
    finally:
        # 确保执行清理工作
        await client.cleanup()
# 程序入口
if __name__ == "__main__":
    asyncio.run(main())