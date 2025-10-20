# -*- coding: UTF-8 -*-
'''
@File    ：setup
@Date    ：2025/10/20 14:45 
@Author  ：Fbx
'''

from setuptools import setup, find_packages

setup(
    name="mcp-tip",
    version="0.1.1",
    description="ThreatBook IP 查询 MCP 工具",
    author="FBX",
    author_email="your_email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31",
        "fastmcp>=0.1.0"
    ],
    python_requires=">=3.10"
)
