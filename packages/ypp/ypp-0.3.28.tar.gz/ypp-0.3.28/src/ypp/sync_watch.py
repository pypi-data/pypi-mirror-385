#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 平台下，监听目录 A 及其子目录的文件变化，并同步到目录 B。

实现策略：
- 仅支持 Windows（通过 platform.system 判断）
- 初次运行先进行一次全量同步（优先使用 robocopy，如不可用则回退到 Python 复制）
- 后续采用定期轮询（默认 1 秒）比较文件 mtime+size，复制新增/修改文件
- 可选 --delete：当 A 中文件被删除时，B 中对应文件也删除

说明：
- 为避免引入额外依赖（如 watchdog/pywin32），采用轻量轮询方案
- 复制使用 shutil.copy2 保留基本元数据
"""

from __future__ import annotations

import os
import time
import shutil
import platform
import subprocess
import glob
from typing import Dict, Tuple, Optional


FileSig = Tuple[float, int]  # (mtime, size)


def _is_windows() -> bool:
    return platform.system().lower() == "windows"


def _find_matching_path(base_path: str, target_pattern: str) -> Optional[str]:
    """
    在基础路径中查找匹配目标模式的路径。
    
    Args:
        base_path: 基础路径，如 E:\wo\kmultwppai_plugins
        target_pattern: 目标模式，如 apps\wpp-lui-v2\es
    
    Returns:
        找到的完整路径，如果未找到则返回 None
    """
    if not os.path.exists(base_path):
        return None
    
    # 构建搜索模式
    search_pattern = os.path.join(base_path, "**", target_pattern)
    
    # 使用 glob 递归搜索
    matches = glob.glob(search_pattern, recursive=True)
    
    if matches:
        # 返回第一个匹配的路径
        return matches[0]
    
    return None


def _find_path_by_pattern(base_path: str, target_pattern: str) -> Optional[str]:
    """
    通过模式匹配查找路径，搜索所有文件夹并匹配包含目标模式的路径。
    
    Args:
        base_path: 基础路径，如 E:\wo\plugin
        target_pattern: 目标模式，如 node_modules/@ks-kdocs-wpp/wpp-lui-v2/es
    
    Returns:
        找到的完整路径，如果未找到则返回 None
    """
    if not os.path.exists(base_path):
        return None
    
    # 将目标模式转换为路径分隔符
    target_pattern_normalized = target_pattern.replace('/', os.sep)
    
    # 递归搜索所有目录
    for root, dirs, files in os.walk(base_path):
        # 检查当前路径是否包含目标模式
        if target_pattern_normalized in root:
            # 进一步检查路径是否以目标模式结尾
            if root.endswith(target_pattern_normalized):
                return root
            # 或者检查路径中是否包含完整的目标模式
            elif target_pattern_normalized in root:
                # 找到包含目标模式的路径，返回第一个匹配的
                return root
    
    return None


def _auto_detect_paths(source_base: str, target_base: str, source_pattern: str = None, target_pattern: str = None) -> tuple[Optional[str], Optional[str]]:
    """
    自动检测源路径和目标路径。
    
    Args:
        source_base: 源基础路径
        target_base: 目标基础路径
        source_pattern: 源路径模式（可选）
        target_pattern: 目标路径模式（可选）
    
    Returns:
        (源完整路径, 目标完整路径) 的元组
    """
    source_path = None
    target_path = None
    
    # 如果提供了源路径模式，尝试自动检测
    if source_pattern:
        source_path = _find_path_by_pattern(source_base, source_pattern)
        if source_path:
            print(f"[auto-detect] 找到源路径: {source_path}")
        else:
            print(f"[auto-detect] 未找到匹配的源路径: {source_base} + {source_pattern}")
    
    # 如果提供了目标路径模式，尝试自动检测
    if target_pattern:
        target_path = _find_path_by_pattern(target_base, target_pattern)
        if target_path:
            print(f"[auto-detect] 找到目标路径: {target_path}")
        else:
            print(f"[auto-detect] 未找到匹配的目标路径: {target_base} + {target_pattern}")
    
    return source_path, target_path


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _scan_dir_signatures(root: str) -> Dict[str, FileSig]:
    """扫描目录，返回相对路径 -> (mtime, size)"""
    signatures: Dict[str, FileSig] = {}
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            abs_path = os.path.join(dirpath, name)
            try:
                st = os.stat(abs_path)
            except FileNotFoundError:
                continue
            rel_path = os.path.relpath(abs_path, root)
            signatures[rel_path] = (st.st_mtime, st.st_size)
    return signatures


def _copy_file(src_root: str, dst_root: str, rel_path: str) -> None:
    src = os.path.join(src_root, rel_path)
    dst = os.path.join(dst_root, rel_path)
    _ensure_dir(os.path.dirname(dst))
    shutil.copy2(src, dst)


def _remove_file(dst_root: str, rel_path: str) -> None:
    dst = os.path.join(dst_root, rel_path)
    try:
        os.remove(dst)
    except FileNotFoundError:
        pass


def _initial_sync_with_robocopy(src: str, dst: str) -> bool:
    """使用 robocopy 做一次初次同步（速度快，稳健）。返回是否成功调用。"""
    # /E 复制子目录（包括空目录），/COPY:DAT 复制数据/属性/时间，/R:0 不重试，/W:0 无等待
    # /NFL /NDL 减少日志，/NP 不显示进度，/XX 排除多余文件（不删除）
    cmd = [
        "robocopy", src, dst,
        "/E", "/COPY:DAT", "/R:0", "/W:0", "/NFL", "/NDL", "/NP"
    ]
    try:
        # 避免控制台编码差异导致解码异常，不读取文本输出
        completed = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    # robocopy 的返回码不遵循 0=成功，0/1 都可视为成功（有无复制的区别）
    return completed.returncode in (0, 1)


def _initial_sync_fallback(src: str, dst: str) -> None:
    for dirpath, dirnames, filenames in os.walk(src):
        rel_dir = os.path.relpath(dirpath, src)
        target_dir = os.path.join(dst, rel_dir) if rel_dir != "." else dst
        _ensure_dir(target_dir)
        for name in filenames:
            rel_path = os.path.normpath(os.path.join(rel_dir, name)) if rel_dir != "." else name
            _copy_file(src, dst, rel_path)


def command_sync_watch(source_dir: str, target_dir: str, interval: float = 1.0, delete: bool = False, auto_detect: bool = False, source_pattern: str = None, target_pattern: str = None) -> None:
    if not _is_windows():
        print("错误: 该命令当前仅支持 Windows 平台。")
        return
    if not source_dir or not target_dir:
        print("错误: 需要提供源目录和目标目录。")
        return
    
    # 如果启用自动检测
    if auto_detect:
        print("[auto-detect] 启用自动路径检测模式")
        detected_source, detected_target = _auto_detect_paths(source_dir, target_dir, source_pattern, target_pattern)
        
        if detected_source:
            source_dir = detected_source
        else:
            print(f"错误: 无法自动检测源路径: {source_dir}")
            if source_pattern:
                print(f"提示: 尝试在 {source_dir} 中查找模式 {source_pattern}")
            return
            
        if detected_target:
            target_dir = detected_target
        else:
            print(f"错误: 无法自动检测目标路径: {target_dir}")
            if target_pattern:
                print(f"提示: 尝试在 {target_dir} 中查找模式 {target_pattern}")
            return
    
    source_dir = os.path.abspath(source_dir)
    target_dir = os.path.abspath(target_dir)
    if not os.path.isdir(source_dir):
        print(f"错误: 源目录不存在: {source_dir}")
        return
    if not os.path.isdir(target_dir):
        print(f"错误: 目标目录不存在: {target_dir}")
        print(f"请确保目标目录存在后再运行同步命令")
        return

    print(f"[sync] 源: {source_dir}")
    print(f"[sync] 目标: {target_dir}")
    print("[sync] 正在进行初次同步...")

    if not _initial_sync_with_robocopy(source_dir, target_dir):
        _initial_sync_fallback(source_dir, target_dir)

    print("[sync] 初次同步完成，开始监听变更（Ctrl+C 退出）...")

    previous = _scan_dir_signatures(source_dir)

    try:
        while True:
            time.sleep(max(0.1, float(interval)))
            current = _scan_dir_signatures(source_dir)

            # 新增或修改
            for rel_path, sig in current.items():
                prev_sig = previous.get(rel_path)
                if prev_sig is None or prev_sig != sig:
                    try:
                        _copy_file(source_dir, target_dir, rel_path)
                        print(f"[sync] 更新: {rel_path}")
                    except Exception as e:
                        print(f"[sync] 复制失败: {rel_path} -> {e}")

            # 删除（可选）
            if delete:
                for rel_path in previous.keys() - current.keys():
                    try:
                        _remove_file(target_dir, rel_path)
                        print(f"[sync] 删除: {rel_path}")
                    except Exception as e:
                        print(f"[sync] 删除失败: {rel_path} -> {e}")

            previous = current
    except KeyboardInterrupt:
        print("\n同步已停止。")



