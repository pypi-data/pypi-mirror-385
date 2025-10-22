# setup.py
'''
 _   _  _______   _______   _____  
| \ | ||  ___\ \ / /_   _| |  ___| 
|  \| || |__  \ V /  | |   | |__   
| . ` ||  __| /   \  | |   |  __|  
| |\  || |___/ /^\ \ | |   | |___  
\_| \_/\____/\/   \/ \_/   \____/  

Author: ziyu (Chen Zhaoyu)
Date: 2025-09-27 00:32:59
LastEditors: ziyu (Chen Zhaoyu)
LastEditTime: 2025-09-27 13:03:14
Description: 
Copyright (c) 2025 by XAUT NEXT-E/ziyu, All Rights Reserved. 
'''

from setuptools import setup, find_packages

setup(
    name='nrt',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            # 格式：'命令名 = 包名.模块名:函数名'
            'nrt = nrt.nrt:main',
        ],
    },
)