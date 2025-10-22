#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询指定端口被哪些进程占用（跨平台）。

优先使用 psutil（若安装），否则基于系统自带工具：
- Windows: netstat + tasklist
- Linux: ss（优先）/netstat
- macOS: lsof
"""

from __future__ import annotations

import platform
import re
import shutil
import subprocess
from typing import List, Tuple, Optional


def _run_command(command_args: List[str]) -> Tuple[int, str]:
    """运行命令并返回 (returncode, stdout)"""
    process = subprocess.Popen(
        command_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    assert process.stdout is not None
    output_lines = []
    for line in process.stdout:
        output_lines.append(line)
    process.wait()
    return process.returncode, ''.join(output_lines)


def _try_psutil(port: int) -> List[Tuple[int, str]]:
    try:
        import psutil  # type: ignore
    except Exception:
        return []

    pid_set = set()
    results: List[Tuple[int, str]] = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            laddr = conn.laddr if conn.laddr else None
            if not laddr:
                continue
            if getattr(laddr, 'port', None) != port:
                continue
            pid = conn.pid
            if pid is None or pid in pid_set:
                continue
            try:
                proc = psutil.Process(pid)
                name = proc.name()
            except Exception:
                name = "<unknown>"
            pid_set.add(pid)
            results.append((pid, name))
    except Exception:
        return []
    return results


def _windows_lookup(port: int) -> List[Tuple[int, str]]:
    rc, out = _run_command(["netstat", "-ano"])
    if rc != 0:
        return []
    pids = set()
    results: List[Tuple[int, str]] = []
    pattern = re.compile(r"^\s*(TCP|UDP)\s+[^\s]*:%d\b.*\s(\d+)\s*$" % port, re.IGNORECASE)
    for line in out.splitlines():
        m = pattern.match(line)
        if not m:
            continue
        pid = int(m.group(2))
        if pid in pids:
            continue
        pids.add(pid)
    for pid in sorted(pids):
        # 获取进程名
        rc2, out2 = _run_command(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"])  # CSV 无表头
        name = "<unknown>"
        if rc2 == 0:
            # CSV 格式："Image Name","PID","Session Name","Session#","Mem Usage"
            # 取第一列作为进程名，去掉引号
            first_line = out2.strip().splitlines()[0] if out2.strip() else ""
            if first_line and first_line[0] == '"':
                try:
                    name = first_line.split('",')[0].strip('"')
                except Exception:
                    pass
        results.append((pid, name))
    return results


def _linux_lookup(port: int) -> List[Tuple[int, str]]:
    # 优先使用 ss
    if shutil.which("ss") is not None:
        rc, out_tcp = _run_command(["ss", "-ltnp"])  # TCP
        rc2, out_udp = _run_command(["ss", "-lunp"])  # UDP
        combined = (out_tcp if rc == 0 else "") + "\n" + (out_udp if rc2 == 0 else "")
        # 示例: users:(("nginx",pid=1234,fd=6))
        results: List[Tuple[int, str]] = []
        seen = set()
        for line in combined.splitlines():
            if f":{port} " not in line and not line.strip().endswith(f":{port}"):
                continue
            for name, pid in re.findall(r"users:\(\(\"([^\"]+)\",pid=(\d+)", line):
                pid_i = int(pid)
                if pid_i in seen:
                    continue
                seen.add(pid_i)
                results.append((pid_i, name))
        if results:
            return results
    # 回退使用 netstat
    if shutil.which("netstat") is not None:
        rc, out = _run_command(["netstat", "-tunlp"])  # 需要 root 才能包含程序名
        if rc == 0:
            results: List[Tuple[int, str]] = []
            seen = set()
            # 示例末列: 1234/nginx
            for line in out.splitlines():
                if f":{port} " not in line and not line.strip().endswith(f":{port}"):
                    continue
                m = re.search(r"\s(\d+)/(\S+)\s*$", line)
                if not m:
                    continue
                pid_i = int(m.group(1))
                name = m.group(2)
                if pid_i in seen:
                    continue
                seen.add(pid_i)
                results.append((pid_i, name))
            if results:
                return results
    return []


def _mac_lookup(port: int) -> List[Tuple[int, str]]:
    # macOS 上 lsof 最可靠
    if shutil.which("lsof") is None:
        return []
    rc, out = _run_command(["lsof", "-nP", f"-i:{port}"])
    if rc != 0:
        return []
    # 列格式: COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
    results: List[Tuple[int, str]] = []
    seen = set()
    lines = [l for l in out.splitlines() if l.strip()]
    if not lines:
        return []
    for line in lines[1:]:  # 跳过表头
        parts = re.split(r"\s+", line)
        if len(parts) < 2:
            continue
        name = parts[0]
        try:
            pid = int(parts[1])
        except ValueError:
            continue
        if pid in seen:
            continue
        seen.add(pid)
        results.append((pid, name))
    return results


def command_port_who(port: int) -> None:
    """打印占用指定端口的进程信息"""
    if not isinstance(port, int) or port <= 0 or port > 65535:
        print("错误: 端口号无效，应为 1-65535 的整数")
        return

    # 1) 尝试 psutil
    results = _try_psutil(port)
    if not results:
        system = platform.system().lower()
        if system == 'windows':
            results = _windows_lookup(port)
        elif system == 'linux':
            results = _linux_lookup(port)
        elif system == 'darwin':
            results = _mac_lookup(port)
        else:
            results = []

    if not results:
        print(f"端口 {port} 未发现被占用或缺少权限/工具无法识别。")
        print("建议：以管理员/root 权限运行，或安装 psutil/lsof。")
        return

    print(f"端口 {port} 被以下进程占用：")
    for pid, name in results:
        print(f"- PID: {pid}\t进程: {name}")

