# -*- coding: utf-8 -*-
from autogen import AssistantAgent
from typing import Optional, Dict, Any

class OrchestratorAgent(AssistantAgent):
    """
    编排代理 (OrchestratorAgent)
    负责接收任务、制定初步计划并将任务分配给其他专业代理。
    """
    def __init__(self, name: str, llm_config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        初始化编排代理。

        参数:
            name (str): 代理的名称。
            llm_config (Optional[Dict[str, Any]]): LLM 配置。
                           如果为 None，则代理将尝试从环境变量加载。
            **kwargs: 其他传递给 AssistantAgent 的参数。
        """
        super().__init__(name, llm_config=llm_config, **kwargs)
        # 可以在这里添加特定的初始化逻辑，例如加载预设的指令

    async def process_task(self, task_description: str) -> str:
        """
        处理传入的任务描述。

        参数:
            task_description (str): 用户或系统提供的任务描述。

        返回:
            str: 一个表示初步计划或下一步行动的字符串。
        """
        # 目前只是一个简单的实现，后续会扩展
        system_message = f"""你是一个AI编排者。
        你的职责是根据用户提供的任务描述，将其分解为一系列可执行的步骤。
        然后协调其他AI智能体来完成这些步骤。
        用户提供的任务是：{task_description}
        
        请为这个任务制定一个高层次的计划。
        """
        
        # 发送消息给自己 (或其他代理) 来生成计划
        # 注意：在实际的多代理设置中，这里可能会与 GroupChat 或其他代理交互
        response = await self.generate_reply(
            messages=[{"role": "user", "content": system_message}],
            sender=self # 代理本身作为发送者
        )
        
        plan = response if isinstance(response, str) else response.get("content", "")
        
        # 打印或记录计划
        print(f"编排代理 {self.name} 制定的计划: {plan}")
        return plan

# 可以在此文件底部添加一个简单的测试或示例用法，但这通常在 main.py 或测试文件中完成
if __name__ == '__main__':
    # 此部分仅用于基本测试，实际应用中LLM配置会更复杂且从外部加载
    # 需要设置 OPENAI_API_KEY 环境变量才能运行此示例
    import asyncio
    import os

    # 注意：运行此示例需要有效的 LLM 配置。
    # 请确保设置了 OPENAI_API_KEY 环境变量，或者提供了 llm_config 字典。
    # llm_config_example = {
    #     "model": "gpt-3.5-turbo", # 或者 "gpt-4" 等
    #     "api_key": os.environ.get("OPENAI_API_KEY"),
    # }
    
    # 检查 API 密钥是否存在
    if not os.environ.get("OPENAI_API_KEY"):
        print("错误：OPENAI_API_KEY 环境变量未设置。请设置该变量后重试。")
    else:
        print("OPENAI_API_KEY 已找到。尝试初始化代理...")
        orchestrator = OrchestratorAgent(
            name="首席编排者",
            # llm_config=llm_config_example # 如果上面取消注释 llm_config_example，则使用它
            # 如果 llm_config 未提供，AssistantAgent 会尝试从环境变量加载
        )

        async def test_process_task():
            task = "分析一个可疑的登录行为，并确定其是否为恶意。"
            print(f"测试任务: {task}")
            generated_plan = await orchestrator.process_task(task)
            print(f"从 process_task 收到的计划: {generated_plan}")

        try:
            asyncio.run(test_process_task())
        except Exception as e:
            print(f"运行测试时发生错误: {e}")
