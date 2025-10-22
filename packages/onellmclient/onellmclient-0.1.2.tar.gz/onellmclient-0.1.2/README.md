# onellmclient

统一主要 LLM 提供商接口的 Python 客户端，让你用一套 API 调用 OpenAI、Anthropic、Gemini、DeepSeek 等不同厂商的模型。

## ✨ 特性

- **统一接口**：一套 API 调用多个 LLM 厂商，无需学习不同 SDK
- **开箱即用**：一次安装，支持所有主流 LLM 提供商（OpenAI、Anthropic、Gemini、DeepSeek）
- **透明切换**：随时切换不同的模型提供商，代码几乎无需改动
- **完整功能**：支持文本生成、工具调用、结构化输出等核心功能

## 📦 安装

```bash
# 使用 uv（推荐）
uv add onellmclient

# 或使用 pip
pip install onellmclient
```

**注意**：安装 `onellmclient` 会自动安装所有支持的 LLM 提供商 SDK（OpenAI、Anthropic、Gemini），DeepSeek 使用 OpenAI 兼容的 API，无需额外依赖。

## 🚀 快速开始

### 基础用法

```python
from onellmclient import Client

# 初始化客户端（支持多个厂商）
client = Client(
    openai={"key": "your-openai-api-key"},
    anthropic={"key": "your-anthropic-api-key"},
    gemini={"key": "your-gemini-api-key"},
    deepseek={"key": "your-deepseek-api-key"}
)

# 调用 OpenAI 模型
response = client.completion(
    provider="openai",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "你好，请介绍一下自己"}]
)
print(response.content)

# 切换到 Anthropic 模型，代码几乎不变
response = client.completion(
    provider="anthropic",
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": "你好，请介绍一下自己"}]
)
print(response.content)

# 切换到 DeepSeek 模型，同样简单
response = client.completion(
    provider="deepseek",
    model="deepseek-v3.2-exp",
    messages=[{"role": "user", "content": "你好，请介绍一下自己"}]
)
print(response.content)
```

### 高级功能

#### 结构化输出

```python
# 定义 JSON Schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "hobbies": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["name", "age"]
}

response = client.completion(
    provider="openai",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "请介绍一个虚构的人物"}],
    schema=schema
)
# response.content 将是一个符合 schema 的 JSON 字符串
```

#### 工具调用

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
            }
        }
    }
]

response = client.completion(
    provider="openai",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
    tools=tools
)
```

#### 推理能力（Claude）

```python
response = client.completion(
    provider="anthropic",
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": "解这个数学题：2x + 5 = 13"}],
    reasoning_effort="medium"  # off, minimal, low, medium, high
)
```

## 📋 支持的厂商和模型

| 厂商 | 支持的模型 | 特殊功能 |
|------|------------|----------|
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-4, gpt-3.5-turbo 等 | 结构化输出、工具调用、网络搜索 |
| **Anthropic** | claude-3-5-sonnet, claude-3-opus, claude-3-haiku 等 | 推理能力、工具调用 |
| **Gemini** | gemini-1.5-pro, gemini-1.5-flash 等 | 工具调用 |
| **DeepSeek** | deepseek-v3.2-exp, deepseek-chat 等 | 结构化输出、工具调用 |

## 🔧 API 参考

### Client 初始化

```python
Client(
    openai={"key": "api-key", "base": "https://api.openai.com/v1"},     # 可选
    anthropic={"key": "api-key", "base": "https://api.anthropic.com"}, # 可选
    gemini={"key": "api-key", "base": "https://generativelanguage.googleapis.com"}, # 可选
    deepseek={"key": "api-key", "base": "https://api.deepseek.com"}    # 可选
)
```

### completion 方法

```python
client.completion(
    provider: str,                    # "openai", "anthropic", "gemini", "deepseek"
    model: str,                       # 模型名称
    messages: List[Dict],             # 消息列表
    instructions: Optional[str],      # 系统指令
    schema: Optional[Dict],           # JSON Schema（结构化输出）
    tools: Optional[List[Dict]],      # 工具定义
    reasoning_effort: Optional[str],  # 推理能力："off", "minimal", "low", "medium", "high"
    temperature: Optional[float],     # 温度参数 0-2
    web_search: bool,                 # 是否启用网络搜索（仅 OpenAI）
    tool_choice: Optional[str]        # 工具选择策略："auto", "none", "required"
)
```

## 💡 最佳实践

1. **环境变量管理**：将 API 密钥存储在环境变量中
```python
import os
client = Client(
    openai={"key": os.getenv("OPENAI_API_KEY")},
    anthropic={"key": os.getenv("ANTHROPIC_API_KEY")},
    deepseek={"key": os.getenv("DEEPSEEK_API_KEY")}
)
```

2. **错误处理**：捕获特定异常
```python
try:
    response = client.completion(provider="openai", model="gpt-4", messages=[...])
except ValueError as e:
    print(f"配置错误: {e}")
```

3. **模型切换**：为不同场景选择合适的模型
```python
# 快速响应场景
response = client.completion(provider="openai", model="gpt-4o-mini", messages=[...])

# 复杂推理场景
response = client.completion(provider="anthropic", model="claude-3-5-sonnet", messages=[...], reasoning_effort="high")
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 开源协议

MIT License
