# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

# 构建 .env 文件的路径，该文件应该在 config 目录中
# __file__ 是当前 config_loader.py 文件的路径
# os.path.dirname(__file__) 是 config_loader.py 所在的目录 (即 config 目录)
# os.path.join(...) 会正确地将它们连接起来
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# 加载 .env 文件中的环境变量
# 如果 .env 文件不存在，load_dotenv 不会报错，但变量不会被加载
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path, override=True) # override=True 允许覆盖已存在的系统环境变量
    # print(f"已从 {dotenv_path} 加载配置。") # 用于调试
else:
    # print(f"警告: 配置文件 {dotenv_path} 未找到。将依赖系统环境变量。") # 用于调试
    pass


class AppConfig:
    """
    应用程序配置类。
    从环境变量加载和提供配置参数。
    """
    def __init__(self):
        # 从环境变量获取配置，如果未设置则提供默认值或 None
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY")
        self.oai_model_name: str = os.getenv("OAI_MODEL_NAME", "gpt-3.5-turbo") # 提供一个默认模型

        # 可以在这里添加更多的配置参数
        # self.another_api_key: str = os.getenv("ANOTHER_API_KEY")

    def get_llm_config(self) -> dict:
        """
        为 AutoGen 代理生成 LLM 配置字典。
        确保 API 密钥已配置。
        """
        if not self.openai_api_key or self.openai_api_key == "YOUR_OPENAI_API_KEY_HERE":
            # 如果用户忘记替换占位符，也视为未配置
            # print("错误：OPENAI_API_KEY 未在 .env 文件中配置或仍然是占位符。") # 用于调试
            # raise ValueError("OPENAI_API_KEY 未在 .env 文件中正确配置。请检查 config/.env 文件。")
            # 对于 AssistantAgent，如果 llm_config 中的 api_key 为 None 或未提供，它会尝试从环境变量直接读取
            # 所以这里返回 None 也是一种策略，让 AutoGen 自己处理
            return {
                "model": self.oai_model_name,
                "api_key": None, # 让 AssistantAgent 尝试从 os.environ.get("OPENAI_API_KEY") 读取
            }
        
        return {
            "model": self.oai_model_name,
            "api_key": self.openai_api_key,
            # "timeout": 600, # 可选：添加超时等参数
            # "cache_seed": 42, # 可选：用于可复现的 LLM 调用
        }

# 创建一个全局配置实例，方便在其他模块中导入和使用
# 例如: from config.config_loader import app_config
# api_key = app_config.openai_api_key
# llm_config = app_config.get_llm_config()
app_config = AppConfig()

if __name__ == '__main__':
    # 此部分用于测试 config_loader.py 是否能正确加载配置
    print("测试加载配置:")
    if app_config.openai_api_key and app_config.openai_api_key != "YOUR_OPENAI_API_KEY_HERE":
        print(f"  OpenAI API 密钥: {'*' * 10}{app_config.openai_api_key[-4:]}") # 打印部分密钥以确认加载
    else:
        print("  OpenAI API 密钥: 未配置或仍为占位符。")
    
    print(f"  OpenAI 模型名称: {app_config.oai_model_name}")
    
    llm_settings = app_config.get_llm_config()
    print("  生成的 LLM 配置 (用于 AutoGen):")
    if llm_settings.get("api_key"):
        print(f"    API Key: {'*' * 10}{llm_settings['api_key'][-4:]}")
    else:
        print(f"    API Key: 未提供 (AutoGen 将尝试从环境变量 OPENAI_API_KEY 读取)")
    print(f"    Model: {llm_settings['model']}")

    if not os.path.exists(dotenv_path):
        print(f"\n警告: {dotenv_path} 文件未找到。")
        print("请确保在 'config' 目录下创建 '.env' 文件并填入您的 API 密钥。")
        print("示例 .env 内容:")
        print("OPENAI_API_KEY=\"sk-xxxxxxxxxxxxxxxxxxxx\"")
        print("OAI_MODEL_NAME=\"gpt-4\"")
