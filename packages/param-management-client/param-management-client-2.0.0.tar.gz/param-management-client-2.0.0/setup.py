#!/usr/bin/env python3
"""
参数管理系统 Python 客户端包安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "参数管理系统 Python 客户端"

# 读取requirements文件
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['requests>=2.25.0']

setup(
    name="param-management-client",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="参数管理系统 Python 客户端，支持类似pandas DataFrame的点号访问方式，内置完整后端服务",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/param-management-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "pyomo": ["pyomo>=6.0.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
    },
    keywords="parameter management, optimization, pyomo, pandas-like, dot notation, fastapi, backend, embedded server, database",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/param-management-client/issues",
        "Source": "https://github.com/yourusername/param-management-client",
        "Documentation": "https://github.com/yourusername/param-management-client#readme",
    },
)
