from openai import OpenAI
from typing import Dict, Any, Optional, List
import os
from autoterminal.utils.logger import logger


class LLMClient:
    """LLM客户端，封装OpenAI API调用"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.info("初始化 LLM 客户端")
        logger.debug(f"使用模型: {config.get('model')}, Base URL: {config.get('base_url')}")
        self.client = OpenAI(
            api_key=config.get('api_key'),
            base_url=config.get('base_url')
        )

    def generate_command(self, user_input: str, prompt: Optional[str] = None,
                         history: Optional[List[Dict[str, Any]]] = None,
                         current_dir_content: Optional[List[str]] = None,
                         shell_history: Optional[List[str]] = None,
                         last_executed_command: str = "") -> str:
        """根据用户输入生成命令"""
        # 根据用户输入是否为空选择不同的提示词
        if not user_input:
            if not prompt:
                prompt = self.config.get(
                    'recommendation_prompt',
                    '你现在是一个终端助手，根据上下文自动推荐命令：当用户没有输入时，基于最近执行的命令历史和当前目录内容，智能推荐最可能需要的终端命令（仅当有明确上下文线索时）；当用户输入命令需求时，生成对应命令。仅输出纯命令文本，不要任何解释或多余内容！')
        else:
            if not prompt:
                prompt = self.config.get(
                    'default_prompt',
                    '你现在是一个终端助手，用户输入想要生成的命令,你来输出一个命令,不要任何多余的文本!')

        # 构建系统提示，包含上下文信息
        system_prompt = prompt

        # 添加历史命令上下文
        if history:
            history_context = "\n最近执行的命令历史:\n"
            for i, entry in enumerate(reversed(history), 1):
                history_context += f"{i}. 用户输入: {entry.get('user_input', '')} -> 生成命令: {entry.get('generated_command', '')}\n"
            system_prompt += history_context

        # 添加当前目录内容上下文
        if current_dir_content:
            dir_context = "\n当前目录下的文件和文件夹:\n" + "\n".join(current_dir_content)
            system_prompt += dir_context

        # 添加系统 Shell 历史上下文
        if shell_history:
            shell_context = "\n系统Shell最近执行的命令:\n"
            for i, cmd in enumerate(shell_history, 1):
                shell_context += f"{i}. {cmd}\n"
            system_prompt += shell_context

        # 当用户输入为空时，使用特殊的提示来触发推荐模式
        if not user_input:
            user_content = f"根据提供的上下文信息，推荐一个最可能需要的终端命令（仅当有明确的上下文线索时）。如果上下文信息不足以确定一个有用的命令，则返回空。请直接返回一个可执行的终端命令，不要包含任何解释或其他文本。例如：ls -la 或 git status。特别注意：不要使用echo命令来列出文件，应该使用ls命令。推荐命令时请考虑最近执行的命令历史，避免重复推荐相同的命令。最后执行的命令是: {last_executed_command}。如果当前目录有pyproject.toml或setup.py文件，可以考虑使用pip list查看已安装的包。"
        else:
            user_content = user_input

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        try:
            logger.info(f"调用 LLM 生成命令，用户输入: '{user_input if user_input else '(推荐模式)'}'")
            logger.debug(f"系统提示长度: {len(system_prompt)} 字符")

            response = self.client.chat.completions.create(
                model=self.config.get('model'),
                messages=messages,
                temperature=0.1,
                max_tokens=100
            )

            command = response.choices[0].message.content.strip()
            logger.info(f"LLM 返回命令: '{command}'")
            return command
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            raise Exception(f"LLM调用失败: {str(e)}")
