# -*- coding: utf-8 -*-
from autogen import AssistantAgent
from typing import Optional, Dict, Any
from tools.basic_tools import analyze_log_entry # 导入我们创建的工具

class LogAnalysisAgent(AssistantAgent):
    """
    日志分析代理 (LogAnalysisAgent)
    专门负责分析日志条目，使用提供的工具来识别潜在的安全事件或问题。
    """
    def __init__(
        self, 
        name: str, 
        llm_config: Optional[Dict[str, Any]] = None,
        system_message: Optional[str] = None,
        **kwargs
    ):
        """
        初始化日志分析代理。

        参数:
            name (str): 代理的名称。
            llm_config (Optional[Dict[str, Any]]): LLM 配置。
                           如果为 None，则代理将尝试从环境变量加载。
            system_message (Optional[str]): 要发送给 LLM 的系统消息。
                                           如果为 None，则使用默认的系统消息。
            **kwargs: 其他传递给 AssistantAgent 的参数。
        """
        # 默认的系统消息，如果用户没有提供
        default_system_message = """你是一个AI日志分析助手。
        你的职责是使用提供的工具来分析日志条目。
        仔细阅读日志，并使用 'analyze_log_entry' 工具来获取分析结果。
        当被要求分析日志时，你应该调用 'analyze_log_entry' 工具，并将日志条目作为参数传递。
        然后，将工具返回的分析结果清晰地呈现出来。
        """
        
        super().__init__(
            name, 
            llm_config=llm_config,
            system_message=system_message if system_message is not None else default_system_message,
            **kwargs
        )

        # 注册工具 (函数) 给这个代理
        # 注意：AutoGen v0.2.x 之后，工具注册通常在构建 AssistantAgent 时通过 llm_config 的 'tools' 或 'tool_map' 参数完成，
        # 或者对于 GroupChat，在 GroupChatManager 中注册。
        # AssistantAgent 本身没有直接的 register_function 方法。
        # 工具应该通过 llm_config 传递，或者在创建代理后更新其 llm_config。
        # 为了简单起见，这里我们假设工具将在使用此代理时通过 llm_config 或 GroupChatManager 注册。
        # 或者，我们可以在创建代理时，将工具函数直接绑定到代理实例的方法上，但这不完全是AutoGen的典型模式。
        #
        # 正确的工具注册方式 (在AutoGen 0.2.x+):
        # 1. 在 llm_config 中定义:
        #    llm_config = {
        #        "model": "gpt-3.5-turbo",
        #        "tools": [
        #            {
        #                "type": "function",
        #                "function": {
        #                    "name": "analyze_log_entry",
        #                    "description": "分析单个日志条目并返回分析结果。",
        #                    "parameters": {
        #                        "type": "object",
        #                        "properties": {
        #                            "log_entry": {
        #                                "type": "string",
        #                                "description": "需要分析的日志条目。"
        #                            }
        #                        },
        #                        "required": ["log_entry"]
        #                    }
        #                }
        #            }
        #        ],
        #        "tool_choice": "auto" # 或指定工具名称
        #    }
        #    agent = LogAnalysisAgent(name="日志分析员", llm_config=llm_config)
        #    agent.register_function(tool_map={"analyze_log_entry": analyze_log_entry}) # 将函数映射到名称
        #
        # 对于这个基本实现，我们将把工具注册的责任留给创建此代理实例的代码 (例如在 main.py 中)。
        # 如果 llm_config 包含工具定义，代理会自动知道它们。
        # 我们还需要确保代理能够执行这些工具，这通常通过 register_function(tool_map={...}) 实现。

    # 可以添加特定于此代理的方法，例如:
    async def analyze_this_log(self, log_to_analyze: str) -> str:
        """
        一个辅助方法，用于直接请求分析特定日志 (主要用于测试或单代理场景)。
        在多代理聊天中，代理通常会根据对话历史和LLM的决策来调用工具。
        """
        # 构建一个模拟的用户消息来触发工具调用
        # 这是一种间接的方式，通常代理会通过对话来决定是否调用工具
        user_query = f"请使用 analyze_log_entry 工具分析以下日志： '{log_to_analyze}'"
        
        # 模拟与自身的对话来获取回复 (这会触发LLM思考并可能调用工具)
        response = await self.generate_reply(
            messages=[{"role": "user", "content": user_query}],
            sender=self 
        )
        return response if isinstance(response, str) else response.get("content", "")


# 示例用法 (通常在 main.py 或测试文件中进行)
if __name__ == '__main__':
    import asyncio
    from config.config_loader import app_config # 导入配置加载器

    # 检查 API 密钥是否存在
    if not app_config.openai_api_key or app_config.openai_api_key == "YOUR_OPENAI_API_KEY_HERE":
        print("错误：OPENAI_API_KEY 未在 config/.env 文件中正确配置。请更新该文件后重试。")
        print("如果没有有效的 API 密钥，此示例将无法与 LLM 交互或使用工具。")
    else:
        print("OpenAI API 密钥已找到。尝试初始化日志分析代理...")

        # 为代理准备 LLM 配置，包括工具定义
        # 这是 AutoGen 0.2.x 及更高版本中推荐的工具注册方式
        log_analyzer_llm_config = app_config.get_llm_config()
        log_analyzer_llm_config["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": "analyze_log_entry", # 确保与工具函数名称匹配
                    "description": "分析单个日志条目并返回分析结果。", # LLM 使用的描述
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "log_entry": {
                                "type": "string",
                                "description": "需要分析的日志条目。"
                            }
                        },
                        "required": ["log_entry"]
                    }
                }
            }
        ]
        # "tool_choice": "auto" # 允许LLM自动选择工具
        # 或者强制LLM使用此工具:
        # "tool_choice": {"type": "function", "function": {"name": "analyze_log_entry"}}


        log_analyzer = LogAnalysisAgent(
            name="日志分析员Alpha",
            llm_config=log_analyzer_llm_config
        )
        
        # 关键步骤：将 Python 函数映射到工具名称，以便代理可以执行它
        log_analyzer.register_model_client(model_client=None) # Ensure model client is initialized if not done by llm_config
        log_analyzer.register_function(
            tool_map={
                "analyze_log_entry": analyze_log_entry 
            }
        )

        print(f"日志分析代理 '{log_analyzer.name}' 初始化完成。")
        print(f"系统消息: {log_analyzer.system_message}")
        print(f"已配置工具: analyze_log_entry")

        async def test_agent_analysis():
            sample_log = "Alert: High CPU usage detected on server 'web01'. Value: 95%"
            # 在实际应用中，通常是通过 chat 来让代理决定调用工具
            # response = await user_proxy.a_initiate_chat(log_analyzer, message=f"请分析这个日志: {sample_log}")
            
            # 或者使用我们定义的辅助方法进行直接测试
            print(f"\n使用辅助方法测试日志分析: '{sample_log}'")
            analysis_output = await log_analyzer.analyze_this_log(sample_log)
            print(f"\n分析员 {log_analyzer.name} 的回复:")
            print(analysis_output)

            print("\n--- 测试直接调用包含工具的LLM ---")
            # 更直接地测试工具调用 (模拟代理内部工作流的一部分)
            # 这需要代理已经配置了工具并且 register_function 已经被调用
            try:
                # 创建一个包含工具调用请求的消息
                # 这模拟了LLM决定调用工具的情况
                tool_call_message = {
                    "role": "assistant", 
                    "content": None,
                    "tool_calls": [{
                        "id": "call_abc123",
                        "type": "function",
                        "function": {
                            "name": "analyze_log_entry",
                            "arguments": '{ "log_entry": "Error: Disk space full on /var/log." }'
                        }
                    }]
                }
                
                # 让代理处理这个工具调用请求
                # The `generate_reply` method handles tool calls when the message comes from an "assistant" role with "tool_calls".
                # However, for direct execution testing, it's simpler to use `execute_tool_call` if available or manually call.
                # For AssistantAgent, it processes tool calls in its `a_generate_tool_call_reply` or similar internal methods.
                # The `generate_reply` with a user message that *leads* to a tool call is more representative.
                
                # Let's try a user message that should lead to a tool call
                user_message_for_tool_call = "请使用 analyze_log_entry 工具分析这个日志：'Critical: Unrecognized access attempt from 10.0.0.5'"
                print(f"发送用户消息: {user_message_for_tool_call}")
                
                # `generate_reply` is the method that triggers the agent's thinking process, including tool usage.
                # `sender` is important for context. Here, we can use the agent itself as the sender, or a dummy agent.
                
                # To properly test tool execution, usually it's done in a chat context or by directly invoking
                # methods that handle tool calls if you are testing the tool execution logic itself.
                # The `analyze_this_log` method already provides a good high-level test.
                
                # The `if __name__ == '__main__'` block in `AssistantAgent` itself has more elaborate
                # examples of tool use that could be adapted.

            except Exception as e:
                print(f"直接测试工具调用时发生错误: {e}")


        if app_config.openai_api_key and app_config.openai_api_key != "YOUR_OPENAI_API_KEY_HERE":
            try:
                asyncio.run(test_agent_analysis())
            except Exception as e:
                print(f"运行日志分析代理测试时发生错误: {e}")
        else:
            print("\n跳过日志分析代理的异步测试，因为 OpenAI API 密钥未配置。")

```
