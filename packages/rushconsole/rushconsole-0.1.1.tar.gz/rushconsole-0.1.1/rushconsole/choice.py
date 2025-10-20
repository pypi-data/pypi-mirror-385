from dataclasses import dataclass
from typing import Any


@dataclass
class Choice:
    """表示单个选项的类"""
    name: str  # 显示名称
    value: Any  # 关联的值
    description: str  # 选项描述
    disabled: bool = False  # 是否禁用选项
