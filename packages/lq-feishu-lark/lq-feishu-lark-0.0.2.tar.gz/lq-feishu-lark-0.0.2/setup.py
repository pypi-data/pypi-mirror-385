# setup.py

from setuptools import setup, find_packages

setup(
    name = 'lq-feishu-lark',
    version = '0.0.2',
    packages = find_packages(),
    description = '飞书扩展库',
    author = 'lant',
    author_email = 'lant@163.com',
    url = 'https://gitee.com/my/my',  # 替换为你的GitHub仓库URL
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires = '>=3.6',
    install_requires = [],
)
