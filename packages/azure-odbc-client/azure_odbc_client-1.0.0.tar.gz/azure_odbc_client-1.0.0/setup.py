"""
简化的setup.py文件
"""

from setuptools import setup, find_packages

# 读取README文件
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

setup(
    name="azure-odbc-client",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="一个简单易用的Azure SQL Server ODBC客户端包",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/azure-odbc-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyodbc>=4.0.30",
    ],
    keywords="azure sql server odbc database client",
)
