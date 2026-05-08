"""输出清洗模块 - 方向C完成

功能：
- 移除Markdown标记
- 清洗LaTeX公式（转为纯文本）
- 标准化数学符号
- 移除多余换行
- 统一答案格式
"""

import re
from typing import Dict, Any


class OutputCleaner:
    """模型输出清洗器"""

    @staticmethod
    def clean_reasoning_process(text: str) -> str:
        """清洗推理过程"""
        
        if not text:
            return ""
        
        # 1. 移除代码块标记
        text = re.sub(r'```[a-z]*\n?', '', text)
        text = re.sub(r'```', '', text)
        
        # 2. 清洗Markdown数学公式
        # $...$ 内联公式 -> 保留内容
        text = re.sub(r'\$\$([^$]+)\$\$', r'\1', text)  # $$...$$ -> ...
        text = re.sub(r'\$([^$]+)\$', r'\1', text)      # $...$ -> ...
        
        # 3. 清洗LaTeX括号
        text = re.sub(r'\\left\(', '(', text)
        text = re.sub(r'\\right\)', ')', text)
        text = re.sub(r'\\left\[', '[', text)
        text = re.sub(r'\\right\]', ']', text)
        text = re.sub(r'\\left\{', '{', text)
        text = re.sub(r'\\right\}', '}', text)
        
        # 4. 清洗分数符号
        # \frac{a}{b} -> a/b
        text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', text)
        
        # 5. 清洗根号
        # \sqrt{x} -> √x
        text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)
        text = re.sub(r'\\sqrt', '√', text)
        
        # 6. 清洗指数
        # x^{2} -> x^2
        text = re.sub(r'\^\{([^}]+)\}', r'^\1', text)
        
        # 7. 清洗上标下标
        # x_{n} -> x_n
        text = re.sub(r'_\{([^}]+)\}', r'_\1', text)
        
        # 8. 清洗希腊字母（常见的转为中文或英文）
        greek_replacements = {
            r'\\alpha': 'α',
            r'\\beta': 'β',
            r'\\gamma': 'γ',
            r'\\delta': 'δ',
            r'\\lambda': 'λ',
            r'\\mu': 'μ',
            r'\\sigma': 'σ',
            r'\\pi': 'π',
            r'\\theta': 'θ',
            r'\\phi': 'φ',
        }
        for latex, char in greek_replacements.items():
            text = re.sub(latex, char, text)
        
        # 9. 清洗特殊符号
        text = re.sub(r'\\times', '×', text)
        text = re.sub(r'\\div', '÷', text)
        text = re.sub(r'\\pm', '±', text)
        text = re.sub(r'\\approx', '≈', text)
        text = re.sub(r'\\neq|\\ne', '≠', text)
        text = re.sub(r'\\leq|\\le', '≤', text)
        text = re.sub(r'\\geq|\\ge', '≥', text)
        text = re.sub(r'\\infty', '∞', text)
        text = re.sub(r'\\in', '∈', text)
        text = re.sub(r'\\notin', '∉', text)
        text = re.sub(r'\\cup', '∪', text)
        text = re.sub(r'\\cap', '∩', text)
        
        # 10. 清洗特殊函数符号
        text = re.sub(r'\\sin', 'sin', text)
        text = re.sub(r'\\cos', 'cos', text)
        text = re.sub(r'\\tan', 'tan', text)
        text = re.sub(r'\\ln', 'ln', text)
        text = re.sub(r'\\log', 'log', text)
        
        # 11. 移除多余空格
        text = re.sub(r' +', ' ', text)  # 多个空格 -> 单个空格
        
        # 12. 移除多余换行
        text = re.sub(r'\n{3,}', '\n\n', text)  # 3个以上换行 -> 2个换行
        
        # 13. 清理首尾空格
        text = text.strip()
        
        return text

    @staticmethod
    def clean_answer(text: str) -> str:
        """清洗答案字段"""
        
        if not text:
            return ""
        
        # 1. 应用通用清洗
        text = OutputCleaner.clean_reasoning_process(text)
        
        # 2. 去除多余的解释性文字（只保留答案本身）
        # 移除「答案是」「所以」等前缀
        text = re.sub(r'^(答案[为是]|因此|所以|故|即|结果[为是])[：:]*\s*', '', text)
        
        # 3. 如果有多行，只取第一行（答案通常是第一行）
        lines = text.split('\n')
        text = lines[0].strip() if lines else ""
        
        # 4. 移除尾部的句号、冒号等
        text = re.sub(r'[。，；：、]*$', '', text)
        
        # 5. 如果答案包含「=」，确保格式规范
        if '=' in text and not re.match(r'^[a-zA-Z_].*=', text):
            # 如果不是以变量开头，添加空格分隔
            text = re.sub(r'([^\s=])=([^\s=])', r'\1 = \2', text)
        
        return text

    @staticmethod
    def clean_response(response: Dict[str, str]) -> Dict[str, str]:
        """清洗完整的模型响应"""
        
        cleaned = {}
        
        # question_id 保持原样
        if "question_id" in response:
            cleaned["question_id"] = response["question_id"]
        
        # 清洗推理过程
        if "reasoning_process" in response:
            cleaned["reasoning_process"] = OutputCleaner.clean_reasoning_process(
                response["reasoning_process"]
            )
        
        # 清洗答案
        if "answer" in response:
            cleaned["answer"] = OutputCleaner.clean_answer(response["answer"])
        
        return cleaned

    @staticmethod
    def validate_response(response: Dict[str, str]) -> tuple[bool, str]:
        """验证响应格式是否合规
        
        Returns:
            (是否合规, 错误信息或成功信息)
        """
        
        # 检查必需字段
        required_fields = ["question_id", "reasoning_process", "answer"]
        for field in required_fields:
            if field not in response:
                return False, f"缺少必需字段：{field}"
            if not isinstance(response[field], str):
                return False, f"字段 {field} 应为字符串"
        
        # 检查字段非空
        if not response["question_id"].strip():
            return False, "question_id 不能为空"
        if not response["reasoning_process"].strip():
            return False, "reasoning_process 不能为空"
        if not response["answer"].strip():
            return False, "answer 不能为空"
        
        # 检查字符长度
        if len(response["reasoning_process"]) > 5000:
            return False, "reasoning_process 过长（>5000字符）"
        if len(response["answer"]) > 500:
            return False, "answer 过长（>500字符）"
        
        # 检查是否包含非法Markdown
        if "```" in response["answer"]:
            return False, "answer 中不应包含代码块标记"
        
        return True, "格式验证通过"


# 使用示例
if __name__ == "__main__":
    test_response = {
        "question_id": "test_001",
        "reasoning_process": """
        使用幂函数求导公式：$(x^n)' = nx^{n-1}$
        
        已知 $f(x) = x^2$，则：
        $$f'(x) = 2x^{2-1} = 2x$$
        """,
        "answer": "答案是：$f'(x) = 2x$。"
    }
    
    print("原始响应：")
    print(test_response)
    print("\n" + "="*80 + "\n")
    
    cleaned = OutputCleaner.clean_response(test_response)
    print("清洗后的响应：")
    print(cleaned)
    print("\n" + "="*80 + "\n")
    
    valid, msg = OutputCleaner.validate_response(cleaned)
    print(f"格式验证：{msg}")
