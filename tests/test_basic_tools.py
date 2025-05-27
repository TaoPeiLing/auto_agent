# -*- coding: utf-8 -*-
import unittest
from tools.basic_tools import analyze_log_entry

class TestBasicTools(unittest.TestCase):
    """
    测试基础工具 (tools/basic_tools.py) 的功能。
    """

    def test_analyze_log_entry_login_failed(self):
        """
        测试 analyze_log_entry 处理登录失败日志。
        """
        log = "Auth: Login failed for user 'testuser' from IP 192.168.1.100"
        result = analyze_log_entry(log)
        self.assertIn("检测到登录失败事件", result)
        self.assertIn("来自可疑IP 192.168.1.100", result) # 根据工具中的特定逻辑

    def test_analyze_log_entry_error(self):
        """
        测试 analyze_log_entry 处理错误日志。
        """
        log = "System Error: servicio 'core_dump' failed to start."
        result = analyze_log_entry(log)
        self.assertIn("检测到错误事件", result)

    def test_analyze_log_entry_warning(self):
        """
        测试 analyze_log_entry 处理警告日志。
        """
        log = "Warning: Disk space is running low on /dev/sda1."
        result = analyze_log_entry(log)
        self.assertIn("检测到警告事件", result)

    def test_analyze_log_entry_normal(self):
        """
        测试 analyze_log_entry 处理普通日志。
        """
        log = "Info: User 'jane_doe' accessed resource '/api/data'."
        result = analyze_log_entry(log)
        self.assertIn("未检测到特定模式", result)
        self.assertIn("常规信息", result)

    def test_analyze_log_entry_empty(self):
        """
        测试 analyze_log_entry 处理空日志条目。
        """
        log = ""
        result = analyze_log_entry(log)
        # 根据实际实现，空字符串可能被视为“常规信息”或有特定处理
        self.assertIn("未检测到特定模式", result) 

if __name__ == '__main__':
    unittest.main()
