#!/usr/bin/env python3
"""
CDMN Decision MCP Server - PyPI 배포용 setup.py
"""

from setuptools import setup, find_packages
import os

# README 파일 읽기
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# requirements.txt 읽기
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cdmn-mcp-server",
    version="1.1.0",
    author="rickjang",
    author_email="rickjang@example.com",
    description="FastMCP 기반 DMN 서버로 자연어 입력을 받아 DMN 규칙을 실행하고 결과를 반환하는 MCP 서버",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/rickjang/cdmn-mcp-server",
    project_urls={
        "Bug Tracker": "https://github.com/rickjang/cdmn-mcp-server/issues",
        "Documentation": "https://github.com/rickjang/cdmn-mcp-server#readme",
        "Source Code": "https://github.com/rickjang/cdmn-mcp-server",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cdmn-mcp-server=cdmn_mcp_server.server_fully_generic:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cdmn_mcp_server": [
            "rules/*.dmn.xml",
            "prompts/*.md",
            "prompts/*.py",
        ],
    },
    keywords="mcp, dmn, decision, rules, engine, fastmcp, llm, natural language",
)
