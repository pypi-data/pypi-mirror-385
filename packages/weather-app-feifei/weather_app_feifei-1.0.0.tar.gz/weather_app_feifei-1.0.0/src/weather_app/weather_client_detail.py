# 此代码完整实现了 “环境配置加载、MCP 服务器通信、大模型交互（含工具调用决策）以及交互式聊天” 功能。
# 核心采用分层设计，将配置管理、服务器连接、模型推理和用户交互的逻辑解耦。
# 借助异步上下文栈实现资源的安全管理，通过异常捕获保障交互的稳定性。
# 利用 MCP 框架实现客户端与服务器的标准化通信，结合大模型的工具调用能力，
# 使用户能通过自然语言查询获取经工具处理后的精准结果。

# 代码通过 MCPClient 类封装核心逻辑，各阶段功能如下：
# • 初始化阶段：加载 API 密钥和模型配置，创建 OpenAI 客户端与异步资源管理器。
# • 连接阶段：通过标准输入输出与 MCP 服务器建立通信，获取可用工具列表。
# • 处理阶段：借助大模型判断是否调用工具，若需要则通过服务器执行并整合结果。
# • 交互阶段：通过循环实现持续对话，确保用户拥有流畅的使用体验。
# • 退出阶段：自动清理资源，避免连接泄漏。

# 整体实现了 “用户输入 → 模型决策 → 工具调用（按需） → 结果反馈” 的闭环，
# 既发挥了大模型的自然语言理解能力，又借助 MCP 框架扩展了外部工具的调用能力。
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
        # AsyncExitStack 是 Python 标准库 contextlib 中的异步上下文管理工具，用于统一管理多个异步资源的生命周期（如与 MCP 服务器的连接、会话等）。
        # 作用：当程序正常结束或发生异常时，AsyncExitStack 会自动调用所有已注册资源的关闭方法（如 aclose()），确保资源（如网络连接、文件句柄）被正确释放，避免资源泄漏。
        # self.exit_stack 将作为实例变量，在后续连接 MCP 服务器、创建会话时使用。
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
        # 创建OpenAI实例self.client,后续所有与大语言模型的交互（如发送用户查询、获取模型响应）都通过self.client完成
        # 它是一个 “API 交互中间件”—— 把 “调用大语言模型” 的复杂流程
        # OpenAI()把“身份验证、发请求、转格式、处理错、解结果”全封装成简单的 “方法调用”，并生成实例self.client，让你不用关注底层技术细节
        self.client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.base_url,
        )
        # 初始化对话，self.session 就相当于一张 “内存卡”，记录了客户端和 MCP 服务器之间的连接信息（比如通信通道、会话状态等）。
        # 这行代码的作用就是：在客户端初始化时，先 “预留一个位置”（self.session），告诉程序 “这里将来要放和 MCP 服务器的会话session信息”；
        # 但因为这时候还没连接服务器，所以暂时先空着（= None），等连接成功后再填入真正的会话对象。
        # Optional[ClientSession] 是 Python 的 “类型注解”（一种代码说明）
        # 它的意思是：这个 self.session 变量，要么是 ClientSession 类型的对象（也就是真正的 “会话”），要么是 None（空，没有值）。
        # Optional 是 Python 标准库 typing 模块里的工具，用来表示：变量的类型可以是 “指定类型”
        # 给 self.session 赋初始值 None
        self.session: Optional[ClientSession] = None
    # connect_to_server是 MCP 客户端连接服务器的核心异步逻辑
    # 作用是 “确定服务器脚本类型,创建 MCP Server 启动参数对象,启动 MCP Server → 建立通信通道 → 创建会话 → 最终目的是，列出可用工具”
    # 每一行代码都在为 “后续调用服务器工具” 做准备。
    # 这个函数是 “客户端与 MCP Server 的桥梁”，跑完这个函数，客户端就和服务器建立了稳定的连接，后续就能通过self.session调用服务器上的工具了。
    async def connect_to_server(self, server_script_path: str):
        """连接到MCP Server 并列出可用工具"""
        # 判断MCP Server的文件类型是.py或.js
        # 根据文件类型运行不同的命令
        # 如果是 Python 脚本，用python命令启动；如果是 JS 脚本，用node命令启动，结果存到command（后续启动服务器要用）
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        command = "python" if is_python else "node"
        #StdioServerParameters：是 MCP 库提供的 “参数类”，专门用来封装 “启动 MCP Server 所需的配置”，让后续启动逻辑更简洁。
        #1.command=command：传入刚才确定的启动命令（python或node）。
        #2.args=[server_script_path]：传入启动命令的 “参数”—— 也就是 MCP Server 脚本的路径（比如./server.py），用列表形式传递（因为命令参数可能有多个，这里只有一个脚本路径）。
        #举个例子：如果command=python、args=["./server.py"]，组合起来就是系统要执行的命令：python ./server.py。
        #3.env=None：设置启动服务器时的 “环境变量”，None表示沿用当前程序的环境变量（比如系统的PATH、之前加载的DEEPSEEK_API_KEY等），不需要额外配置。
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        # 启动 MCP Server 并建立标准输入输出（stdio）通信通道，后续用于列出服务器工具及初始化会话
        # stdio_client(server_params) 是 MCP 库提供的通信客户端函数，依据 server_params 配置启动 MCP Server，
        # 并创建一个 “异步上下文管理器”（AsyncExitStack），用于管理启动过程中的资源（如进程、网络连接等）。
        # 同时创建客户端与服务器间的 stdio 通信通道，返回通信通道对象 stdio_transport
        # self.exit_stack.enter_async_context() 会自动管理该通道的生命周期，
        # 在程序正常结束或发生异常时自动关闭通道，释放网络连接、文件句柄等资源，防止资源泄漏
        # stdio_client(server_params)：创建客户端与 MCP Server 的通信通道；
        # ClientSession(self.stdio, self.write)：客户端与 MCP Server 的会话对象。

        # AsyncExitStack 与 enter_async_context ，二者配合实现异步资源全生命周期自动管理：
        # 先在类的 __init__ 方法中通过 AsyncExitStack() 实例化出 self.exit_stack（相当于搭建空快递柜，创建 “管家”）
        # 之后在 connect_to_server 中通过 await self.exit_stack.enter_async_context(...)
        # （如传入 MCP 通信通道、会话对象）让 “管家” 接收资源 —— 既将资源 “记到清单”，
        # 又为其绑定 “释放时调用 aclose()” 的规则（相当于存快递并约定处理方式），
        # 最后程序退出时调用 self.exit_stack.aclose()，“管家” 按资源存入逆序自动关闭所有资源
        # （相当于关快递柜并统一处理内部快递），整体无需手动管理资源，简化 MCP 客户端等场景的异步资源管理逻辑。
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        # 将 stdio_transport 对象解包为两个部分
        #self.stdio：客户端的 “标准输入流”—— 用来接收 MCP Server 发过来的消息（比如工具列表、工具调用结果）。
        #self.write：客户端的 “标准输出流”—— 用来给 MCP Server 发消息（比如 “初始化会话”“调用工具” 的请求）。
        self.stdio, self.write = stdio_transport
        #创建对话session， “建立可用的会话” 并 “让用户知道有哪些工具能调用”
        # ClientSession(self.stdio, self.write)：MCP 库提供的 “会话类”，用来创建一个会话对象（self.session）。
        # 会话对象的作用是：记录客户端和服务器之间的 “通信状态”（比如会话ID、工具调用记录等）。
        # 后续调用服务器工具时，都要通过这个会话对象来进行。
        # 使用 self.exit_stack.enter_async_context 管理会话对象生命周期，具备以下功能：
        # - 会话创建时自动发送初始化请求完成会话初始化
        # - 会话持续存在直至程序结束或手动关闭
        # - 自动记录每次工具调用的名称和参数等信息
        # - 会话结束时自动发送关闭请求释放资源
        # self.session 是 ClientSession 类的实例，它相当于 “客户端与 MCP Server 的‘专属电话卡’”—— 封装了所有和服务器通信的细节
        # 你不用自己 “接线”（操作 self.stdio 和 self.write 收发消息），直接 “拨号码”（调用 self.session 的方法）就能用工具。
        # 一句话来说，self.session 把上面的两行代码封装起来了。
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        # 初始化会话，给 MCP Server 发 “初始化会话” 的请求 —— 这是 MCP 协议的要求
        # 必须先初始化，后续才能调用list_tools（列工具）、call_tool（调工具）等接口
        await self.session.initialize()
        # 列出 MCP Server 上的工具
        # response.tools 是 MCP Server 返回的 “工具对象列表”
        # 每个元素都是一个 tool 对象，包含 name（名称）、description（描述）、inputSchema（参数 schema）等属性。
        response = await self.session.list_tools()
        tools = response.tools
        # [tool.name for tool in tools]
        # 拆解成普通for循环，等价于：
        # tool_names = []  # 新建一个空列表存名称
        # for tool in tools:  # 遍历tools里的每个工具对象
        #     tool_names.append(tool.name)  # 把每个工具的name属性加入列表
        print("\n已连接到服务器,支持以下工具：", [tool.name for tool in tools])
    # 核心作用是：结合大语言模型与 MCP Server 的工具调用能力，处理用户查询并返回最终结果。
    # 具体流程：
    # 接收用户查询，建初始对话消息；
    # 取 MCP 工具列表并格式化为模型可识别的格式；
    # 调大模型，让其判断是否需用工具；
    # 需用则调用 MCP 工具、补全对话上下文后让模型生成最终回答，无需则直接返回模型回答；
    # 输出最终结果，实现 “用户提问→server提供工具列表给大模型→大模型判是否用工具→用工具（按需）或不用工具→大模型整合所有message出回答” 的闭环。   
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
        # 发送 API 请求（调用大模型,把用户需求、可用工具传给模型(self.client)，让模型做 “是否调用工具” 的决策）
        # self.client 帮你完成 “API 请求的所有脏活”
        # 将3个参数，转换成模型 API 要求的 JSON 格式；
        # 用{你的 API 密钥} 完成身份验证；
        # 从环境变量读的 API 地址）发 POST 请求，把这些信息传给大语言模型的服务器
        # 模型会根据用户需求和可用工具，返回一个 JSON 格式的响应
        response = self.client.chat.completions.create(
            model=self.model,      #用什么模型
            messages=messages,     #用户角色和query
            tools=available_tools  #可用工具
        )
        # 处理返回的内容
        # 获取模型的响应内容，模型的响应结果（即 response 对象）是由 openai 库封装的 ChatCompletion 类实例
        # response.choices[0] 是一个 ChatCompletionChoice 类实例，包含模型的响应内容（即 content.message.content）
        # 以及其他信息（如 finish_reason、logprobs 等）
        content = response.choices[0]
        # 判断是否需要调用 MCP Server（是否触发工具调用）
        if content.finish_reason == "tool_calls":
            # 解析工具调用信息
            # 只有 tool_call.function.arguments 是 JSON 字符串格式，需要通过 json.loads 转换为 Python 字典才能被代码后续逻辑使用；
            # 而其他属性本身就是 Python 可直接处理的原生类型（字符串、对象），因此无需转换。
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            # 执行 MCP Server 上的工具，将工具调用生成的结果（result）赋值给 result 变量
            result = await self.session.call_tool(tool_name, tool_args)
            # 输出工具调用的调试信息，告诉开发者 / 用户 “当前正在调用哪个工具，用了哪些参数”，便于调试（比如检查参数是否正确解析、工具名是否匹配）
            print(f"\n\nCalling tool {tool_name} with args {tool_args}\n\n")
            # 记录 模型决定的"工具调用请求"和"工具执行结果"到对话历史
            # content.message：是把 模型 之前生成的 “工具调用请求消息”（包含 role="assistant"、tool_calls 等信息）。
            # model_dump()：将消息对象（ChatCompletionMessage 实例）转换为字典（方便存入列表）。
            # 目的：把 “模型决定调用工具” 这个决策过程记录到 messages 列表中，让后续的模型调用知道 “之前已经发起过工具调用请求”，保持对话上下文的连贯性。   
            messages.append(content.message.model_dump())
            # 将工具执行的具体结果加入对话历史，让模型能读取到 “工具返回了什么信息”
            messages.append({
                "role": "tool",
                "content": result.content[0].text,
                "tool_call_id": tool_call.id,
            })
            # 将工具结果回传给大模型，生成最终回答
            # 此时的 messages 已经包含完整上下文：
            # 即[用户原始问题, 模型的工具调用请求, 工具返回的结果]
            # 模型会基于这些信息，将 “工具结果” 整理成自然语言回答（比如把 “天气数据” 转换成 “北京今天天气晴朗，适合出行”）
            # create 是 openai 库中 ChatCompletions 类的核心方法，作用是：
            # 向大语言模型（如 DeepSeek、GPT）发送 “聊天补全请求”，传递模型名称（model）、对话历史（messages）等参数；
            # 等待模型处理并返回生成的响应（即 response 对象）。    
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            # 返回大模型生成的最终结果
            return response.choices[0].message.content
        # 如果不需要调用工具，直接返回大模型的回答
        return content.message.content
    # chat_loop 是 MCP 客户端的交互式对话入口，当中调用了上一个函数process_query，核心作用是让用户能持续输入查询、获取响应，同时保证程序稳定运行
    # 启动提示：打印客户端启动信息，告知用户输入 quit 可退出，明确使用规则；
    # 无限循环维持交互：通过 while True 实现 “用户输入→系统响应” 的循环，支持连续对话；
    # 用户输入处理：
    # 用 input 获取用户输入并去除首尾空格（strip）；
    # 若输入 quit（不区分大小写），则退出循环，结束对话；
    # 响应生成与输出：调用 process_query 处理用户查询，拿到结果后以 “🤖 OpenAI:” 为前缀打印，呈现给用户；
    # 异常防护：捕获循环中所有异常（如 API 调用失败、工具调用错误等），打印错误提示，避免程序崩溃。
    # 简言之，这个方法让客户端从 “单次调用” 变成 “实时对话工具”，是用户与 “大模型 + MCP 工具” 交互的直接入口。
    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n 🤖 MCP 客户端已启动! 输入 'quit' 退出")
        # 无限循环实现连续对话，让程序一直处于 “等待用户输入” 的状态，直到用户主动退出（输入 quit）
        while True:
            try:
                # 获取用户输入 并 去除首尾空格（strip）
                query = input("\n你: ").strip()
                # 输入 'quit' 则退出对话
                #query.lower()：将用户输入的内容全部转为小写（输入 Quit、QUIT，都会变成 quit），避免 “大小写不匹配导致无法退出”。
                if query.lower() == 'quit':
                    break
                # 处理用户查询并获取响应
                response = await self.process_query(query)
                print(f"\n 🤖 OpenAI: {response}")
            # 捕获并打印异常
            except Exception as e:
                print(f"\n ⚠️ 发生错误: {str(e)}")
    # 退出时清理资源（如关闭异步上下文）
    # 核心操作：await self.exit_stack.aclose()
    # self.exit_stack：还记得在 __init__ 里初始化的 AsyncExitStack 实例吗？它就像一个 “异步资源管家”
    # 之前我们通过 self.exit_stack.enter_async_context(...)，把两个关键异步资源交给它管理了：
    # stdio_client(server_params)：客户端与 MCP Server 的通信通道；
    # ClientSession(self.stdio, self.write)：客户端与 MCP Server 的会话对象。
    # aclose()：是 AsyncExitStack 的异步关闭方法，作用是 “让管家逐个关闭所有它管理的资源”—— 
    # 它会自动调用每个资源的 aclose() 方法（比如关闭通信通道、结束会话），确保资源被完整释放。
    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()
#定义异步主函数，用于统筹整个程序流程（包括命令行参数检查、MCP 客户端实例化、连接服务器、启动聊天循环等）。
async def main():
    # 检查命令行参数（确保指定了 MCP Server 脚本路径，确保Server路径存在）
    # sys.argv 是 sys 模块提供的一个列表，用于存储用户运行程序时自动存入输入的命令行参数
    # sys.argv[0] 是永远都是脚本本身的路径（client.py），sys.argv[1] 在这里是指用户指定的 MCP Server 脚本路径
    if len(sys.argv) < 2:
        print("缺少 MCP Server 脚本路径参数: python client.py <path_to_server_script>")
        # sys.exit(1)：立即终止程序运行（1 表示 “异常退出”，用于区分正常退出）
        sys.exit(1)
    
    # 创建 MCP 客户端实例
    client = MCPClient()
    try:
        # 连接服务器
        # sys.argv[1]：用户指定的 MCP Server 脚本路径，作为 connect_to_server 的参数传入
        await client.connect_to_server(sys.argv[1])
        # 开始聊天循环，process_query是单次对话，被chat_loop调用实现聊天循环
        await client.chat_loop()
    finally:
        # 确保执行清理工作
        await client.cleanup()
# 程序入口
# if __name__ == "__main__":：判断程序的 “运行方式”
# 首先要理解 __name__—— 它是 Python 内置的特殊变量，用来标识 “当前模块的运行状态”，取值只有两种情况：
# 当脚本被直接运行时（比如你在终端输入 python client.py server.py）：__name__ 会自动被赋值为 "__main__"，此时 if 条件成立，会执行缩进里的代码。
# 当脚本被作为模块导入时（比如其他脚本用 import client）：__name__ 会被赋值为模块名（比如 "client"），此时 if 条件不成立，缩进里的代码不会执行。
# 核心作用：确保 “启动异步逻辑” 的代码只在 “直接运行脚本” 时执行，避免被导入时意外触发（比如其他脚本导入 client 模块时，不会自动启动 MCP 客户端）。
if __name__ == "__main__":
    asyncio.run(main())
# 为什么必须用 asyncio.run(main())？
# 整个 MCP 客户端的核心逻辑（main() 及里面调用的 connect_to_server、chat_loop 等）都是异步函数（带 async def），这些函数必须在 “事件循环” 里才能运行。
# asyncio.run(main()) 就像一个 “一站式启动器”：
# asyncio.run() 自动搭好 “调度中心”（事件循环）；
# main()把那些异步函数async等任务交给调度中心asyncio.run()，调度中心按顺序执行这些任务；
# 最后自动拆了调度中心asyncio.run()，不留垃圾。    

