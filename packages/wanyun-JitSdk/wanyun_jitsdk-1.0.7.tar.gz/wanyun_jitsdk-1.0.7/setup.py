# -*-coding:utf-8-*-
"""
Created on 2024/11/13

@author: 臧韬

@desc: 默认描述
"""

from setuptools import setup, find_packages

from pathlib import Path

__lib_name__ = 'wanyun_JitSdk'

this_directory = Path(__file__).parent
read_me_path = this_directory / __lib_name__ / "README.md"

VERSION = '1.0.7'
DESCRIPTION = 'Official Jit API Authorization SDK'
LONG_DESCRIPTION = read_me_path.read_text()

# 配置
setup(
    # 名称必须匹配文件名 'verysimplemodule'
    name=__lib_name__,
    version=VERSION,
    author="zangtao",
    author_email="support@jit.pro",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],

    keywords=['python', 'jit', "sdk", "apiAuth"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ]
)
