# -*- coding: utf-8 -*-
from autogen import UserProxyAgent
from typing import Optional, Dict, Any

class SecurityUserProxyAgent(UserProxyAgent):
    """
    用户代理 (UserProxyAgent) 的安全特定版本。
    负责人机交互，例如获取用户输入、请求批准或向用户展示结果。
    """
    def __init__(
        self, 
        name: str, 
        human_input_mode: str = "TERMINATE", 
        max_consecutive_auto_reply: Optional[int] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        初始化安全用户代理。

        参数:
            name (str): 代理的名称。
            human_input_mode (str): 用户输入模式。默认为 "TERMINATE"，表示在收到用户输入后终止对话。
                                   其他选项可以是 "ALWAYS" (总是需要用户输入) 或 "NEVER" (从不寻求用户输入)。
            max_consecutive_auto_reply (Optional[int]): 代理在需要用户输入之前可以自动回复的最大次数。
            llm_config (Optional[Dict[str, Any]]): LLM 配置 (如果此代理需要使用 LLM 生成回复)。
                                                  对于标准 UserProxyAgent，通常不需要 LLM。
            **kwargs: 其他传递给 UserProxyAgent 的参数。
        """
        super().__init__(
            name,
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            llm_config=llm_config,
            # code_execution_config=False by default for UserProxyAgent, 
            # but can be enabled if needed for specific security tasks like running verification scripts.
            # For a basic setup, we'll keep it simple.
            **kwargs
        )
        # 可以在这里添加特定的初始化逻辑

# 示例用法 (通常在 main.py 或测试文件中进行)
if __name__ == '__main__':
    # 此部分仅用于演示 UserProxyAgent 的基本初始化和一些功能
    # 通常 UserProxyAgent 会在与其他代理的聊天中使用

    # 初始化用户代理
    user_proxy = SecurityUserProxyAgent(
        name="安全事件分析员",
        human_input_mode="ALWAYS", # 要求用户始终提供输入
        code_execution_config=False # 通常用户代理不执行代码，除非特定场景
    )

    print(f"用户代理 '{user_proxy.name}' 初始化完成。")
    print(f" - 输入模式: {user_proxy.human_input_mode}")
    print(f" - 最大自动回复次数: {user_proxy.max_consecutive_auto_reply}")

    # 模拟接收消息并获取用户输入
    # 在实际应用中，这是在 agent.receive() 和 agent.get_human_input() 内部处理的
    # message_to_analyst = "发现一个来自IP 192.168.1.100 的可疑登录尝试。需要分析吗？"
    # reply = user_proxy.get_human_input(f"分析师，请对以下情况作出回应: {message_to_analyst}")
    # print(f"分析师的回应: {reply}")

    # 注意: get_human_input 是一个同步方法。
    # AutoGen 的核心交互是异步的。这里仅为简单演示。
    # 要运行一个完整的聊天，你需要设置一个异步事件循环并使用 agent.a_initiate_chat() 等。

    print("\nUserProxyAgent 主要用于多智能体对话中，以代表用户。")
    print("它通常通过 initiate_chat 或作为回复者参与对话。")
