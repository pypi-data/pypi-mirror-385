from onellmclient import Client
from dotenv import load_dotenv
import os
import pytest
import json

load_dotenv()

client = Client(
    openai={"key": os.getenv("OPENAI_API_KEY"), "base": os.getenv("OPENAI_API_BASE")},
    anthropic={
        "key": os.getenv("ANTHROPIC_API_KEY"),
        "base": os.getenv("ANTHROPIC_API_BASE"),
    },
    gemini={"key": os.getenv("GEMINI_API_KEY"), "base": os.getenv("GEMINI_API_BASE")},
    deepseek={
        "key": os.getenv("DEEPSEEK_API_KEY"),
        "base": os.getenv("DEEPSEEK_API_BASE"),
    },
    xai={"key": os.getenv("XAI_API_KEY"), "base": os.getenv("XAI_API_BASE")},
)


@pytest.mark.parametrize(
    "provider,model",
    [
        ("openai", "gpt-4o-mini"),
        ("anthropic", "claude-3-5-sonnet-20240620"),
        ("gemini", "gemini-2.0-flash-001"),
        ("deepseek", "deepseek-v3.2-exp"),
        ("xai", "grok-4-fast-non-reasoning"),
    ],
)
def test_completion_say_cow(provider, model):
    resp = client.completion(
        provider=provider,
        model=model,
        messages=[{"role": "user", "content": "say 'i am a cow' in your response"}],
    )
    print(resp)
    assert resp is not None
    assert isinstance(resp.content, list)
    assert "i am a cow" in resp.content[0].content.lower()


@pytest.mark.parametrize(
    "provider,model",
    [
        ("openai", "gpt-4o-mini"),
        ("anthropic", "claude-3-5-sonnet-20240620"),
        ("gemini", "gemini-2.0-flash-001"),
        ("deepseek", "deepseek-v3.2-exp"),
        ("xai", "grok-4-fast-non-reasoning"),
    ],
)
def test_completion_meow(provider, model):
    resp = client.completion(
        provider=provider,
        model=model,
        instructions="you are a cat, you can only say 'meow'",
        messages=[{"role": "user", "content": "hello hello you cute little kitty"}],
    )
    print(resp)
    assert resp is not None
    assert isinstance(resp.content, list)
    assert "meow" in resp.content[0].content.lower()


@pytest.mark.parametrize(
    "provider,model",
    [
        ("openai", "gpt-5-mini"),
        ("anthropic", "claude-3-7-sonnet-latest"),
        ("gemini", "gemini-2.5-flash"),
        ("deepseek", "deepseek-v3.2-exp"),
        ("xai", "grok-4-fast-non-reasoning"),
    ],
)
def test_completion_schema(provider, model):
    resp = client.completion(
        provider=provider,
        model=model,
        instructions="You are Gavin, a nice guy",
        messages=[{"role": "user", "content": "hello, what your name"}],
        schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        },
        temperature=0,
    )
    print(resp)
    assert resp is not None
    assert isinstance(resp.content, list)
    content = json.loads(resp.content[0].content)
    assert "gavin" in content["name"].lower()


@pytest.mark.parametrize(
    "provider,model",
    [
        ("openai", "gpt-5-mini"),
        (
            "anthropic",
            "claude-3-7-sonnet-20250219",
        ),  # claude-sonnet-4 has issues with tool_choice='any' via proxy
        ("gemini", "gemini-2.5-flash"),
        ("deepseek", "deepseek-v3.2-exp"),
        ("xai", "grok-4-fast-non-reasoning"),
    ],
)
def test_completion_tools(provider, model):
    resp = client.completion(
        provider=provider,
        model=model,
        instructions="You are Gavin, a nice guy. Use available tools to help you answer the question",
        messages=[{"role": "user", "content": "hello, what time is it now"}],
        tools=[
            {
                "name": "current_time",
                "description": "call this function to get the current time",
            }
        ],
        tool_choice="required",
    )
    print(resp)
    assert resp is not None
    assert isinstance(resp.content, list)
    has_tool_call = False
    for content in resp.content:
        if content.type == "tool_call":
            has_tool_call = True
            assert content.content.name == "current_time"
    assert has_tool_call


@pytest.mark.parametrize(
    "provider,model",
    [
        ("openai", "gpt-5-mini"),
        # ("anthropic", "claude-sonnet-4-20250514"),
        ("gemini", "gemini-2.5-flash"),
        ("xai", "grok-4-fast-non-reasoning"),
    ],
)
def test_completion_web_search(provider, model):
    resp = client.completion(
        provider=provider,
        model=model,
        instructions="Help user retrieve information from the web",
        messages=[
            {
                "role": "user",
                "content": "what is the result of the latest F1 grand prix?",
            }
        ],
        web_search=True,
    )
    print(resp)
    assert resp is not None
    assert isinstance(resp.content, list)
    assert isinstance(resp.content[0].content, str)


@pytest.mark.parametrize(
    "provider,model",
    [
        ("openai", "gpt-5-mini"),
        ("anthropic", "claude-sonnet-4-20250514"),
        ("gemini", "gemini-2.5-flash"),
        ("xai", "grok-4-fast-non-reasoning"),
    ],
)
def test_completion_reasoning_effort(provider, model):
    resp = client.completion(
        provider=provider,
        model=model,
        instructions="You are a smart guy",
        messages=[
            {
                "role": "user",
                "content": "tell me, how many r's in the word strawberry, think as hard as you can",
            }
        ],
        reasoning_effort="high",
    )
    print(resp)
    assert resp is not None
    assert isinstance(resp.content, list)
    assert (
        "3" in resp.content[0].content.lower()
        or "three" in resp.content[0].content.lower()
    )


def current_time():
    return "北京时间2025-09-30 10:00:00"


@pytest.mark.parametrize(
    "provider,model",
    [
        # ("openai", "gpt-5-mini"),
        # ("anthropic", "claude-3-7-sonnet-20250219"),
        # ("gemini", "gemini-2.5-flash"),
        ("deepseek", "deepseek-v3.2-exp"),
        # ("xai", "grok-4-fast-non-reasoning"),
    ],
)
def test_agent(provider, model):
    resp = client.agent(
        provider=provider,
        model=model,
        instructions="You are Gavin, a nice guy. Use available tools to help you answer the question. Use `current_time` function to get the current time",
        messages=[{"role": "user", "content": "hello, what time is it now"}],
        tools=[
            {
                "name": "current_time",
                "description": "call this function to get the current time",
                "handler": current_time,
            }
        ],
        temperature=0,
    )
    print(resp)
    assert resp is not None
    assert isinstance(resp.content, list)
    assert "30" in resp.content[0].content
