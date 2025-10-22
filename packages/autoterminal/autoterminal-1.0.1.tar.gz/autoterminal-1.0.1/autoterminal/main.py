#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import glob

from autoterminal.config.loader import ConfigLoader
from autoterminal.config.manager import ConfigManager
from autoterminal.llm.client import LLMClient
from autoterminal.utils.helpers import clean_command, get_shell_history
from autoterminal.history import HistoryManager
from autoterminal.utils.logger import logger


def main():
    """主程序入口"""
    logger.info("AutoTerminal 启动")

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AutoTerminal - 智能终端工具')
    parser.add_argument('user_input', nargs='*', help='用户输入的自然语言命令')
    parser.add_argument('--api-key', help='API密钥')
    parser.add_argument('--base-url', help='Base URL')
    parser.add_argument('--model', help='模型名称')
    parser.add_argument('--history-count', type=int, help='历史命令数量')

    args = parser.parse_args()

    # 合并用户输入
    user_input = ' '.join(args.user_input).strip()
    logger.debug(f"用户输入: '{user_input}'")

    # 加载配置
    logger.debug("加载配置文件")
    config_loader = ConfigLoader()
    config = config_loader.get_config()

    # 命令行参数优先级最高
    if args.api_key:
        config['api_key'] = args.api_key
    if args.base_url:
        config['base_url'] = args.base_url
    if args.model:
        config['model'] = args.model

    # 获取历史命令数量配置
    history_count = args.history_count or config.get('max_history', 10)

    # 如果配置不完整，使用配置管理器初始化
    config_manager = ConfigManager()
    if not all([config.get('api_key'), config.get('base_url'), config.get('model')]):
        config = config_manager.get_or_create_config()
        if not config:
            logger.error("缺少必要的配置参数，请通过命令行参数或配置文件提供API密钥、Base URL和模型名称。")
            return 1

    # 如果有命令行参数输入，直接处理
    if user_input:
        # 初始化历史管理器
        history_manager = HistoryManager(max_history=history_count)

        # 获取历史命令
        history = history_manager.get_recent_history(history_count)

        # 获取当前目录内容
        try:
            current_dir_content = glob.glob("*")
        except Exception as e:
            logger.warning(f"无法获取当前目录内容: {e}")
            current_dir_content = []

        # 获取系统 Shell 历史
        shell_history = get_shell_history()  # 使用默认值 20

        # 初始化LLM客户端
        try:
            llm_client = LLMClient(config)
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            return 1

        # 调用LLM生成命令
        try:
            generated_command = llm_client.generate_command(
                user_input=user_input,
                history=history,
                current_dir_content=current_dir_content,
                shell_history=shell_history
            )
            cleaned_command = clean_command(generated_command)

            # 优化输出格式
            print(f"\033[1;32m$\033[0m {cleaned_command}")
            print("\033[1;37mPress Enter to execute...\033[0m")

            # 等待用户回车确认执行
            try:
                input()

                # 在用户的环境中执行命令
                logger.info(f"执行命令: {cleaned_command}")
                os.system(cleaned_command)

                # 记录到历史
                history_manager.add_command(user_input, cleaned_command)
                logger.debug("命令已添加到历史记录")
            except EOFError:
                print("\n输入已取消。")
                return 0
            except Exception as exec_e:
                logger.error(f"命令执行失败: {exec_e}")
                return 1

        except Exception as e:
            logger.error(f"命令生成失败: {e}")
            return 1

        return 0
    else:
        # 处理空输入情况 - 生成基于上下文的推荐命令
        history_manager = HistoryManager(max_history=history_count)
        history = history_manager.get_recent_history(history_count)

        try:
            current_dir_content = glob.glob("*")
        except Exception as e:
            logger.warning(f"无法获取当前目录内容: {e}")
            current_dir_content = []

        # 获取系统 Shell 历史
        shell_history = get_shell_history()  # 使用默认值 20

        try:
            llm_client = LLMClient(config)
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            return 1

        # 获取最后执行的命令以避免重复推荐
        last_executed_command = history_manager.get_last_executed_command()

        try:
            recommendation = llm_client.generate_command(
                user_input="",
                history=history,
                current_dir_content=current_dir_content,
                shell_history=shell_history,
                last_executed_command=last_executed_command
            )
            cleaned_recommendation = clean_command(recommendation)

            if cleaned_recommendation.strip():
                print(f"\033[1;34m💡 建议命令:\033[0m {cleaned_recommendation}")
                print("\033[1;37mPress Enter to execute, or Ctrl+C to cancel...\033[0m")
                try:
                    input()
                    logger.info(f"执行推荐命令: {cleaned_recommendation}")
                    os.system(cleaned_recommendation)
                    history_manager.add_command("自动推荐", cleaned_recommendation)
                    logger.debug("推荐命令已添加到历史记录")
                except EOFError:
                    print("\n输入已取消。")
                    return 0
                except Exception as exec_e:
                    logger.error(f"命令执行失败: {exec_e}")
                    return 1
            else:
                print("没有找到相关的命令建议。")
        except Exception as e:
            logger.error(f"命令推荐生成失败: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
