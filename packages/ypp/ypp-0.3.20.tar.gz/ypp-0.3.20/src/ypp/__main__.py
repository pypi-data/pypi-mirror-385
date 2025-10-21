#!/usr/bin/env python3
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

try:
    from .makefile_modifier import command_modify_makefile
    from .auto_build import command_auto_build
    from .init_commands import init_wpsmain, init_wpsweb
    from .vscode_config import command_code_webwps
    from .ppt_attributes import command_pptattr
    from .wsl_port_forward import command_wsl_port
    from .feedback_export import command_feedback_export, command_feedback_format
    from .common import (
        run_command, ensure_directory, path_exists_and_not_empty,
        get_config_path, load_config, save_config, get_workspace_dir
    )
except ImportError:
    from makefile_modifier import command_modify_makefile
    from auto_build import command_auto_build
    from init_commands import init_wpsmain, init_wpsweb
    from vscode_config import command_code_webwps
    from ppt_attributes import command_pptattr
    from wsl_port_forward import command_wsl_port
    from feedback_export import command_feedback_export, command_feedback_format
    from common import (
        run_command, ensure_directory, path_exists_and_not_empty,
        get_config_path, load_config, save_config, get_workspace_dir
    )





def is_linux_system() -> bool:
    """检查是否为 Linux 系统"""
    return platform.system().lower() == "linux"


def ng_sync(master_repo_path: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 同步仓库: {master_repo_path}")
    rc = run_command(["krepo-ng", "sync"], cwd_path=master_repo_path)
    if rc != 0:
        print("krepo-ng sync 失败", file=sys.stderr)
        sys.exit(rc)


def ng_worktree_add(master_repo_path: str, target_path: str, branch: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 创建 worktree -> {target_path} @ {branch}")
    rc = run_command(["krepo-ng", "worktree", "add", target_path, branch], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_sync(master_repo_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 同步仓库: {master_repo_path}")
    rc = run_command(["git", "pull"], cwd_path=master_repo_path)
    if rc != 0:
        print("git pull 失败", file=sys.stderr)
        sys.exit(rc)


def git_branch_exists(master_repo_path: str, branch: str) -> bool:
    has_local = run_command(["git", "show-ref", "--verify", f"refs/heads/{branch}"], cwd_path=master_repo_path) == 0
    return has_local


def git_worktree_add(master_repo_path: str, target_path: str, branch: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 创建 worktree -> {target_path} @ {branch}")
    rc = run_command(["git", "worktree", "add", target_path, branch], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_worktree_list(master_repo_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] worktree list @ {master_repo_path}")
    rc = run_command(["git", "worktree", "list"], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def ng_worktree_remove(master_repo_path: str, target_path: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 移除 worktree -> {target_path}")
    rc = run_command(["krepo-ng", "worktree", "remove", target_path], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_worktree_remove(master_repo_path: str, target_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 移除 worktree -> {target_path}")
    rc = run_command(["git", "worktree", "remove", target_path], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def command_add_generic_git(path_value: str, branch_value: str) -> None:
    """通用的 git 仓库 worktree 创建方法"""
    current_dir = os.getcwd()
    
    # 检查当前目录是否是 git 仓库
    if not os.path.isdir(os.path.join(current_dir, ".git")):
        print("错误: 当前目录不是 git 仓库", file=sys.stderr)
        sys.exit(1)
    
    target_path = os.path.join(current_dir, path_value)
    
    if not path_exists_and_not_empty(target_path):
        ensure_directory(target_path)
        git_sync(current_dir)
        git_worktree_add(current_dir, target_path, branch_value)
    
    print("完成。")


def command_add(path_value: str, branch_value: str) -> None:
    current_dir = os.getcwd()
    
    # 检查当前路径中是否有 wpsmain
    master_wpsmain_path = None
    if os.path.basename(current_dir) == "wpsmain":
        master_wpsmain_path = current_dir
    else:
        wpsmain_candidate = os.path.join(current_dir, "wpsmain")
        if os.path.isdir(wpsmain_candidate):
            master_wpsmain_path = wpsmain_candidate
    
    # 检查当前路径中是否有 wpsweb
    master_wpsweb_path = None
    if os.path.basename(current_dir) == "wpsweb":
        master_wpsweb_path = current_dir
    else:
        wpsweb_candidate = os.path.join(current_dir, "wpsweb")
        if os.path.isdir(wpsweb_candidate):
            master_wpsweb_path = wpsweb_candidate
    
    if not master_wpsmain_path and not master_wpsweb_path:
        print("未找到 wpsmain 或 wpsweb 目录，尝试使用通用 git 仓库方法")
        command_add_generic_git(path_value, branch_value)
        return
    
    target_root = os.path.join(current_dir, path_value)
    
    # 处理 wpsmain
    if master_wpsmain_path:
        target_wpsmain_path = os.path.join(target_root, "wpsmain")
        if not path_exists_and_not_empty(target_wpsmain_path):
            ensure_directory(target_wpsmain_path)
            ng_sync(master_wpsmain_path)
            ng_worktree_add(master_wpsmain_path, target_wpsmain_path, branch_value)
    
    # 处理 wpsweb
    if master_wpsweb_path:
        target_wpsweb_path = os.path.join(target_root, "wpsweb")
        if not path_exists_and_not_empty(target_wpsweb_path):
            ensure_directory(target_wpsweb_path)
            git_sync(master_wpsweb_path)
            git_worktree_add(master_wpsweb_path, target_wpsweb_path, branch_value)

    print("完成。")


def command_list() -> None:
    current_dir = os.getcwd()
    
    # 检查当前路径中是否有 wpsweb
    wpsweb_path = None
    if os.path.basename(current_dir) == "wpsweb":
        wpsweb_path = current_dir
    else:
        # 在当前路径中查找 wpsweb
        wpsweb_candidate = os.path.join(current_dir, "wpsweb")
        if os.path.isdir(wpsweb_candidate):
            wpsweb_path = wpsweb_candidate
    
    # 检查当前路径中是否有 wpsmain
    wpsmain_path = None
    if os.path.basename(current_dir) == "wpsmain":
        wpsmain_path = current_dir
    else:
        # 在当前路径中查找 wpsmain
        wpsmain_candidate = os.path.join(current_dir, "wpsmain")
        if os.path.isdir(wpsmain_candidate):
            wpsmain_path = wpsmain_candidate
    
    # 执行相应的 git_worktree_list
    if wpsweb_path and os.path.isdir(wpsweb_path):
        print("=== wpsweb worktrees ===")
        git_worktree_list(wpsweb_path)
        print()
    
    if wpsmain_path and os.path.isdir(wpsmain_path):
        print("=== wpsmain worktrees ===")
        git_worktree_list(wpsmain_path)
        print()

    
    
    if not wpsweb_path and not wpsmain_path:
        # 检查当前目录是否是 git 仓库
        if os.path.isdir(os.path.join(current_dir, ".git")):
            print("=== 当前 git 仓库 worktrees ===")
            git_worktree_list(current_dir)
        else:
            print("未找到 wpsweb、wpsmain 目录或 git 仓库", file=sys.stderr)
            sys.exit(1)


def command_remove_generic_git(path_value: str) -> None:
    """通用的 git 仓库 worktree 移除方法"""
    current_dir = os.getcwd()
    
    # 检查当前目录是否是 git 仓库
    if not os.path.isdir(os.path.join(current_dir, ".git")):
        print("错误: 当前目录不是 git 仓库", file=sys.stderr)
        sys.exit(1)
    
    target_path = os.path.join(current_dir, path_value)
    
    if os.path.exists(target_path):
        git_worktree_remove(current_dir, target_path)
        print(f"已删除 worktree: {target_path}")
    else:
        print(f"worktree 不存在: {target_path}")
    
    print("完成。")


def command_remove(path_value: str) -> None:
    current_dir = os.getcwd()
    
    # 检查当前路径中是否有 wpsmain
    master_wpsmain_path = None
    if os.path.basename(current_dir) == "wpsmain":
        master_wpsmain_path = current_dir
    else:
        wpsmain_candidate = os.path.join(current_dir, "wpsmain")
        if os.path.isdir(wpsmain_candidate):
            master_wpsmain_path = wpsmain_candidate
    
    # 检查当前路径中是否有 wpsweb
    master_wpsweb_path = None
    if os.path.basename(current_dir) == "wpsweb":
        master_wpsweb_path = current_dir
    else:
        wpsweb_candidate = os.path.join(current_dir, "wpsweb")
        if os.path.isdir(wpsweb_candidate):
            master_wpsweb_path = wpsweb_candidate
    
    if not master_wpsmain_path and not master_wpsweb_path:
        print("未找到 wpsmain 或 wpsweb 目录，尝试使用通用 git 仓库方法")
        command_remove_generic_git(path_value)
        return
    
    # 处理 wpsmain
    if master_wpsmain_path:
        remove_wpsmain_path = os.path.join(path_value, "wpsmain")
        if os.path.exists(remove_wpsmain_path):
            ng_worktree_remove(master_wpsmain_path, remove_wpsmain_path)
        else:
            print(f"wpsmain worktree 不存在: {remove_wpsmain_path}")
    
    # 处理 wpsweb
    if master_wpsweb_path:
        remove_wpsweb_path = os.path.join(path_value, "wpsweb")
        if os.path.exists(remove_wpsweb_path):
            git_worktree_remove(master_wpsweb_path, remove_wpsweb_path)
        else:
            print(f"wpsweb worktree 不存在: {remove_wpsweb_path}")

    # 删除整个路径目录
    if os.path.exists(path_value):
        try:
            shutil.rmtree(path_value)
            print(f"已删除目录: {path_value}")
        except OSError as e:
            print(f"删除目录失败: {path_value}, 错误: {e}", file=sys.stderr)
    else:
        print(f"目录不存在: {path_value}")
    
    print("完成。")










def main() -> None:
    parser = argparse.ArgumentParser(description="多分支 worktree 管理工具（子命令版）")
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # worktree 子命令：worktree 相关操作
    worktree_parser = subparsers.add_parser("worktree", aliases=["wt"], help="worktree 相关操作")
    worktree_subparsers = worktree_parser.add_subparsers(dest="worktree_command", metavar="worktree_command")
    
    # worktree add 子命令：添加 wpsmain 与 wpsweb 的 worktree
    worktree_add_parser = worktree_subparsers.add_parser("add", help="创建 worktree。用法: worktree add <path> <branch>")
    worktree_add_parser.add_argument("path", help="目标路径名（对应 ~/<path>/...）")
    worktree_add_parser.add_argument("branch", help="要创建/切换的分支名")

    # worktree list 子命令：列出 wpsmain 与 wpsweb 的 worktree
    worktree_subparsers.add_parser("list", help="列出 master 下 wpsmain 和 wpsweb 的 worktree")

    # worktree remove 子命令：移除 wpsmain 与 wpsweb 的 worktree
    worktree_remove_parser = worktree_subparsers.add_parser("remove", help="移除 worktree。用法: worktree remove <path>")
    worktree_remove_parser.add_argument("path", help="要移除的路径名（对应 ~/<path>/...）")


    # modify 子命令：修改 wpsweb/server/Makefile 修改 wpsweb/build_server.sh
    modify_parser = subparsers.add_parser("modify", aliases=["m"], help="修改 wpsweb/server/Makefile 和生成 build_server.sh（仅限 Linux） , 为Coding模式创建VSCode配置文件")
    modify_parser.add_argument("--force", action="store_true", help="强制在非 Linux 系统上运行（不推荐）")
    modify_parser.add_argument("mode", nargs="?", choices=["coding"], help="模式选择：coding模式创建VSCode配置文件")

    # build 子命令：自动编译 wpsmain
    subparsers.add_parser("build", help="自动编译 wpsmain（在 Docker 中执行）,并编译wpsweb")

    # code 子命令：创建VSCode配置文件
    code_parser = subparsers.add_parser("code", help="创建VSCode配置文件")
    code_parser.add_argument("type", choices=["wpsweb"], help="配置文件类型")

    # init 子命令：初始化仓库
    init_parser = subparsers.add_parser("init", help="初始化仓库。用法: init [type]")
    init_parser.add_argument("type", nargs="?", choices=["wpsmain", "wpsweb"], help="要初始化的仓库类型（可选，为空时依次执行 wpsmain 和 wpsweb）")

    # pptattr 子命令：读取 PPTX 文件属性
    pptattr_parser = subparsers.add_parser("pptattr", help="读取 PPTX 文件的自定义属性。用法: pptattr <filepath> [--clean]")
    pptattr_parser.add_argument("filepath", help="PPTX 文件路径")
    pptattr_parser.add_argument("--clean", action="store_true", help="清除指定属性（lastModifiedBy 和 ICV）并保存到原文件")

    # wsl 子命令：WSL 相关操作
    wsl_parser = subparsers.add_parser("wsl", help="WSL 相关操作")
    wsl_subparsers = wsl_parser.add_subparsers(dest="wsl_command", metavar="wsl_command")
    
    # wsl port 子命令：端口转发
    wsl_port_parser = wsl_subparsers.add_parser("port", help="WSL 端口转发管理")
    wsl_port_parser.add_argument("action", nargs="?", choices=["add", "remove", "list"], default="add", 
                                help="操作类型：add(添加), remove(移除), list(列出)")
    wsl_port_parser.add_argument("host_port", nargs="?", type=int, help="本机端口")
    wsl_port_parser.add_argument("wsl_port", nargs="?", type=int, help="WSL 端口")

    # feedback 子命令：反馈导出
    feedback_parser = subparsers.add_parser("feedback", help="反馈导出相关操作")
    feedback_subparsers = feedback_parser.add_subparsers(dest="feedback_command", metavar="feedback_command")
    
    # feedback export 子命令：导出反馈数据
    feedback_export_parser = feedback_subparsers.add_parser("export", help="从Excel文件导出WPP或P组件的对话详情")
    feedback_export_parser.add_argument("file_path", help="Excel文件路径")
    feedback_export_parser.add_argument("--sheet", "-s", help="指定要读取的sheet表名（可选，默认读取最新的表）")
    
    # feedback format 子命令：格式化客服原语
    feedback_subparsers.add_parser("format", help="格式化客服原语，在特定关键词前添加换行符")

    args = parser.parse_args()

    if args.command in ["worktree", "wt"]:
        if hasattr(args, 'worktree_command') and args.worktree_command == "add":
            command_add(args.path, args.branch)
        elif hasattr(args, 'worktree_command') and args.worktree_command == "list":
            command_list()
        elif hasattr(args, 'worktree_command') and args.worktree_command == "remove":
            command_remove(args.path)
        else:
            worktree_parser.print_help()
        return
    if args.command == "modify":
        if not is_linux_system() and not getattr(args, 'force', False):
            print("错误: modify 命令仅在 Linux 系统上支持", file=sys.stderr)
            print(f"当前系统: {platform.system()}", file=sys.stderr)
            print("提示: 可以使用 --force 参数强制运行（不推荐）", file=sys.stderr)
            sys.exit(1)
        if not is_linux_system() and getattr(args, 'force', False):
            print(f"警告: 在 {platform.system()} 系统上强制运行 modify 命令", file=sys.stderr)
        command_modify_makefile(mode=getattr(args, 'mode', None))
        return
    if args.command == "build":
        command_auto_build()
        return
    if args.command == "code":
        if args.type == "wpsweb":
            command_code_webwps()
        return
    if args.command == "init":
        if args.type == "wpsmain":
            init_wpsmain()
        elif args.type == "wpsweb":
            init_wpsweb()
        else:
            # 如果 type 为空，依次执行 wpsmain 和 wpsweb
            print("未指定仓库类型，将依次初始化 wpsmain 和 wpsweb...")
            init_wpsmain()
            init_wpsweb()
        return
    if args.command == "pptattr":
        command_pptattr(args.filepath, args.clean)
        return
    if args.command == "wsl":
        if hasattr(args, 'wsl_command') and args.wsl_command == "port":
            # 处理端口转发命令
            if args.action == "list":
                command_wsl_port(action="list")
            elif args.action == "remove":
                if args.host_port is None:
                    print("错误: 移除端口转发需要指定本机端口", file=sys.stderr)
                    print("用法: ypp wsl port remove <本机端口>", file=sys.stderr)
                    sys.exit(1)
                command_wsl_port(host_port=args.host_port, action="remove")
            else:  # add
                if args.host_port is None or args.wsl_port is None:
                    print("错误: 添加端口转发需要指定本机端口和 WSL 端口", file=sys.stderr)
                    print("用法: ypp wsl port <本机端口> <WSL端口>", file=sys.stderr)
                    sys.exit(1)
                command_wsl_port(host_port=args.host_port, wsl_port=args.wsl_port, action="add")
        else:
            wsl_parser.print_help()
        return
    if args.command == "feedback":
        if hasattr(args, 'feedback_command') and args.feedback_command == "export":
            command_feedback_export(args.file_path, getattr(args, 'sheet', None))
        elif hasattr(args, 'feedback_command') and args.feedback_command == "format":
            command_feedback_format()
        else:
            feedback_parser.print_help()
        return

    parser.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()

