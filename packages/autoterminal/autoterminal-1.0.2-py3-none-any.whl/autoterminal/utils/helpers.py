import os
from typing import List
from autoterminal.utils.logger import logger


def clean_command(command: str) -> str:
    """清理命令字符串"""
    # 移除可能的引号和多余空格
    command = command.strip()
    if command.startswith('"') and command.endswith('"'):
        command = command[1:-1]
    if command.startswith("'") and command.endswith("'"):
        command = command[1:-1]
    return command.strip()


def get_shell_history(count: int = 20) -> List[str]:
    """
    获取系统 Shell 历史命令

    Args:
        count: 获取最近的命令数量

    Returns:
        最近执行的 Shell 命令列表
    """
    history_commands = []

    try:
        # 尝试从环境变量获取历史文件路径
        histfile = os.getenv('HISTFILE')

        # 如果没有 HISTFILE，根据 SHELL 推断
        if not histfile or not os.path.exists(histfile):
            home_dir = os.path.expanduser("~")
            shell = os.getenv('SHELL', '')

            # 根据当前 Shell 类型优先尝试对应的历史文件
            possible_files = []
            if 'zsh' in shell:
                possible_files = [
                    os.path.join(home_dir, ".zsh_history"),
                    os.path.join(home_dir, ".zhistory"),
                    os.path.join(home_dir, ".bash_history"),
                ]
            else:  # bash 或其他
                possible_files = [
                    os.path.join(home_dir, ".bash_history"),
                    os.path.join(home_dir, ".zsh_history"),
                    os.path.join(home_dir, ".zhistory"),
                ]

            for file_path in possible_files:
                if os.path.exists(file_path):
                    histfile = file_path
                    break

        if histfile and os.path.exists(histfile):
            logger.debug(f"读取 Shell 历史文件: {histfile}")

            with open(histfile, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # 过滤和清理命令
            for line in lines:
                line = line.strip()

                # 跳过空行
                if not line:
                    continue

                # 处理 zsh 扩展历史格式 (: timestamp:duration;command)
                if line.startswith(':'):
                    parts = line.split(';', 1)
                    if len(parts) > 1:
                        line = parts[1].strip()

                # 过滤敏感命令（包含密码、密钥等）
                sensitive_keywords = [
                    'password',
                    'passwd',
                    'secret',
                    'key',
                    'token',
                    'api_key',
                    'api-key']
                if any(keyword in line.lower() for keyword in sensitive_keywords):
                    continue

                # 过滤重复命令（保持顺序，只保留最后一次出现）
                if line in history_commands:
                    history_commands.remove(line)

                history_commands.append(line)

            # 返回最近的 N 条命令
            result = history_commands[-count:] if len(
                history_commands) > count else history_commands
            logger.debug(f"成功获取 {len(result)} 条 Shell 历史命令")
            return result
        else:
            logger.warning("未找到 Shell 历史文件")
            return []

    except Exception as e:
        logger.warning(f"获取 Shell 历史失败: {e}")
        return []
