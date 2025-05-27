# -*- coding: utf-8 -*-
import asyncio
import os

from config.config_loader import app_config
from agents.orchestrator_agent import OrchestratorAgent
from agents.log_analysis_agent import LogAnalysisAgent
from agents.user_proxy_agent import SecurityUserProxyAgent
from tools.basic_tools import analyze_log_entry # Tool function

async def main_workflow():
    """
    主工作流程函数，用于演示智能体的基本交互。
    """
    print("开始网络安全事件研判智能体系统演示...")

    # 1. 加载配置并检查 API 密钥
    if not app_config.openai_api_key or app_config.openai_api_key == "YOUR_OPENAI_API_KEY_HERE":
        print("\n错误：OPENAI_API_KEY 未在 config/.env 文件中正确配置。")
        print("请更新 config/.env 文件中的 OPENAI_API_KEY。")
        print("演示需要有效的 API 密钥才能与 LLM 交互并使用工具。")
        return

    print(f"使用模型: {app_config.oai_model_name}")

    # 2. 实例化智能体
    # 用户代理，负责人机交互
    user_proxy = SecurityUserProxyAgent(
        name="安全分析师接口",
        human_input_mode="ALWAYS", # 每次交互都需要用户输入
        code_execution_config=False, # 通常用户代理不执行代码
        description="一个代表人类安全分析师的代理，用于提供输入和接收最终结果。",
    )

    # 日志分析代理，配备了日志分析工具
    log_analyzer_llm_config_raw = app_config.get_llm_config() # Get the raw config dict
    log_analyzer_llm_config_raw["tools"] = [
        {
            "type": "function",
            "function": {
                "name": "analyze_log_entry",
                "description": "分析单个日志条目并返回详细的分析结果。",
                "parameters": { # ... (parameters as before)
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

    # 选择模型客户端实例
    log_analyzer_model_client = None
    if app_config.llm_provider == "ollama" and OllamaChatCompletionClient:
        current_ollama_config = app_config.get_llm_config() # Get fresh config for ollama
        if 'api_base' in current_ollama_config and 'base_url' not in current_ollama_config:
             current_ollama_config['base_url'] = current_ollama_config.pop('api_base')
        log_analyzer_model_client = OllamaChatCompletionClient(**current_ollama_config)
    elif app_config.llm_provider == "openai" or app_config.llm_provider == "zhipu": # Assuming Zhipu is OpenAI compatible for now
        log_analyzer_model_client = OpenAIChatCompletionClient(**app_config.get_llm_config())
    else:
        raise ValueError(f"不支持的 LLM 提供商: {app_config.llm_provider}，无法创建模型客户端。")


    log_analyzer = LogAnalysisAgent(
        name="日志分析专家",
        model_client=log_analyzer_model_client, # Pass the instantiated client
        system_message="你是一名日志分析专家。当给定一个日志条目时，你的任务是使用 'analyze_log_entry' 工具对其进行彻底分析，并清晰地报告分析结果。"
    )
    log_analyzer.llm_config = log_analyzer_llm_config_raw
    
    # 注册实际的Python函数到日志分析代理
    log_analyzer.register_function(
        tool_map={"analyze_log_entry": analyze_log_entry}
    )
    
    # 编排代理
    orchestrator_llm_config_raw = app_config.get_llm_config()
    # orchestrator_llm_config_raw["tools"] = ... # if orchestrator needs tools

    orchestrator_model_client = None
    if app_config.llm_provider == "ollama" and OllamaChatCompletionClient:
        current_ollama_config_orch = app_config.get_llm_config()
        if 'api_base' in current_ollama_config_orch and 'base_url' not in current_ollama_config_orch:
             current_ollama_config_orch['base_url'] = current_ollama_config_orch.pop('api_base')
        orchestrator_model_client = OllamaChatCompletionClient(**current_ollama_config_orch)
    elif app_config.llm_provider == "openai" or app_config.llm_provider == "zhipu":
        orchestrator_model_client = OpenAIChatCompletionClient(**app_config.get_llm_config())
    else:
        raise ValueError(f"不支持的 LLM 提供商: {app_config.llm_provider}，无法为编排器创建模型客户端。")

    orchestrator = OrchestratorAgent(
        name="首席事件编排员",
        model_client=orchestrator_model_client,
        system_message="""你是一位首席AI事件编排员。
        你的职责是理解用户报告的初步安全信息，然后协调其他AI智能体（如日志分析专家）来处理具体任务。
        你需要制定一个高层次的计划，并将具体的分析任务分配给合适的专家。
        当收到分析结果后，你需要汇总信息并呈现给用户。
        如果日志分析专家需要分析日志，请明确指示它使用 'analyze_log_entry' 工具。
        """
    )
    orchestrator.llm_config = orchestrator_llm_config_raw # Pass raw config for reference or tool use

    print("\n智能体初始化完成:")
    print(f"- {user_proxy.name} ({user_proxy.human_input_mode} human input)")
    print(f"- {orchestrator.name}")
    print(f"- {log_analyzer.name} (配备 analyze_log_entry 工具)")

    # 3. 定义群聊和任务管理器 (简化版：两阶段对话)
    # 更复杂的场景会使用 GroupChat 和 GroupChatManager

    # --- 工作流程开始 ---
    print("\n--- 开始模拟安全事件研判工作流程 ---")
    
    # 初始任务：用户报告一个可疑日志
    # initial_log_event = "User 'johndoe' failed to login from IP 172.16.34.58. Error code: 531"
    # print(f"用户报告的初始日志事件: {initial_log_event}")
    
    # 通过 UserProxyAgent 获取用户输入的日志事件
    # user_proxy.get_human_input 将会提示用户输入
    
    # 使用 a_initiate_chat 开始对话
    # 在这个简化流程中，我们让 UserProxy 与 Orchestrator 对话，Orchestrator 再与 LogAnalyzer 对话。
    # AutoGen 的典型多代理交互是基于 GroupChat 的。
    # 这里我们用 initiate_chat 来模拟一个更直接的请求-响应流程，分步进行。

    # 第一阶段: 用户向编排员报告事件
    # 这个消息会由 user_proxy 发送给 orchestrator
    # Orchestrator 会回复，这个回复将是它对任务的理解和初步计划
    
    # 让用户输入一个日志条目
    print("\n请输入一个可疑的日志条目进行分析 (例如: 'Auth: Login failed for user admin from IP 192.168.1.100'):")
    # user_proxy.get_human_input() is synchronous. For an async flow, we'd handle input differently
    # or use user_proxy.a_get_human_input() if available and awaited.
    # For simplicity in a script, we'll take input directly first.
    log_entry_from_user = input("> ")

    if not log_entry_from_user:
        print("未提供日志条目，退出演示。")
        return

    print(f"\n安全分析师接口 ({user_proxy.name}) 收到日志: '{log_entry_from_user}'")
    print("将此日志提交给首席事件编排员进行处理...")

    # 模拟用户代理将任务传递给编排代理
    # 在一个完整的 GroupChat 设置中, user_proxy 会直接把消息发到聊天组里。
    # 这里我们直接调用编排代理。
    
    # 让编排代理制定计划
    # task_for_orchestrator = f"用户报告了一个可疑日志：'{log_entry_from_user}'. 请制定分析计划并协调处理。"
    # orchestrator_plan = await orchestrator.process_task(task_for_orchestrator) # 使用我们之前定义的 process_task
    # print(f"\n{orchestrator.name} 的初步计划或回应:\n{orchestrator_plan}")

    # 第二阶段: 编排员要求日志分析员分析日志
    # 构建一个消息，指示日志分析员执行任务
    # message_for_log_analyzer = f"根据编排计划，请日志分析专家 '{log_analyzer.name}' 分析以下日志条目：'{log_entry_from_user}'。请务必使用 'analyze_log_entry' 工具。"
    
    # 为了演示编排，我们让编排员与日志分析员进行一次 "聊天"
    # UserProxyAgent (acting as initiator) -> Orchestrator (responds, then initiates with LogAnalyzer)
    # For a simpler flow: UserProxy -> Orchestrator -> LogAnalyzer -> Orchestrator -> UserProxy

    # 我们将直接使用 initiate_chat 来展示一个完整的对话流程，
    # 其中 Orchestrator 会与 LogAnalysisAgent 交互 (通过 GroupChat 或直接)。
    # 对于这个简化的 main.py，我们将设置一个包含 Orchestrator 和 LogAnalysisAgent 的聊天。
    # UserProxyAgent 将发起聊天。

    # 创建一个聊天组，包含Orchestrator和LogAnalysisAgent
    # Forcing the order of speakers can be tricky without a proper GroupChatManager or flow control.
    # Let's try a direct instruction flow.

    # UserProxy initiates a chat with the Orchestrator
    await user_proxy.a_initiate_chat(
        recipient=orchestrator,
        message=f"我这里有一个可疑日志需要分析：'{log_entry_from_user}'. 请你来编排处理流程，并让日志分析专家进行分析。",
        max_turns=3 # 限制对话轮次，防止无限循环或过多开销
    )
    
    # 在上面的 initiate_chat 中，理想情况下：
    # 1. UserProxy 发送消息给 Orchestrator。
    # 2. Orchestrator (LLM) 理解任务，决定需要 LogAnalysisAgent。
    # 3. Orchestrator (LLM) 生成一条消息给 LogAnalysisAgent，指示它分析日志并使用工具。
    #    (这需要 Orchestrator 的 system_message 和 prompt 能够引导它这样做，
    #     或者 GroupChatManager 能够根据 Orchestrator 的回复路由到 LogAnalysisAgent)
    # 4. LogAnalysisAgent (LLM) 接收到指令，调用 analyze_log_entry 工具。
    # 5. 工具执行，结果返回给 LogAnalysisAgent (LLM)。
    # 6. LogAnalysisAgent (LLM) 将工具结果格式化为回复。
    # 7. 此回复返回给 Orchestrator (LLM)。
    # 8. Orchestrator (LLM) 收到分析结果，可能进行总结，然后回复给 UserProxy。
    # 9. UserProxy 收到最终结果并展示。

    # 为了让上述流程更可靠地发生，通常需要更复杂的 GroupChat 设置，
    # 包括明确的 speaker_selection_method，或者让 Orchestrator 能够直接调用其他代理。
    # AssistantAgent 可以通过 GroupChat 与其他代理通信。

    # 另一种方法是，编排员接收任务，然后在其内部逻辑中直接调用（或发起与）日志分析员的对话。
    # orchestrator_response_to_user = await orchestrator.a_generate_reply(...)
    # if "analyze_log" in orchestrator_response_to_user:
    #    await orchestrator.a_initiate_chat(log_analyzer, message=...)
    
    # 对于此步骤，上面的 a_initiate_chat 是一个起点。
    # 确保 Orchestrator 的 system_message 鼓励它在回复中包含调用 LogAnalysisAgent 的指令。
    # 并且 LogAnalysisAgent 在接收到这样的指令时，其 system_message 引导它使用工具。

    print("\n--- 工作流程结束 ---")
    print("请检查上面的对话历史。")
    print("如果API密钥有效且LLM配置正确，您应该能看到代理之间的交互以及工具的使用。")

if __name__ == "__main__":
    try:
        asyncio.run(main_workflow())
    except Exception as e:
        print(f"运行主工作流程时发生意外错误: {e}")
        import traceback
        traceback.print_exc()
