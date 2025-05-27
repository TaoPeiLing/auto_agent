# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path, override=True)
else:
    print(f"警告: 配置文件 {dotenv_path} 未找到。将依赖系统环境变量。")

class AppConfig:
    def __init__(self):
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "openai").lower()

        # OpenAI settings
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY")
        self.openai_model_name: str = os.getenv("OAI_MODEL_NAME", "gpt-3.5-turbo")
        self.openai_api_base: str = os.getenv("OPENAI_API_BASE") 

        # Ollama settings
        self.ollama_api_base: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        self.ollama_model_name: str = os.getenv("OLLAMA_MODEL_NAME", "llama3") # Default if not in .env
        # self.ollama_context_window: int = int(os.getenv("OLLAMA_CONTEXT_WINDOW", "0")) # Example if we add context window

        # ZhipuAI settings
        self.zhipu_api_key: str = os.getenv("ZHIPU_API_KEY")
        self.zhipu_model_name: str = os.getenv("ZHIPU_MODEL_NAME", "glm-4") # Default if not in .env
        self.zhipu_api_base: str = os.getenv("ZHIPU_API_BASE") 

        self._validate_config()

    def _validate_config(self):
        if self.llm_provider == "openai":
            if not self.openai_api_key or self.openai_api_key == "YOUR_OPENAI_API_KEY_HERE":
                print("警告：LLM_PROVIDER 设置为 'openai'，但 OPENAI_API_KEY 未配置或仍为占位符。")
        elif self.llm_provider == "ollama":
            if not self.ollama_model_name:
                print("警告：LLM_PROVIDER 设置为 'ollama'，但 OLLAMA_MODEL_NAME 未配置。")
        elif self.llm_provider == "zhipu":
            if not self.zhipu_api_key or self.zhipu_api_key == "c859bf3bcec5fbcf4b5897a2c3dc9a6e.hS8pVPUzEJNLinwo" or self.zhipu_api_key == "YOUR_ZHIPU_API_KEY_HERE": # Updated placeholder check
                # This check is a bit tricky if the actual key can be the placeholder value.
                # Better to rely on user knowing if it's a real key.
                pass # Assuming user has put a real key if it's not the default placeholder
            if not self.zhipu_model_name:
                print("警告：LLM_PROVIDER 设置为 'zhipu'，但 ZHIPU_MODEL_NAME 未配置。")

    def get_llm_config(self) -> dict:
        llm_config = {}

        if self.llm_provider == "openai":
            api_key_to_use = self.openai_api_key if (self.openai_api_key and self.openai_api_key != "YOUR_OPENAI_API_KEY_HERE") else None
            if not api_key_to_use:
                print("警告：OpenAI API 密钥未在 .env 中正确配置。AutoGen 将尝试从环境变量 OPENAI_API_KEY 读取。")
            
            llm_config = {
                "model": self.openai_model_name,
                "api_key": api_key_to_use,
            }
            if self.openai_api_base:
                llm_config["base_url"] = self.openai_api_base

        elif self.llm_provider == "ollama":
            if not self.ollama_model_name:
                raise ValueError("OLLAMA_MODEL_NAME 未在 .env 文件中配置，但 LLM_PROVIDER 设置为 'ollama'。")
            
            llm_config = {
                "model": self.ollama_model_name,
                "base_url": self.ollama_api_base, 
                "api_key": "ollama", 
                # if self.ollama_context_window > 0:
                #    llm_config["max_tokens"] = self.ollama_context_window # Or appropriate param name
            }

        elif self.llm_provider == "zhipu":
            if not self.zhipu_api_key or self.zhipu_api_key == "YOUR_ZHIPU_API_KEY_HERE":
                 raise ValueError("ZHIPU_API_KEY 未在 .env 文件中正确配置，但 LLM_PROVIDER 设置为 'zhipu'。")
            if not self.zhipu_model_name:
                raise ValueError("ZHIPU_MODEL_NAME 未在 .env 文件中配置，但 LLM_PROVIDER 设置为 'zhipu'。")

            llm_config = {
                "model": self.zhipu_model_name,
                "api_key": self.zhipu_api_key,
            }
            # If ZhipuAI uses a specific base_url for its OpenAI-compatible API, add it.
            # This is often needed if their SDK doesn't default to it or if we are using a generic OpenAI client.
            if self.zhipu_api_base:
                llm_config["base_url"] = self.zhipu_api_base
        
        else:
            print(f"警告：未知的 LLM_PROVIDER '{self.llm_provider}'。将返回空配置。")
        
        return llm_config

app_config = AppConfig()

if __name__ == '__main__':
    print("测试加载配置 (增强版):")
    print(f"  LLM Provider: {app_config.llm_provider}")

    if app_config.llm_provider == "openai":
        # ... (OpenAI print logic as before)
        if app_config.openai_api_key and app_config.openai_api_key != "YOUR_OPENAI_API_KEY_HERE":
            print(f"  OpenAI API 密钥: {'*' * 10 + app_config.openai_api_key[-4:]}")
        else:
            print("  OpenAI API 密钥: 未配置或占位符。")
        print(f"  OpenAI 模型名称: {app_config.openai_model_name}")
        if app_config.openai_api_base:
            print(f"  OpenAI API Base: {app_config.openai_api_base}")

    elif app_config.llm_provider == "ollama":
        print(f"  Ollama Configured API Base (from OLLAMA_API_BASE env): {app_config.ollama_api_base}")
        print(f"  Ollama 模型名称: {app_config.ollama_model_name}")

    elif app_config.llm_provider == "zhipu":
        if app_config.zhipu_api_key and app_config.zhipu_api_key != "YOUR_ZHIPU_API_KEY_HERE": # Check against default placeholder
             print(f"  ZhipuAI API 密钥: {'*' * 10 + app_config.zhipu_api_key[-4:] if app_config.zhipu_api_key else '未配置'}")
        else:
             print("  ZhipuAI API 密钥: 未配置或占位符。")
        print(f"  ZhipuAI 模型名称: {app_config.zhipu_model_name}")
        if app_config.zhipu_api_base:
            print(f"  ZhipuAI API Base: {app_config.zhipu_api_base}")

    llm_settings = app_config.get_llm_config()
    print(f"\n  生成的 LLM 配置 (用于 AutoGen for {app_config.llm_provider}):")
    for key, value in llm_settings.items():
        if key == "api_key" and value and isinstance(value, str) and len(value) > 4 : # Check type and length
            print(f"    {key.capitalize()}: {'*' * 10 + value[-4:]}")
        else:
            print(f"    {key.capitalize()}: {value}")
    
    if not os.path.exists(dotenv_path):
        print(f"\n警告: {dotenv_path} 文件未找到。")
