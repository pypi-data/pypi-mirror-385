from setuptools import setup, find_packages

NAME = "blackman-client"
VERSION = "0.0.5"
REQUIRES = [
    "urllib3 >= 1.25.3",
    "python-dateutil",
    "pydantic >= 1.10.5, < 2",
    "aenum"
]

setup(
    name=NAME,
    version=VERSION,
    description="Official Python SDK for Blackman AI - Optimize your AI API costs",
    author="Blackman AI",
    author_email="support@useblackman.ai",
    url="https://github.com/blackman-ai/python-sdk",
    keywords=["blackman", "ai", "llm", "openai", "anthropic", "cost-optimization", "api-client"],
    python_requires=">=3.7",
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description="""\
# Blackman AI Python SDK

Official Python client for [Blackman AI](https://www.useblackman.ai) - The AI API proxy that optimizes token usage to reduce costs.

## Features

- 🚀 Drop-in replacement for OpenAI, Anthropic, and other LLM APIs
- 💰 Automatic token optimization (save 20-40% on costs)
- 📊 Built-in analytics and cost tracking
- 🔒 Enterprise-grade security with SSO support
- ⚡ Low latency overhead (<50ms)
- 🎯 Semantic caching for repeated queries

## Installation

\`\`\`bash
pip install blackman-client
\`\`\`

## Quick Start

\`\`\`python
import blackman_client
from blackman_client import CompletionRequest

configuration = blackman_client.Configuration(
    host="https://app.useblackman.ai",
    access_token="sk_your_blackman_api_key"
)

with blackman_client.ApiClient(configuration) as api_client:
    api = blackman_client.CompletionsApi(api_client)
    response = api.completions(
        CompletionRequest(
            provider="OpenAI",
            model="gpt-4o",
            messages=[{"role": "user", "content": "Explain quantum computing"}]
        )
    )
    print(response.choices[0].message.content)
    print(f"Tokens saved: {response.usage.prompt_tokens}")
\`\`\`

## Documentation

- [Full API Reference](https://app.useblackman.ai/docs)
- [Getting Started Guide](https://app.useblackman.ai/docs/getting-started)
- [Python Examples](https://github.com/blackman-ai/python-sdk/tree/main/examples)
- [Django Integration](https://app.useblackman.ai/docs/frameworks/django)
- [FastAPI Integration](https://app.useblackman.ai/docs/frameworks/fastapi)

## Support

- 📧 Email: support@blackman.ai
- 💬 Discord: [Join our community](https://discord.gg/blackman-ai)
- 🐛 Issues: [GitHub Issues](https://github.com/blackman-ai/python-sdk/issues)
""",
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
