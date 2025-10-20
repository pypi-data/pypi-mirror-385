"""
LLM 客户端：支持 OpenAI 和 Anthropic Claude API

支持真实 API 调用和缓存功能（用于大型repo的断点续传）。
使用前必须配置相应的 API Key。
"""

import os
import json
import hashlib

# Cache configuration
CACHE_FILE = "llm_cache.json"


def call_llm(prompt, model=None, temperature=0.2, max_tokens=2000, use_cache=True):
    """
    调用 LLM API - 支持真实 API 调用和缓存

    支持的模型：
    - OpenAI: gpt-4, gpt-4-turbo, gpt-3.5-turbo
    - Anthropic: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-5-sonnet-20241022

    环境变量（至少设置一个）：
    - ANTHROPIC_API_KEY: Anthropic API 密钥（推荐）
    - OPENAI_API_KEY: OpenAI API 密钥

    参数：
    - use_cache: 是否使用缓存（用于大型repo的断点续传）

    异常：
    - ValueError: 如果未设置任何 API Key
    - ImportError: 如果未安装相应的 SDK
    - Exception: API 调用失败时抛出原始异常
    """

    # Auto-detect available API key and set appropriate model if not specified
    if model is None:
        # Check which API keys are available
        has_anthropic_key = bool(os.getenv('ANTHROPIC_API_KEY'))
        has_openai_key = bool(os.getenv('OPENAI_API_KEY'))

        if has_anthropic_key:
            model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
        elif has_openai_key:
            model = "gpt-4"
        else:
            raise ValueError(
                "No API key found. Please set one of the following:\n"
                "  export ANTHROPIC_API_KEY='your-key-here'  (recommended)\n"
                "  export OPENAI_API_KEY='your-key-here'"
            )

    # Check cache if enabled
    if use_cache:
        # Create cache key (hash of prompt + model for uniqueness)
        cache_key = hashlib.md5(f"{prompt}_{model}".encode()).hexdigest()

        # Load cache from disk
        cache = {}
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except:
                pass

        # Return from cache if exists
        if cache_key in cache:
            print(f"[CACHE] Using cached LLM response")
            return cache[cache_key]

    # Call actual API with smart fallback
    if model.startswith('claude'):
        # User wants Claude, check if key available
        if not os.getenv('ANTHROPIC_API_KEY'):
            # Fallback to OpenAI if available
            if os.getenv('OPENAI_API_KEY'):
                print(f"[WARNING] ANTHROPIC_API_KEY not found, falling back to OpenAI (gpt-4)")
                model = "gpt-4"
                response = _call_openai(prompt, model, temperature, max_tokens)
            else:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found. Please set it:\n"
                    "  export ANTHROPIC_API_KEY='your-key-here'"
                )
        else:
            response = _call_anthropic(prompt, model, temperature, max_tokens)
    else:
        # User wants OpenAI (gpt-4, etc.), check if key available
        if not os.getenv('OPENAI_API_KEY'):
            # Fallback to Anthropic if available
            if os.getenv('ANTHROPIC_API_KEY'):
                print(f"[WARNING] OPENAI_API_KEY not found, falling back to Anthropic (claude-3-haiku-20240307)")
                model = "claude-3-haiku-20240307"
                response = _call_anthropic(prompt, model, temperature, max_tokens)
            else:
                raise ValueError(
                    "OPENAI_API_KEY not found. Please set it:\n"
                    "  export OPENAI_API_KEY='your-key-here'"
                )
        else:
            response = _call_openai(prompt, model, temperature, max_tokens)

    # Update cache if enabled
    if use_cache:
        cache_key = hashlib.md5(f"{prompt}_{model}".encode()).hexdigest()

        # Load cache again to avoid overwrites
        cache = {}
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except:
                pass

        # Add to cache and save
        cache[cache_key] = response
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
            print(f"[CACHE] Saved LLM response to cache")
        except Exception as e:
            print(f"[WARNING] Failed to save cache: {e}")

    return response


def _call_anthropic(prompt, model, temperature, max_tokens):
    """调用 Anthropic Claude API - 仅支持真实API调用"""
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Please set it before running:\n"
            "  export ANTHROPIC_API_KEY='your-api-key-here'\n"
            "Mock mode is not supported. Real API interaction is required."
        )

    # Clean API key - remove any smart quotes or non-ASCII characters
    api_key = api_key.strip()

    # Check for common issues with API key
    if not api_key.isascii():
        # Find problematic characters
        bad_chars = [c for c in api_key if ord(c) > 127]
        raise ValueError(
            f"ANTHROPIC_API_KEY contains non-ASCII characters: {bad_chars}\n"
            "This often happens when using smart quotes (" " ' ') instead of regular quotes.\n"
            "Please reset your API key using regular ASCII quotes:\n"
            "  export ANTHROPIC_API_KEY='your-api-key-here'  # Use regular quotes\n"
            f"Current key preview: {repr(api_key[:20])}"
        )

    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic package not installed. "
            "Please install it by running:\n"
            "  pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=api_key)

    print(f"\n{'='*60}")
    print(f"Calling Anthropic API")
    print(f"Model: {model}")
    print(f"Prompt length: {len(prompt)} chars")
    print(f"Prompt preview: {prompt[:100]}...")
    print(f"{'='*60}\n")

    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(f"\n{'='*60}")
    print(f"API Response received")
    print(f"Input tokens: {message.usage.input_tokens}")
    print(f"Output tokens: {message.usage.output_tokens}")
    print(f"Response length: {len(message.content[0].text)} chars")
    print(f"{'='*60}\n")

    return message.content[0].text


def _call_openai(prompt, model, temperature, max_tokens):
    """调用 OpenAI API - 仅支持真实API调用"""
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable not set. "
            "Please set it before running:\n"
            "  export OPENAI_API_KEY='your-api-key-here'\n"
            "Mock mode is not supported. Real API interaction is required."
        )

    # Clean API key - remove any smart quotes or non-ASCII characters
    api_key = api_key.strip()

    # Check for common issues with API key
    if not api_key.isascii():
        # Find problematic characters
        bad_chars = [c for c in api_key if ord(c) > 127]
        raise ValueError(
            f"OPENAI_API_KEY contains non-ASCII characters: {bad_chars}\n"
            "This often happens when using smart quotes (" " ' ') instead of regular quotes.\n"
            "Please reset your API key using regular ASCII quotes:\n"
            "  export OPENAI_API_KEY='your-api-key-here'  # Use regular quotes\n"
            f"Current key preview: {repr(api_key[:20])}"
        )

    try:
        import openai
    except ImportError:
        raise ImportError(
            "openai package not installed. "
            "Please install it by running:\n"
            "  pip install openai"
        )

    client = openai.OpenAI(api_key=api_key)

    print(f"\n{'='*60}")
    print(f"Calling OpenAI API")
    print(f"Model: {model}")
    print(f"Prompt length: {len(prompt)} chars")
    print(f"Prompt preview: {prompt[:100]}...")
    print(f"{'='*60}\n")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    print(f"\n{'='*60}")
    print(f"API Response received")
    print(f"Response length: {len(response.choices[0].message.content)} chars")
    print(f"{'='*60}\n")

    return response.choices[0].message.content
