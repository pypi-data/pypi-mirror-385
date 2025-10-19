#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""upcat包安装配置"""

from setuptools import setup, find_packages
from upcat import __version__

try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except TypeError:
    # 兼容不支持encoding参数的旧版Python
    with open("README.md", "r") as f:
        long_description = f.read().decode('utf-8')

setup(
    name="upcat",
    version=__version__,
    author="upcat Authors",
    author_email="upcat@example.com",
    description="图片文件夹可视化工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/upcat-project/upcat",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'upcat': ['*.py'],
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
    ],
    python_requires='>=3.6',
    install_requires=[],  # 本项目不需要额外依赖
    entry_points={
        'console_scripts': [
            'upcat=upcat.cli:main',
        ],
    },
)