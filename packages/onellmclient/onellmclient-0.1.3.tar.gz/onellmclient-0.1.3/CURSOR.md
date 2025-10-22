# CURSOR.md

统一LLM接口客户端

## 技术架构
- 语言：Python 3.9+
- 构建：hatchling（PEP 517/518）
- 环境管理：uv（推荐）
- 包布局：`src/` 结构

## 技术关键点

### Provider 适配器模式
每个 LLM 提供商都有独立的适配器文件 (`provider/` 目录)，负责：
1. **消息格式转换**：将统一的消息格式转换为各供应商的特定格式
2. **工具定义转换**：将统一的工具定义转换为各供应商的 schema 格式
3. **响应转换**：将各供应商的响应格式转换回统一格式
4. **Payload 构建**：构建符合各供应商 API 规范的请求负载

#### 各 Provider 文件的主要函数：

**openai.py**:
- `openai_payload()` - 构建 OpenAI API 请求负载
- `openai_messages()` - 消息格式转换
- `openai_tools()` - 工具定义转换
- `openai_json_schema()` - JSON schema 处理
- `openai_response_convert()` - 响应转换

**anthropic.py**:
- `anthropic_payload()` - 构建 Anthropic API 请求负载
- `anthropic_messages()` - 消息格式转换
- `anthropic_tools()` - 工具定义转换
- `anthropic_response_convert()` - 响应转换

**gemini.py**:
- `gemini_payload()` - 构建 Gemini API 请求负载
- `gemini_messages()` - 消息格式转换
- `gemini_tools()` - 工具定义转换
- `gemini_response_convert()` - 响应转换

**deepseek.py**:
- `deepseek_completion_payload()` - 构建 DeepSeek API 请求负载
- 复用 OpenAI 的工具转换逻辑 (`openai_completion_tools()`)
- 支持 JSON schema 格式响应
- 不支持 `reasoning_effort` 和 `web_search` 参数

**xai.py**:
- `xai_payload()` - 构建 xAI API 请求负载
- `xai_tools()` - 工具定义转换（复用 OpenAI 逻辑，处理空参数情况）
- 支持 JSON schema、推理能力、网络搜索
- 工具参数不能为空（必须提供 `parameters` 字段）

这种设计使得代码职责清晰，易于维护和扩展新的提供商。`client.py` 只负责调用各 provider 的函数，不包含具体的转换逻辑。

## 项目结构
- `src/onellmclient/`：核心包
  - `client.py`：统一客户端入口
  - `types.py`：统一类型定义
  - `provider/`：各供应商的适配器
    - `openai.py`：OpenAI 转换函数（payload、messages、tools、response 转换）
    - `anthropic.py`：Anthropic 转换函数（messages、tools、response 转换）
    - `gemini.py`：Gemini 转换函数（messages、tools、response 转换）
    - `deepseek.py`：DeepSeek 转换函数（payload 构建，复用 OpenAI 工具转换）
    - `xai.py`：xAI 转换函数（payload 构建，复用 OpenAI 工具转换，处理空参数）
- `tests/`：单元测试

## 开发约定
- 仅最小化实现，所有 LLM SDK 作为硬依赖一次性安装。
- 单元测试仅覆盖改动部分。
- 禁止改动 `.env`。

## 依赖管理策略
- 使用版本范围限制：`>=x.y.z,<x.y+1.0` 格式
- 防止破坏性更新，允许安全补丁更新
- 保持构建可重现性

## 开发环境安装
```bash
# 安装所有依赖（包括 LLM SDK）
uv sync

# 安装测试依赖
uv sync --extra test

# 安装发布依赖
uv sync --extra publish

# 安装所有开发依赖（测试 + 发布）
uv sync --extra test --extra publish
```

## 打包发布到 PyPI

### 快速发布（推荐）

使用自动化脚本一键发布：

```bash
# 发布到正式 PyPI（会要求确认）
./publish.sh

# 只构建不上传（本地验证）
./publish.sh --dry-run
```

**发布流程说明**：
1. 自动清理旧文件（确保只上传最新版本）
2. 构建源码包和轮子包
3. 检查包内容
4. 确认后上传到正式 PyPI

### 手动发布流程

1. **清理并构建包**：
```bash
# 清理旧的构建文件（确保只上传最新版本）
rm -rf dist/

# 构建源码包和轮子包
uv build

# 构建的文件会生成在 dist/ 目录下
ls dist/
# onellmclient-0.1.2-py3-none-any.whl
# onellmclient-0.1.2.tar.gz
```

2. **检查包内容**：
```bash
# 检查构建的包内容
uv run twine check dist/*
```

3. **上传到 PyPI**：
```bash
# 上传到测试 PyPI（推荐先测试）
uv run twine upload --repository testpypi dist/*

# 上传到正式 PyPI
uv run twine upload dist/*
```

### 发布前检查清单

- [ ] 更新版本号（在 `pyproject.toml` 中）
- [ ] 更新 CHANGELOG.md（如果有）
- [ ] 运行所有测试确保功能正常
- [ ] 检查 README.md 内容是否最新
- [ ] 确认所有依赖版本正确
- [ ] 构建并检查包内容

### 版本管理策略

- **主版本号**：不兼容的 API 变更
- **次版本号**：向后兼容的功能新增（如新增 DeepSeek 支持）
- **修订版本号**：向后兼容的问题修复

当前版本：v0.1.3（添加 xAI 支持）

## TODO 记录
- 初始化包与发布配置
- 实现统一 Client（OpenAI/Anthropic/Gemini）
- 增加 provider 适配层与最小集成测试
- 添加 DeepSeek 适配器支持（v0.1.2）
- 添加 xAI/Grok 适配器支持（v0.1.3）
