import sys
from typing import Any, Optional, Callable, Union

import questionary
from questionary import Style as QStyle

from rushconsole.choice import Choice
from rushconsole.result import Result


class ConsoleInput:
    def __init__(
            self,
            highlighted_style: str = '#00ffff',
            separator_style: str = '#cc5454',
            qmark_style: str = '#5f819d bold',
            question_style: str = '#00ffff bold',
            pointer_style: str = '#00ffff bold',
            answer_style: str = '#ffd700 bold',
            text_style: str = '#cccccc',
            disabled_style: str = '#858585 italic',
            error_style: str = '#ff0000 bold',
            header_style: str = '#5f819d bold',
            summary_style: str = '#5f819d bold',
            key_style: str = '#5f819d',
            value_style: str = '#ffd700'
    ):
        """
        初始化表单
        :param separator_style: 分隔线样式
        :param qmark_style: 问题标记样式
        :param question_style: 问题文本样式
        :param pointer_style: 光标指针样式
        :param answer_style: 答案文本样式
        :param text_style: 普通文本/描述文本样式
        :param disabled_style: 禁用选项样式
        :param error_style: 错误文本样式
        :param header_style: 标题样式
        :param summary_style: 摘要标题样式
        :param key_style: 摘要键样式
        :param value_style: 摘要值样式
        """
        self.answers: dict[str, Any] = {}
        self.questions: list[dict] = []

        # 创建兼容PyCharm终端的questionary样式
        # 移除了所有背景色，确保选中项无背景色
        self.style = QStyle([
            ('separator', f"fg:{separator_style}"),
            ('qmark', f"fg:{qmark_style}"),
            ('question', f"fg:{question_style}"),
            ('pointer', f"fg:{pointer_style}"),  # 仅保留指针样式
            ('answer', f"fg:{answer_style}"),
            ('text', f"fg:{text_style}"),
            ('disabled', f"fg:{disabled_style}"),
            ('error', f"fg:{error_style}"),
            ('header', f"fg:{header_style}"),
            ('summary', f"fg:{summary_style}"),
            ('key', f"fg:{key_style}"),
            ('value', f"fg:{value_style}"),
            # 使用指针指示当前选项，避免背景色
            ('highlighted', f'fg:{highlighted_style} bold'),  # 高亮当前选项（无背景色）
        ])

    def add_question(
            self,
            key: str,
            question_type: str,
            prompt: str,
            choices: Optional[list[Union[str, Choice]]] = None,
            default: Any = None,
            validate: Optional[Callable] = None,
            required: bool = True,
            description: str = ""
    ):
        """
        添加问题到表单
        :param key: 问题唯一标识
        :param question_type: 问题类型
        :param prompt: 问题提示文本
        :param choices: 选项列表
        :param default: 默认值
        :param validate: 验证函数
        :param required: 是否必填
        :param description: 问题描述
        """

        if choices is None:
            choices = []

        # 转换字符串选项为Choice对象
        processed_choices = []
        for _choice in choices:
            if isinstance(_choice, str):
                processed_choices.append(Choice(_choice, _choice, ""))
            else:
                processed_choices.append(_choice)

        self.questions.append({
            "key": key,
            "type": question_type,
            "prompt": prompt,
            "choices": processed_choices,
            "default": default,
            "validate": validate,
            "required": required,
            "description": description
        })

    @staticmethod
    def _create_validator(required, custom_validate):
        """创建验证函数"""

        def validator(value):
            if required and not value:
                return "此字段为必填项"

            if custom_validate:
                _result = custom_validate(value)
                if _result is not True:
                    if isinstance(_result, str):
                        return _result
                    return "输入验证失败"
            return True

        return validator

    def _create_questionary_question(self, question):
        """将内部问题格式转换为questionary格式"""
        q_type = question["type"]
        prompt_text = question["prompt"]
        description = question["description"]
        default = question["default"]
        required = question["required"]
        validate = question["validate"]
        choices = question["choices"]

        # 添加问题描述
        if description:
            prompt_text += f"\n[描述: {description}]"

        if q_type == "select":
            # 创建选择选项
            q_choices = []
            for _choice in choices:
                # 处理禁用选项
                title_text = _choice.name

                q_choices.append(questionary.Choice(
                    title=title_text,
                    value=_choice.value,
                    description=_choice.description,
                    disabled="不可用" if _choice.disabled else None
                ))

            return questionary.select(
                message=prompt_text,
                choices=q_choices,
                style=self.style,
                pointer="→",
                use_indicator=True,  # 使用指示器而非反色高亮
                use_arrow_keys=True  # 确保使用箭头键导航
            )

        elif q_type == "input":
            # 确保默认值是字符串
            default_str = str(default) if default is not None else ""
            return questionary.text(
                message=prompt_text,
                default=default_str,
                validate=self._create_validator(required, validate),
                style=self.style
            )

        elif q_type == "confirm":
            return questionary.confirm(
                message=prompt_text,
                default=default if default is not None else False,
                style=self.style
            )

        elif q_type == "checkbox":
            q_choices = []
            # 确保默认值是一个列表
            default_list = default if isinstance(default, list) else []

            for _choice in choices:
                # 默认选中状态
                checked = _choice.value in default_list

                # 处理禁用选项
                title_text = _choice.name
                if _choice.disabled:
                    title_text = f"{_choice.name} [不可用]"

                q_choices.append(questionary.Choice(
                    title=title_text,
                    value=_choice.value,
                    description=_choice.description,
                    checked=checked,
                    disabled="不可用" if _choice.disabled else None
                ))

            return questionary.checkbox(
                message=prompt_text,
                choices=q_choices,
                validate=lambda selected: True if not required or len(selected) > 0
                else "至少选择一个选项",
                style=self.style,
                pointer="→"
            )

        return None

    def run(self) -> Result:
        """运行表单并返回答案字典"""
        try:
            _answers = {}
            for question in self.questions:
                # 创建questionary问题
                q = self._create_questionary_question(question)
                if q is None:
                    continue

                # 获取答案
                answer = q.ask()
                if answer is None:  # 用户按Ctrl+C
                    print("\n操作已取消")
                    sys.exit(1)

                _answers[question["key"]] = answer
                print()  # 问题间空行

            return Result(_answers)

        except KeyboardInterrupt:
            print("\n\n操作已取消")
            sys.exit(1)