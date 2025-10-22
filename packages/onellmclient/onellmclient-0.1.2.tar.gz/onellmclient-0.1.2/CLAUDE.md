# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Unified LLM Client - A Python library that provides a unified interface for OpenAI, Anthropic, and Gemini APIs. This allows applications to transparently switch between LLM providers without changing code.

**Key Design Principle**: Zero mandatory runtime dependencies. Each provider's SDK is optional and installed via extras.

## Common Commands

### Environment Setup
```bash
# Create virtual environment and install package
uv venv
uv pip install -e .

# Install specific provider SDKs
uv pip install -e .[openai]
uv pip install -e .[anthropic]
uv pip install -e .[gemini]
uv pip install -e .[all]

# Install test dependencies
uv pip install -e .[test]
```

### Testing
```bash
# Run all tests
pytest

# Run tests for a specific provider
pytest tests/test_client.py::test_completion_say_cow -k openai
pytest tests/test_client.py::test_completion_say_cow -k anthropic
pytest tests/test_client.py::test_completion_say_cow -k gemini

# Run a specific test function
pytest tests/test_client.py::test_completion_schema -v
```

### Building and Publishing
```bash
# Build distribution packages
uv build

# Upload to TestPyPI
uv tool install twine
uv run twine upload --repository testpypi dist/*

# Upload to PyPI
uv run twine upload dist/*
```

## Architecture

### Core Components

**`client.py`**: Main `Client` class that provides two methods:
- `completion()`: Single request/response interaction with provider
- `agent()`: Automatic tool call execution loop (up to 10 iterations)

Both methods accept unified parameters and return `UnifiedMessage` objects.

**`types.py`**: Pydantic models defining the unified message format:
- `UnifiedMessage`: Base message container with role and content
- `UnifiedTextMessageContent`: Text content blocks
- `UnifiedToolCallMessageContent`: Tool/function call requests
- `UnifiedToolResultMessageContent`: Tool execution results
- All types extend `UnifiedBaseModel` which adds `.get()` method for dict-like access

**`utils.py`**: Conversion utilities between unified format and provider-specific formats:
- `{provider}_messages()`: Convert `UnifiedMessage` → provider format
- `{provider}_response_convert()`: Convert provider response → `UnifiedMessage`
- `{provider}_tools()`: Convert unified tool definitions → provider format
- `openai_json_schema()`: Recursively adds `additionalProperties: false` for OpenAI strict mode

### Key Architectural Patterns

1. **Message Format Unification**: All providers use different message formats. The library normalizes them:
   - OpenAI uses `response.output` with separate `message` and `function_call` types
   - Anthropic uses `message.content` with `text` and `tool_use` blocks
   - Gemini uses `content.parts` with `text` and `function_call` attributes

2. **Parameter Translation**: Provider-specific parameters are translated:
   - `temperature`: Anthropic uses 0-1 range (divided by 2), others use 0-2
   - `instructions`: Maps to `instructions` (OpenAI), `system` (Anthropic), `system_instruction` (Gemini)
   - `schema`: OpenAI uses native support, Anthropic uses system prompt injection, Gemini uses `response_schema`
   - `tool_choice`: Unified `auto/none/required` maps to provider-specific values
   - `reasoning_effort`: Maps to `reasoning.effort` (OpenAI), `thinking.budget_tokens` (Anthropic), `thinking_budget` (Gemini)

3. **Tool Call Loop**: The `agent()` method automatically handles multi-turn tool execution by:
   - Calling `completion()` with tools
   - If response contains tool calls, execute handlers and append results to messages
   - Repeat until no tool calls in response or max iterations (10) reached

4. **Role Mapping**: Gemini uses `model` instead of `assistant`, converted in `gemini_messages()` and `gemini_response_convert()`

## Development Constraints

- **Minimize implementation**: Only add features when needed
- **Preserve `.env`**: Never modify the environment file
- **Unit test coverage**: Only test modified code sections
- **Dependency versioning**: Use format `>=x.y.z,<x.y+1.0` to prevent breaking updates while allowing patches
- **Provider isolation**: Each provider implementation in `src/onellmclient/provider/{provider}/` is independent

## Testing Requirements

Tests require API keys in `.env`:
```
OPENAI_API_KEY=...
OPENAI_API_BASE=...
ANTHROPIC_API_KEY=...
ANTHROPIC_API_BASE=...
GEMINI_API_KEY=...
GEMINI_API_BASE=...
```

All test functions are parameterized to run against all three providers with their respective models.