# -*- coding: utf-8 -*-
import unittest
import os
from unittest.mock import patch

# 在导入 app_config 之前，可能需要设置一些环境变量或模拟 .env 文件
# 以确保测试的隔离性和可重复性。

class TestConfigLoader(unittest.TestCase):
    """
    测试配置加载器 (config/config_loader.py) 的功能。
    """

    def setUp(self):
        """
        在每个测试方法运行前设置环境。
        """
        # 保存原始环境变量值（如果存在）
        self.original_api_key = os.environ.get("OPENAI_API_KEY")
        self.original_model_name = os.environ.get("OAI_MODEL_NAME")
        
        # 清除环境变量，以便测试 .env 文件加载或默认值
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "OAI_MODEL_NAME" in os.environ:
            del os.environ["OAI_MODEL_NAME"]

        # 模拟一个 .env 文件在 config 目录中
        self.mock_env_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env.test_temp')
        with open(self.mock_env_path, 'w', encoding='utf-8') as f:
            f.write("OPENAI_API_KEY=test_api_key_from_file\n")
            f.write("OAI_MODEL_NAME=test_model_from_file\n")
        
        # Patch 'dotenv_path' 在 config_loader 模块内部指向我们的测试 .env 文件
        # 需要在导入 app_config 之前 patch，或者重新加载模块
        self.dotenv_patcher = patch('config.config_loader.dotenv_path', self.mock_env_path)
        self.dotenv_patcher.start()
        
        # 动态导入或重新加载 app_config 以确保它使用 mock 的 .env 文件
        # 这是因为 app_config 是在模块加载时实例化的
        import importlib
        import config.config_loader
        importlib.reload(config.config_loader)
        self.app_config = config.config_loader.app_config


    def tearDown(self):
        """
        在每个测试方法运行后清理环境。
        """
        # 恢复原始环境变量
        if self.original_api_key is not None:
            os.environ["OPENAI_API_KEY"] = self.original_api_key
        elif "OPENAI_API_KEY" in os.environ: # 如果测试中设置了但原来没有
            del os.environ["OPENAI_API_KEY"]

        if self.original_model_name is not None:
            os.environ["OAI_MODEL_NAME"] = self.original_model_name
        elif "OAI_MODEL_NAME" in os.environ:
            del os.environ["OAI_MODEL_NAME"]
        
        # 停止 patch 并删除模拟的 .env 文件
        self.dotenv_patcher.stop()
        if os.path.exists(self.mock_env_path):
            os.remove(self.mock_env_path)
        
        # 恢复原始的 dotenv_path (通过重新加载模块)
        import importlib
        import config.config_loader
        importlib.reload(config.config_loader)


    def test_load_from_mock_env_file(self):
        """
        测试是否能从模拟的 .env 文件加载配置。
        """
        self.assertEqual(self.app_config.openai_api_key, "test_api_key_from_file")
        self.assertEqual(self.app_config.oai_model_name, "test_model_from_file")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_api_key_env_var", "OAI_MODEL_NAME": "test_model_env_var"})
    def test_load_from_environment_variables_override(self):
        """
        测试环境变量是否会覆盖 .env 文件（如果 load_dotenv 的 override=True）。
        注意：AppConfig 在初始化时直接使用 os.getenv，
        而 load_dotenv(override=True) 会更新 os.environ。
        所以这里我们直接 patch os.environ 来模拟环境变量优先。
        """
        import importlib
        import config.config_loader
        # 重新加载模块以使 AppConfig 实例获取最新的 patched 环境变量
        importlib.reload(config.config_loader) 
        reloaded_app_config = config.config_loader.app_config
        
        self.assertEqual(reloaded_app_config.openai_api_key, "test_api_key_env_var")
        self.assertEqual(reloaded_app_config.oai_model_name, "test_model_env_var")

    def test_get_llm_config_with_key(self):
        """
        测试 get_llm_config 方法在 API 密钥存在时是否正确返回。
        """
        expected_llm_config = {
            "model": "test_model_from_file",
            "api_key": "test_api_key_from_file",
        }
        self.assertEqual(self.app_config.get_llm_config(), expected_llm_config)

    @patch.dict(os.environ, {}, clear=True) # 清除所有环境变量
    def test_get_llm_config_without_key(self):
        """
        测试 get_llm_config 方法在 API 密钥不存在时的行为。
        它应该返回 api_key 为 None，让 AutoGen 尝试从环境变量加载。
        """
        # 确保 .env 文件也不存在或不包含密钥
        if os.path.exists(self.mock_env_path):
            os.remove(self.mock_env_path)

        import importlib
        import config.config_loader
        importlib.reload(config.config_loader) # 重新加载以确保 AppConfig 初始化时密钥不存在
        reloaded_app_config_no_key = config.config_loader.app_config

        expected_llm_config = {
            "model": "gpt-3.5-turbo", # 默认模型
            "api_key": None,
        }
        self.assertEqual(reloaded_app_config_no_key.get_llm_config(), expected_llm_config)
        self.assertIsNone(reloaded_app_config_no_key.openai_api_key)


if __name__ == '__main__':
    unittest.main()
