#!/usr/bin/env python3

'''
 _   _  _______   _______   _____  
| \ | ||  ___\ \ / /_   _| |  ___| 
|  \| || |__  \ V /  | |   | |__   
| . ` ||  __| /   \  | |   |  __|  
| |\  || |___/ /^\ \ | |   | |___  
\_| \_/\____/\/   \/ \_/   \____/  

Author: ziyu (Chen Zhaoyu)
Date: 2025-09-27 00:37:45
LastEditors: ziyu (Chen Zhaoyu)
LastEditTime: 2025-10-21 22:35:31
Description: 

NEXT-E Ros2 tools

Copyright (c) 2025 by XAUT NEXT-E/ziyu, All Rights Reserved. 
'''

import argparse
import os

from .rapc import rapc

def main():
    parser = argparse.ArgumentParser(description='NEXT-E Ros2 tools')
    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommand help')

    # RAPC 子命令
    
    rapc.args_declare(subparsers) # 解析rapc子命令参数
    

    # # 子命令2
    # parser_tool2 = subparsers.add_parser('tool2', help='Tool2 help')
    # parser_tool2.set_defaults(func=tool2.main)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()