"""方向C：输出清洗管道

负责清洗模型输出中的Markdown、LaTeX、多余符号等问题，
确保最终提交给评测系统的答案格式规范、易于解析。
"""

import re
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CleaningReport:
    """清洗报告"""
    original: str
    cleaned: str
    changes: list
    is_valid: bool


class OutputCleaner:
    """输出清洗器"""

    # LaTeX常见符号映射
    LATEX_SYMBOL_MAP = {
        r"\times": "×",
        r"\cdot": "·",
        r"\div": "÷",
        r"\pm": "±",
        r"\mp": "∓",
        r"\leq": "≤",
        r"\le": "≤",
        r"\geq": "≥",
        r"\ge": "≥",
        r"\neq": "≠",
        r"\ne": "≠",
        r"\approx": "≈",
        r"\infty": "∞",
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\pi": "π",
        r"\theta": "θ",
        r"\sqrt": "√",
    }

    @staticmethod
    def clean_response(response: Dict[str, Any]) -> Dict[str, str]:
        """清洗整个响应字典"""
        
        cleaned = {}
        for key, value in response.items():
            if key in ["question_id"]:
                # question_id 保持原样
                cleaned[key] = str(value)
            elif key in ["reasoning_process", "answer"]:
                # 这两个字段进行完整清洗
                cleaned[key] = OutputCleaner.clean_text(str(value))
            else:
                # 其他字段保持原样
                cleaned[key] = value

        return cleaned

    @staticmethod
    def clean_text(text: str) -> str:
        """清洗文本内容"""
        
        if not text:
            return ""

        # 1. 移除代码块标记
        text = OutputCleaner._remove_code_blocks(text)

        # 2. 移除Markdown公式块
        text = OutputCleaner._remove_markdown_formulas(text)

        # 3. 清洗LaTeX公式
        text = OutputCleaner._clean_latex_formulas(text)

        # 4. 替换LaTeX符号
        text = OutputCleaner._replace_latex_symbols(text)

        # 5. 标准化空格
        text = OutputCleaner._normalize_spaces(text)

        # 6. 移除头尾多余符号
        text = text.strip()
        text = re.sub(r'^[。，、；：\s]+', '', text)  # 头部
        text = re.sub(r'[。，、；：\s]+$', '', text)  # 尾部

        return text

    @staticmethod
    def _remove_code_blocks(text: str) -> str:
        """移除代码块：```...```"""
        
        # 移除带语言标记的代码块
        text = re.sub(r'```\w*\n(.*?)```', r'\1', text, flags=re.DOTALL)
        # 移除普通代码块
        text = re.sub(r'```(.*?)```', r'\1', text, flags=re.DOTALL)
        return text

    @staticmethod
    def _remove_markdown_formulas(text: str) -> str:
        """移除Markdown公式块：$$...$$"""
        
        # 移除块级公式 $$...$$ 但保留内容
        text = re.sub(r'\$\$(.*?)\$\$', r'\1', text, flags=re.DOTALL)
        # 移除行级公式 $...$ 但保留内容  
        text = re.sub(r'\$([^$]+)\$', r'\1', text)
        return text

    @staticmethod
    def _clean_latex_formulas(text: str) -> str:
        """清洗LaTeX公式"""
        
        # \frac{a}{b} -> a/b
        text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', text)
        
        # \sqrt{x} -> √(x)
        text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)
        text = re.sub(r'\\sqrt\[([^]]+)\]\{([^}]+)\}', r'^\1√(\2)', text)  # n次方根
        
        # x^{n} -> x^n
        text = re.sub(r'\^\{([^}]+)\}', r'^\1', text)
        
        # _{n} -> _n
        text = re.sub(r'_\{([^}]+)\}', r'_\1', text)
        
        # \left( ... \right) -> ( ... )
        text = re.sub(r'\\left\(', '(', text)
        text = re.sub(r'\\right\)', ')', text)
        text = re.sub(r'\\left\[', '[', text)
        text = re.sub(r'\\right\]', ']', text)
        text = re.sub(r'\\left\{', '{', text)
        text = re.sub(r'\\right\}', '}', text)
        
        return text

    @staticmethod
    def _replace_latex_symbols(text: str) -> str:
        """替换LaTeX符号为Unicode"""
        
        for latex, unicode_char in OutputCleaner.LATEX_SYMBOL_MAP.items():
            text = text.replace(latex, unicode_char)
        
        return text

    @staticmethod
    def _normalize_spaces(text: str) -> str:
        """标准化空格"""
        
        # 移除多余的空格
        text = re.sub(r'\s+', ' ', text)
        
        # 等号前后加空格
        text = re.sub(r'([^\s=])=([^\s=])', r'\1 = \2', text)
        
        # 移除中文符号周围的多余空格
        text = re.sub(r'\s+([，。：；？！])', r'\1', text)
        text = re.sub(r'([，。：；？！])\s+', r'\1', text)
        
        return text.strip()

    @staticmethod
    def validate_response(response: Dict[str, Any]) -> Tuple[bool, str]:
        """验证响应格式"""
        
        # 检查必需字段
        required_fields = ["question_id", "reasoning_process", "answer"]
        for field in required_fields:
            if field not in response:
                return False, f"缺少必需字段: {field}"
        
        # 检查字段类型
        for field in required_fields:
            if not isinstance(response[field], str):
                return False, f"字段 {field} 应为字符串类型"
        
        # 检查字段不为空
        if not response["question_id"].strip():
            return False, "question_id 不能为空"
        if not response["answer"].strip():
            return False, "answer 不能为空"
        
        # 检查长度限制
        if len(response["reasoning_process"]) > 5000:
            return False, "reasoning_process 超过长度限制(5000)"
        if len(response["answer"]) > 1000:
            return False, "answer 超过长度限制(1000)"
        
        # 检查非法标记
        illegal_patterns = [
            (r'```', "代码块标记"),
            (r'\$\$', "Markdown公式块"),
            (r'<script', "脚本标签"),
        ]
        
        for pattern, name in illegal_patterns:
            if re.search(pattern, response["answer"]):
                return False, f"答案中包含非法标记: {name}"
        
        return True, "格式验证通过"

    @staticmethod
    def clean_answer_only(answer: str) -> str:
        """只清洗答案部分（提取第一行核心内容）"""
        
        # 清洗文本
        cleaned = OutputCleaner.clean_text(answer)
        
        # 提取第一行作为最终答案（如果有多行）
        first_line = cleaned.split('\n')[0].strip()
        
        return first_line if first_line else cleaned

    @staticmethod
    def detailed_clean(text: str) -> CleaningReport:
        """详细清洗报告"""
        
        original = text
        cleaned = OutputCleaner.clean_text(text)
        changes = []
        
        # 记录所有变化
        if '```' in original:
            changes.append("移除了代码块标记")
        if '$$' in original:
            changes.append("移除了Markdown公式块")
        if '\\\\' in original or '\\$' in original:
            changes.append("清洗了LaTeX公式")
        if original != cleaned:
            changes.append("标准化了空格和符号")
        
        return CleaningReport(
            original=original,
            cleaned=cleaned,
            changes=changes,
            is_valid=OutputCleaner.validate_response({
                "question_id": "test",
                "reasoning_process": cleaned,
                "answer": cleaned,
            })[0],
        )
