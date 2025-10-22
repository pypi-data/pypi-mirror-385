from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentbill",
    version="1.0.0",
    author="AgentBill",
    author_email="support@agentbill.com",
    description="OpenTelemetry-based SDK for tracking AI agent usage and billing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Agent-Bill/python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.9.0"],
    },
    keywords="opentelemetry otel ai agent billing usage-tracking openai anthropic llm observability",
)
