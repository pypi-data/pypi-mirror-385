#!/usr/bin/env python3

'''
 _   _  _______   _______   _____  
| \ | ||  ___\ \ / /_   _| |  ___| 
|  \| || |__  \ V /  | |   | |__   
| . ` ||  __| /   \  | |   |  __|  
| |\  || |___/ /^\ \ | |   | |___  
\_| \_/\____/\/   \/ \_/   \____/  

Author: ziyu (Chen Zhaoyu)
Date: 2025-09-26 18:06:36
LastEditors: ziyu (Chen Zhaoyu)
LastEditTime: 2025-09-27 12:59:37
Description: 

ros2 ament_cmake_auto package create script
- create a package with ament_cmake_auto build tool
- add necessary dependencies
- create a cpp and hpp file with the name of the package_name_node
- add a class in the cpp and hpp file with the default components settings

Copyright (c) 2025 by XAUT NEXT-E/ziyu, All Rights Reserved. 
'''

import os
import sys
import argparse

# AI生成 可能有误
def is_snake_case(s, allow_digit_start=False, allow_underscore_start=False):
    """
    增强版下划线命名法检查
    
    Args:
        s (str): 要检查的字符串
        allow_digit_start (bool): 是否允许以数字开头
        allow_underscore_start (bool): 是否允许以下划线开头
        
    Returns:
        bool: 是否符合规则
    """
    if not s:
        return False
    
    # 基础字符集检查
    if not all(c.islower() or c.isdigit() or c == '_' for c in s):
        return False
    
    # 开头检查
    if not allow_digit_start and s[0].isdigit():
        return False
    if not allow_underscore_start and s[0] == '_':
        return False
    
    # 结尾检查
    if s[-1] == '_':
        return False
    
    # 连续下划线检查
    if '__' in s:
        return False
    
    return True

# AI生成 可能有误
def snake_to_pascal(snake_str):
    """
    将下划线命名法转换为大驼峰命名法
    
    Args:
        snake_str (str): 下划线命名法的字符串，如 "a_num_of_dog"
        
    Returns:
        str: 大驼峰命名法的字符串，如 "ANumOfDog"
    """
    if not snake_str:
        return ""
    
    # 按下划线分割字符串
    words = snake_str.split('_')
    
    # 过滤掉空字符串（处理连续下划线的情况）
    words = [word for word in words if word]
    
    # 将每个单词的首字母大写，其他字母小写，然后拼接
    pascal_case = ''.join(word.capitalize() for word in words)
    
    return pascal_case

def rapc(pkg_name, dep, dest_path, namespace, node_name, class_name, file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "rapc_templates", "CMakeLists_template.txt"), 'r') as f:
        cmake_t = f.read()
    with open(os.path.join(script_dir, "rapc_templates", "src_template.cpp"), 'r') as f:
        src_t = f.read()
    with open(os.path.join(script_dir, "rapc_templates", "header_template.hpp"), 'r') as f:
        header_t = f.read()

    if not os.path.isdir(dest_path):
        print(f"Error: Destination path '{dest_path}' does not exist or is not a directory.")
        sys.exit(1)

    # 准备各种奇奇怪怪的名字
    if not is_snake_case(pkg_name):
        print("Package name must be in snake_case!")
        sys.exit(1)

    namespace_str = ""
    if not (namespace is None or len(namespace) == 0):
        namespace_str = f"{namespace}::"

    node_name_str = "${PROJECT_NAME}_node"
    if not (node_name is None or len(node_name) == 0):
        node_name_str = node_name

    namespace_name = namespace_str.replace("::", "")
    namespace_start = "namespace " + namespace_name + "\n{\n" if len(namespace_name) > 0 else ""
    namespace_end = f"}} // namespace {namespace_name}\n" if len(namespace_name) > 0 else ""

    class_name_str = snake_to_pascal(pkg_name) + "Node"
    if not (class_name is None or len(class_name) == 0):
        class_name_str = class_name

    file_name_str = pkg_name + "_node"
    if not (file_name is None or len(file_name) == 0):
        file_name_str = file_name

    hpp_file_name = file_name_str + ".hpp"
    cpp_file_name = file_name_str + ".cpp"

    hpp_file_path = os.path.join(dest_path, pkg_name, "include", pkg_name, hpp_file_name)
    cpp_file_path = os.path.join(dest_path, pkg_name, "src", cpp_file_name)

    pkg_create_str = f"ros2 pkg create --build-type ament_cmake --destination-directory {dest_path}"

    pkg_create_str += f" {pkg_name}"

    if not (dep is None or len(dep) == 0):
        dep_str = " --dependencies " + " ".join(dep)
        pkg_create_str += dep_str


    print(f"Run commend to create package:\n{pkg_create_str}")

    if (os.system(pkg_create_str)):
        print("Package creation failed!")
        sys.exit(1)

    print(f"Package {pkg_name} created successfully!")

    # 开始替换一些东西

    # 替换CMake
    print("Modifying CMakeLists.txt...")
    cmake_t = cmake_t.replace("{{pkg_name}}", pkg_name)
    cmake_t = cmake_t.replace("{{namespace}}", namespace_str)
    cmake_t = cmake_t.replace("{{node_name}}", node_name_str)
    cmake_t = cmake_t.replace("{{class_name}}", class_name_str)
    cmake_t = cmake_t.replace("{{file_name}}", file_name_str)
    with open(os.path.join(dest_path, pkg_name, "CMakeLists.txt"), 'w') as f:
        f.write(cmake_t)

    # 创建头文件
    print(f"Creating header file {hpp_file_path}...")
    header_t = header_t.replace("{{namespace_name}}", namespace_name)
    header_t = header_t.replace("{{namespace_start}}", namespace_start)
    header_t = header_t.replace("{{namespace_end}}", namespace_end)
    header_t = header_t.replace("{{class_name}}", class_name_str)
    define_name = f"{pkg_name.upper()}__{file_name_str.upper()}_HPP"
    header_t = header_t.replace("{{define_name}}", define_name)
    with open(hpp_file_path, 'w') as f:
        f.write(header_t)

    # 创建源文件
    print(f"Creating source file {cpp_file_path}...")
    src_t = src_t.replace("{{namespace_name}}", namespace_name)
    src_t = src_t.replace("{{namespace_start}}", namespace_start)
    src_t = src_t.replace("{{namespace_end}}", namespace_end)
    src_t = src_t.replace("{{class_name}}", class_name_str)
    src_t = src_t.replace("{{file_name}}", file_name_str)
    src_t = src_t.replace("{{pkg_name}}", pkg_name)
    src_t = src_t.replace("{{header_file_name}}", hpp_file_name)
    src_t = src_t.replace("{{node_name}}", node_name_str)
    src_t = src_t.replace("{{namespace}}", namespace_str)
    with open(cpp_file_path, 'w') as f:
        f.write(src_t)

    print("All done!")
    print(f"To build the package, run:\ncolcon build --packages-select {pkg_name}")
    print(f"To source the workspace, run:\nsource install/setup.bash")
    print(f"To run the node, run:\nros2 run {pkg_name} {node_name_str}")

def main(args):
    if args.package_name:
        rapc(
            args.package_name, 
            args.dependencies, 
            args.dest_path,
            args.namespace if args.namespace != "None" else None, 
            args.node_name if args.node_name else args.package_name + "_node", 
            args.class_name if args.class_name else ''.join([word.capitalize() for word in args.package_name.split('_')]) + "Node", 
            args.file_name if args.file_name else args.package_name + "_node"
        )
    else:
        print("Package name is required!")
        sys.exit(1)

def args_declare(root_parser):
    parser_rapc = root_parser.add_parser('rapc', help='rapc help', description="Create a ROS2 package with ament_cmake_auto build tool")
    parser_rapc.add_argument("package_name", type=str, help="包名")
    parser_rapc.add_argument("-p", "--dest_path", type=str, default=os.getcwd(), help="包创建路径，默认为当前路径")
    parser_rapc.add_argument("-ns", "--namespace", type=str, default="None", help="包命名空间，默认为None")
    parser_rapc.add_argument("-d", "--dependencies", type=str, nargs='*', default=["rclcpp", "rclcpp_components"], help="依赖包，空格分隔")
    parser_rapc.add_argument("-nn", "--node_name", type=str, default=None, help="节点名，默认为包名+node，如demo_pkg_node")
    parser_rapc.add_argument("-cn", "--class_name", type=str, default=None, help="类名，默认为包名+Node，如DemoPkgNode")
    parser_rapc.add_argument("-fn", "--file_name", type=str, default=None, help="文件名，默认为包名+_node，如demo_pkg_node.cpp/hpp")
    parser_rapc.set_defaults(func=main)