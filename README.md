# AutoGen Security Event Analysis System (AutoGen 安全事件研判系统)

## 项目简介与目标 (Project Description and Goals)

本项目旨在使用 [AutoGen](https://github.com/microsoft/autogen) 框架构建一个智能代理系统，用于网络安全事件的自动化分析和研判。系统的目标是通过多智能体协作，结合大型语言模型 (LLM) 的能力和专业的安全工具，实现对安全事件的快速响应、深入分析和辅助决策。

参考架构思想来源于 [Magentic-UI](https://deepwiki.com/microsoft/magentic-ui/)，强调编排、专业分工和人机协同。

## 系统配置 (Configuration)

系统的大部分配置通过项目根目录下的 `config/.env` 文件进行管理。在首次运行前，您需要手动创建此文件。

### 1. 创建 `config/.env` 文件

在 `config` 目录下创建一个名为 `.env` 的文件。 (用户已手动创建此文件)

### 2. 配置内容示例与说明

将以下内容复制到 `config/.env` 中，并根据您的实际情况修改：

```env
# LLM Provider: "openai", "ollama", "zhipu"
# 选择您希望使用的LLM提供商
LLM_PROVIDER="zhipu" 

# OpenAI Configuration
OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE" 
OAI_MODEL_NAME="gpt-4" 
OPENAI_API_BASE="" # 可选：自定义的OpenAI兼容接口地址或代理

# Ollama Configuration
OLLAMA_API_BASE="http://localhost:11434" # 您的Ollama服务API地址
OLLAMA_MODEL_NAME="llama3" # 您在Ollama中已拉取的模型名称，例如 "qwen2:7b", "llama3"

# ZhipuAI Configuration (智谱AI)
ZHIPU_API_KEY="YOUR_ZHIPU_API_KEY_HERE" # 您的智谱AI API Key
ZHIPU_MODEL_NAME="glm-4" # 您希望使用的智谱AI模型
ZHIPU_API_BASE="https://open.bigmodel.cn/api/paas/v4/" # 智谱AI的API Endpoint
```

**关键配置项说明:**

*   `LLM_PROVIDER`: 指定当前激活的LLM提供商。有效值为:
    *   `"openai"`: 使用 OpenAI 的模型。
    *   `"ollama"`: 使用本地运行的 Ollama 模型。
    *   `"zhipu"`: 使用智谱AI的模型。
*   **OpenAI**:
    *   `OPENAI_API_KEY`: 您的 OpenAI API 密钥。
    *   `OAI_MODEL_NAME`: 您希望使用的 OpenAI 模型名称 (例如 `gpt-4`, `gpt-3.5-turbo`)。
    *   `OPENAI_API_BASE` (可选): 如果您通过代理或自定义端点访问OpenAI服务，请设置此项。
*   **Ollama**:
    *   `OLLAMA_API_BASE`: 您本地Ollama服务的地址 (通常是 `http://localhost:11434`，如果您在其他机器或端口运行，请修改)。
    *   `OLLAMA_MODEL_NAME`: 您已经在Ollama中下载并希望使用的模型名称 (例如 `llama3`, `mistral`, `qwen2:7b`)。
*   **ZhipuAI (智谱AI)**:
    *   `ZHIPU_API_KEY`: 您的智谱AI API Key。
    *   `ZHIPU_MODEL_NAME`: 您希望使用的智谱模型 (例如 `glm-4`, `glm-3-turbo`)。
    *   `ZHIPU_API_BASE`: 智谱AI的API服务地址。

**请确保根据您选择的 `LLM_PROVIDER` 填写了正确的API密钥和模型信息。**

## 依赖安装 (Dependencies)

本项目依赖的 Python 包记录在 `requirements.txt` 文件中。请通过以下命令安装：

```bash
pip install -r requirements.txt
```
主要依赖包括 `autogen-agentchat`, `autogen-ext[ollama]`, `autogen-ext[openai]`, 和 `python-dotenv`。

## 如何运行 (How to Run)

配置好 `config/.env` 文件并安装完依赖后，您可以通过以下命令运行主程序：

```bash
python main.py
```
程序将启动，并根据 `.env` 中的配置初始化相应的LLM和代理。您将被提示输入一个可疑的日志条目进行分析。

## 项目结构 (Project Structure)

*   `agents/`: 包含各个AutoGen智能体的定义 (例如编排代理, 日志分析代理)。
*   `tools/`: 包含可供智能体使用的工具函数 (例如日志条目分析工具)。
*   `config/`: 包含配置文件 (`.env`) 和配置加载逻辑 (`config_loader.py`)。
*   `data/`: (规划中) 可以用于存放输入数据样本、输出报告等。
*   `tests/`: 包含单元测试和集成测试。
*   `main.py`: 项目的主入口点，演示基本的工作流程。
*   `workflows/`: (规划中) 用于定义更复杂的智能体协作流程。

```
