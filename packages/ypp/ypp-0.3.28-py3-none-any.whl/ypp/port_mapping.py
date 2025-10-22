#!/usr/bin/env python3
"""
通用端口映射工具
支持任意IP到IP的端口转发
"""

import os
import sys
import subprocess
import platform
from typing import Optional


def is_windows_system() -> bool:
    """检查是否为 Windows 系统"""
    return platform.system().lower() == "windows"


def is_admin() -> bool:
    """检查是否具有管理员权限"""
    try:
        if is_windows_system():
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False


def run_netsh_as_admin(command: list) -> bool:
    """以管理员权限执行 netsh 命令"""
    try:
        if not is_windows_system():
            return False
            
        import subprocess
        
        # 使用 PowerShell 以管理员权限执行 netsh 命令
        # 移除第一个 "netsh" 参数，因为 -FilePath 已经指定了程序
        netsh_args = command[1:] if command[0] == "netsh" else command
        # 构建参数列表字符串
        args_str = ",".join([f'"{arg}"' for arg in netsh_args])
        ps_cmd = f'Start-Process -FilePath "netsh" -ArgumentList {args_str} -Verb RunAs -Wait'
        
        result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            return True
        else:
            print(f"netsh 命令执行失败: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"以管理员权限执行 netsh 命令失败: {e}", file=sys.stderr)
        return False


def validate_ip_address(ip: str) -> bool:
    """验证IP地址格式"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True
    except:
        return False


def validate_port(port: int) -> bool:
    """验证端口号"""
    return 1 <= port <= 65535


def add_port_mapping(source_ip: str, source_port: int, target_ip: str, target_port: int) -> bool:
    """添加端口映射规则"""
    try:
        # 验证参数
        if not validate_ip_address(source_ip):
            print(f"错误: 源IP地址格式无效: {source_ip}", file=sys.stderr)
            return False
        
        if not validate_ip_address(target_ip):
            print(f"错误: 目标IP地址格式无效: {target_ip}", file=sys.stderr)
            return False
        
        if not validate_port(source_port):
            print(f"错误: 源端口号无效: {source_port}", file=sys.stderr)
            return False
        
        if not validate_port(target_port):
            print(f"错误: 目标端口号无效: {target_port}", file=sys.stderr)
            return False
        
        # 使用 netsh 添加端口映射规则
        cmd = [
            "netsh", "interface", "portproxy", "add", "v4tov4",
            f"listenport={source_port}",
            f"listenaddress={source_ip}",
            f"connectport={target_port}",
            f"connectaddress={target_ip}"
        ]
        
        print(f"添加端口映射: {source_ip}:{source_port} -> {target_ip}:{target_port}")
        
        # 尝试直接执行，如果失败则使用管理员权限
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
            if result.returncode == 0:
                print(f"✓ 端口映射规则添加成功")
                return True
        except subprocess.CalledProcessError:
            # 直接执行失败，尝试使用管理员权限
            print("需要管理员权限，正在请求...")
            if run_netsh_as_admin(cmd):
                print(f"✓ 端口映射规则添加成功")
                return True
            else:
                print(f"✗ 添加端口映射失败", file=sys.stderr)
                return False
        
        return False
    except Exception as e:
        print(f"✗ 添加端口映射时发生错误: {e}", file=sys.stderr)
        return False


def remove_port_mapping(source_ip: str, source_port: int) -> bool:
    """移除端口映射规则"""
    try:
        # 验证参数
        if not validate_ip_address(source_ip):
            print(f"错误: 源IP地址格式无效: {source_ip}", file=sys.stderr)
            return False
        
        if not validate_port(source_port):
            print(f"错误: 源端口号无效: {source_port}", file=sys.stderr)
            return False
        
        cmd = [
            "netsh", "interface", "portproxy", "delete", "v4tov4",
            f"listenport={source_port}",
            f"listenaddress={source_ip}"
        ]
        
        print(f"移除端口映射: {source_ip}:{source_port}")
        
        # 尝试直接执行，如果失败则使用管理员权限
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
            if result.returncode == 0:
                print(f"✓ 端口映射规则移除成功")
                return True
        except subprocess.CalledProcessError:
            # 直接执行失败，尝试使用管理员权限
            print("需要管理员权限，正在请求...")
            if run_netsh_as_admin(cmd):
                print(f"✓ 端口映射规则移除成功")
                return True
            else:
                print(f"✗ 移除端口映射失败", file=sys.stderr)
                return False
        
        return False
    except Exception as e:
        print(f"✗ 移除端口映射时发生错误: {e}", file=sys.stderr)
        return False


def list_port_mappings() -> bool:
    """列出所有端口映射规则"""
    try:
        cmd = ["netsh", "interface", "portproxy", "show", "v4tov4"]
        
        print("当前端口映射规则:")
        print("=" * 80)
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        
        if result.stdout.strip():
            print(result.stdout)
        else:
            print("暂无端口映射规则")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 获取端口映射规则失败: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ 获取端口映射规则时发生错误: {e}", file=sys.stderr)
        return False


def command_port_mapping(source_ip: Optional[str] = None, source_port: Optional[int] = None, 
                        target_ip: Optional[str] = None, target_port: Optional[int] = None,
                        action: str = "add") -> None:
    """
    执行端口映射命令
    
    Args:
        source_ip: 源IP地址
        source_port: 源端口
        target_ip: 目标IP地址
        target_port: 目标端口
        action: 操作类型 (add/remove/list)
    """
    # 检查系统
    if not is_windows_system():
        print("错误: 此命令仅在 Windows 系统上支持", file=sys.stderr)
        sys.exit(1)
    
    try:
        if action == "list":
            # 列出所有端口映射规则
            if not list_port_mappings():
                sys.exit(1)
                
        elif action == "add":
            # 添加端口映射规则
            if source_ip is None or source_port is None or target_ip is None or target_port is None:
                print("错误: 添加端口映射需要指定源IP、源端口、目标IP和目标端口", file=sys.stderr)
                print("用法: ypp port <源IP> <源端口> <目标IP> <目标端口>", file=sys.stderr)
                sys.exit(1)
            
            if not add_port_mapping(source_ip, source_port, target_ip, target_port):
                sys.exit(1)
                
        elif action == "remove":
            # 移除端口映射规则
            if source_ip is None or source_port is None:
                print("错误: 移除端口映射需要指定源IP和源端口", file=sys.stderr)
                print("用法: ypp port remove <源IP> <源端口>", file=sys.stderr)
                sys.exit(1)
            
            if not remove_port_mapping(source_ip, source_port):
                sys.exit(1)
        
    except Exception as e:
        print(f"执行端口映射命令时发生错误: {e}", file=sys.stderr)
        sys.exit(1)
