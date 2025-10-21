from setuptools import setup, find_packages

# 读取 README.md 作为长描述（在 PyPI 上展示）
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sglang-musa",  # 包名（必须唯一）
    version="0.0.1",  # 版本号
    author="zhouyu",
    author_email="zhouyuzf@163.com",
    description="A simple demo Python package for PyPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/hellopkg",
    license="MIT",

    packages=find_packages(),  # 自动发现所有包
    python_requires=">=3.7",   # Python 版本要求

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
