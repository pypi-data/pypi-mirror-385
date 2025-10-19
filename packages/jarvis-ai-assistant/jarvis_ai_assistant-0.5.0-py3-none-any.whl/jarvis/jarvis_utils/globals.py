# -*- coding: utf-8 -*-
"""
全局变量和配置模块
该模块管理Jarvis系统的全局状态和配置。
包含：
- 全局代理管理
- 带有自定义主题的控制台配置
- 环境初始化
"""
import os

# 全局变量：保存消息历史
from typing import Any, Dict, List, Optional

message_history: List[str] = []
MAX_HISTORY_SIZE = 50

# 短期记忆存储
short_term_memories: List[Dict[str, Any]] = []
MAX_SHORT_TERM_MEMORIES = 100

import colorama
from rich.console import Console
from rich.theme import Theme

# 初始化colorama以支持跨平台的彩色文本
colorama.init()
# 禁用tokenizers并行以避免多进程问题
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# 全局代理管理
global_agents: Dict[str, Any] = {}
current_agent_name: str = ""
# 表示与大模型交互的深度(>0表示正在交互)
g_in_chat: int = 0
# 表示是否接收到中断信号
g_interrupt: int = 0
# 使用自定义主题配置rich控制台
custom_theme = Theme(
    {
        "INFO": "yellow",
        "WARNING": "yellow",
        "ERROR": "red",
        "SUCCESS": "green",
        "SYSTEM": "cyan",
        "CODE": "green",
        "RESULT": "blue",
        "PLANNING": "magenta",
        "PROGRESS": "white",
        "DEBUG": "blue",
        "USER": "green",
        "TOOL": "yellow",
    }
)
console = Console(theme=custom_theme)


def make_agent_name(agent_name: str) -> str:
    """
    通过附加后缀生成唯一的代理名称（如果必要）。

    参数：
        agent_name: 基础代理名称

    返回：
        str: 唯一的代理名称
    """
    if agent_name in global_agents:
        i = 1
        while f"{agent_name}_{i}" in global_agents:
            i += 1
        return f"{agent_name}_{i}"
    return agent_name


def get_agent(agent_name: str) -> Any:
    """
    获取指定名称的代理实例。

    参数：
        agent_name: 代理名称

    返回：
        Any: 代理实例，如果不存在则返回None
    """
    return global_agents.get(agent_name)


def set_agent(agent_name: str, agent: Any) -> None:
    """
    设置当前代理并将其添加到全局代理集合中。

    参数：
        agent_name: 代理名称
        agent: 代理对象
    """
    global_agents[agent_name] = agent
    global current_agent_name
    current_agent_name = agent_name


def get_agent_list() -> str:
    """
    获取表示当前代理状态的格式化字符串。

    返回：
        str: 包含代理数量和当前代理名称的格式化字符串
    """
    return (
        "[" + str(len(global_agents)) + "]" + current_agent_name
        if global_agents
        else ""
    )


def delete_agent(agent_name: str) -> None:
    """
    从全局代理集合中删除一个代理。

    参数：
        agent_name: 要删除的代理名称
    """
    if agent_name in global_agents:
        del global_agents[agent_name]
        global current_agent_name
        current_agent_name = ""


def set_in_chat(status: bool) -> None:
    """
    设置与大模型交互的状态。

    参数:
        status: True表示增加交互深度，False表示减少
    """
    global g_in_chat
    if status:
        g_in_chat += 1
    else:
        g_in_chat = max(0, g_in_chat - 1)


def get_in_chat() -> bool:
    """
    获取当前是否正在与大模型交互的状态。

    返回:
        bool: 当前交互状态(>0表示正在交互)
    """
    return g_in_chat > 0


def set_interrupt(status: bool) -> None:
    """
    设置中断信号状态。

    参数:
        status: 中断状态
    """
    global g_interrupt
    if status:
        g_interrupt += 1
    else:
        g_interrupt = 0


def get_interrupt() -> int:
    """
    获取当前中断信号状态。

    返回:
        int: 当前中断计数
    """
    return g_interrupt


def set_last_message(message: str) -> None:
    """
    将消息添加到历史记录中。

    参数:
        message: 要保存的消息
    """
    global message_history
    if message:
        # 避免重复添加
        if not message_history or message_history[-1] != message:
            message_history.append(message)
            if len(message_history) > MAX_HISTORY_SIZE:
                message_history.pop(0)


def get_last_message() -> str:
    """
    获取最后一条消息。

    返回:
        str: 最后一条消息，如果历史记录为空则返回空字符串
    """
    global message_history
    if message_history:
        return message_history[-1]
    return ""


def get_message_history() -> List[str]:
    """
    获取完整的消息历史记录。

    返回:
        List[str]: 消息历史列表
    """
    global message_history
    return message_history


def add_short_term_memory(memory_data: Dict[str, Any]) -> None:
    """
    添加短期记忆到全局存储。

    参数:
        memory_data: 包含记忆信息的字典
    """
    global short_term_memories
    short_term_memories.append(memory_data)
    # 如果超过最大数量，删除最旧的记忆
    if len(short_term_memories) > MAX_SHORT_TERM_MEMORIES:
        short_term_memories.pop(0)


def get_short_term_memories(tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    获取短期记忆，可选择按标签过滤。

    参数:
        tags: 用于过滤的标签列表（可选）

    返回:
        List[Dict[str, Any]]: 符合条件的短期记忆列表，按创建时间降序排列
    """
    global short_term_memories

    # 获取记忆副本
    memories_copy = short_term_memories.copy()

    # 按标签过滤（如果提供了标签）
    if tags:
        filtered_memories = []
        for memory in memories_copy:
            memory_tags = memory.get("tags", [])
            if any(tag in memory_tags for tag in tags):
                filtered_memories.append(memory)
        memories_copy = filtered_memories

    # 按创建时间排序（最新的在前）
    memories_copy.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return memories_copy


def clear_short_term_memories() -> None:
    """
    清空所有短期记忆。
    """
    global short_term_memories
    short_term_memories.clear()


def get_all_memory_tags() -> Dict[str, List[str]]:
    """
    获取所有记忆类型中的标签集合。
    每个类型最多返回200个标签，超过时随机提取。

    返回:
        Dict[str, List[str]]: 按记忆类型分组的标签列表
    """
    from pathlib import Path
    import json
    import random
    from jarvis.jarvis_utils.config import get_data_dir

    tags_by_type: Dict[str, List[str]] = {
        "short_term": [],
        "project_long_term": [],
        "global_long_term": [],
    }

    MAX_TAGS_PER_TYPE = 200

    # 获取短期记忆标签
    short_term_tags = set()
    for memory in short_term_memories:
        short_term_tags.update(memory.get("tags", []))
    short_term_tags_list = sorted(list(short_term_tags))
    if len(short_term_tags_list) > MAX_TAGS_PER_TYPE:
        tags_by_type["short_term"] = sorted(
            random.sample(short_term_tags_list, MAX_TAGS_PER_TYPE)
        )
    else:
        tags_by_type["short_term"] = short_term_tags_list

    # 获取项目长期记忆标签
    project_memory_dir = Path(".jarvis/memory")
    if project_memory_dir.exists():
        project_tags = set()
        for memory_file in project_memory_dir.glob("*.json"):
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    memory_data = json.load(f)
                    project_tags.update(memory_data.get("tags", []))
            except Exception:
                pass
        project_tags_list = sorted(list(project_tags))
        if len(project_tags_list) > MAX_TAGS_PER_TYPE:
            tags_by_type["project_long_term"] = sorted(
                random.sample(project_tags_list, MAX_TAGS_PER_TYPE)
            )
        else:
            tags_by_type["project_long_term"] = project_tags_list

    # 获取全局长期记忆标签
    global_memory_dir = Path(get_data_dir()) / "memory" / "global_long_term"
    if global_memory_dir.exists():
        global_tags = set()
        for memory_file in global_memory_dir.glob("*.json"):
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    memory_data = json.load(f)
                    global_tags.update(memory_data.get("tags", []))
            except Exception:
                pass
        global_tags_list = sorted(list(global_tags))
        if len(global_tags_list) > MAX_TAGS_PER_TYPE:
            tags_by_type["global_long_term"] = sorted(
                random.sample(global_tags_list, MAX_TAGS_PER_TYPE)
            )
        else:
            tags_by_type["global_long_term"] = global_tags_list

    return tags_by_type
