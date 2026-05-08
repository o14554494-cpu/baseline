"""方向B：增强本地规则库

包含反函数、定义域、导数、积分、矩阵等高频题型的本地规则实现。
设计目标：在API不可用时，提供完整的本地求解能力。
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class RuleResult:
    """规则求解结果"""
    answer: str
    reasoning_steps: List[str]
    source: str
    success: bool = True


class EnhancedLocalRules:
    """增强本地规则库"""

    def solve(self, question: str) -> Optional[RuleResult]:
        """通用求解接口，按优先级尝试各规则"""
        
        solvers = [
            self.solve_inverse_function,
            self.solve_domain,
            self.solve_basic_derivative,
            self.solve_basic_integral,
            self.solve_matrix_rank,
        ]

        for solver in solvers:
            result = solver(question)
            if result and result.success:
                return result

        return None

    # ==================== 反函数求解 ====================

    def solve_inverse_function(self, question: str) -> Optional[RuleResult]:
        """求反函数"""
        
        if "反函数" not in question and "f^{-1}" not in question:
            return None

        # 模式1：一次函数 f(x) = ax + b
        match = re.search(r"f\(x\)\s*=\s*([+-]?\d+(?:\.\d+)?)\s*x\s*([+-])\s*(\d+(?:\.\d+)?)", question)
        if match:
            a = float(match.group(1))
            sign = match.group(2)
            b = float(match.group(3))
            if sign == "-":
                b = -b

            if a == 0:
                return None

            result = self._inverse_linear(a, b)
            return result

        # 模式2：分式函数 f(x) = (ax+b)/(cx+d)
        match = re.search(
            r"f\(x\)\s*=\s*\\?frac\{([^}]+)\}\{([^}]+)\}",
            question,
        )
        if match:
            numerator = match.group(1).strip()
            denominator = match.group(2).strip()
            result = self._inverse_fraction(numerator, denominator)
            return result

        return None

    def _inverse_linear(self, a: float, b: float) -> RuleResult:
        """一次函数反函数：f(x) = ax + b → f^{-1}(x) = (x - b)/a"""
        
        # 化简系数
        b_inv = -b / a
        a_inv = 1 / a

        # 格式化答案
        if a == 1 and b == 0:
            answer = "f^{-1}(x) = x"
        elif a == 1:
            answer = f"f^{{-1}}(x) = x - {b}" if b > 0 else f"f^{{-1}}(x) = x + {-b}"
        elif b == 0:
            answer = f"f^{{-1}}(x) = x/{a}"
        else:
            b_str = f" - {b}" if b > 0 else f" + {-b}"
            answer = f"f^{{-1}}(x) = (x{b_str})/{a}"

        reasoning_steps = [
            f"设 y = {a}x + {b}（即 f(x)）",
            f"解出 x：{a}x = y - {b}",
            f"x = (y - {b})/{a} = y/{a} - {b/a}",
            f"交换 x 与 y：f^{{-1}}(x) = x/{a} - {b/a}",
            f"化简：{answer}",
        ]

        return RuleResult(
            answer=answer,
            reasoning_steps=reasoning_steps,
            source="反函数求解（一次函数）",
        )

    def _inverse_fraction(self, numerator: str, denominator: str) -> RuleResult:
        """分式函数反函数步骤提示"""
        
        reasoning_steps = [
            f"设 y = ({numerator})/({denominator})",
            f"两边同乘 ({denominator})：y({denominator}) = {numerator}",
            "展开并整理成 cx + d 形式的线性方程",
            "解出 x = f(y)",
            "交换 x 与 y 得到反函数",
        ]

        answer = f"f^{{-1}}(x) = [需要手工计算分式反函数]\n提示：将 f(x)={numerator}/{denominator} 按上述步骤操作"

        return RuleResult(
            answer=answer,
            reasoning_steps=reasoning_steps,
            source="反函数求解（分式函数）",
        )

    # ==================== 定义域求解 ====================

    def solve_domain(self, question: str) -> Optional[RuleResult]:
        """求定义域"""
        
        if "定义域" not in question:
            return None

        constraints = []
        reasoning_steps = ["识别到定义域问题，找出所有约束条件："]

        # 分母约束：1/(...)
        denom_match = re.findall(r"1\s*[/÷]\s*\(([^)]+)\)", question)
        for expr in denom_match:
            constraints.append((f"分母 {expr} ≠ 0", expr))
            reasoning_steps.append(f"分母不为零：{expr} ≠ 0")

        # 根号约束：√(...)
        sqrt_match = re.findall(r"√\(([^)]+)\)", question)
        for expr in sqrt_match:
            constraints.append((f"根号内 {expr} ≥ 0", expr))
            reasoning_steps.append(f"根号内非负：{expr} ≥ 0")

        # 对数约束：ln(...)
        ln_match = re.findall(r"ln\(([^)]+)\)", question)
        for expr in ln_match:
            constraints.append((f"对数参数 {expr} > 0", expr))
            reasoning_steps.append(f"对数参数为正：{expr} > 0")

        if not constraints:
            return None

        # 生成答案
        answer = "定义域：" + "，".join([c[0] for c in constraints])
        reasoning_steps.append(f"\n综合所有约束得到定义域")

        return RuleResult(
            answer=answer,
            reasoning_steps=reasoning_steps,
            source="定义域求解",
        )

    # ==================== 基础导数 ====================

    def solve_basic_derivative(self, question: str) -> Optional[RuleResult]:
        """基础导数求解"""
        
        if "导数" not in question and "求导" not in question and "f'" not in question:
            return None

        # 幂函数：(x^n)' = n*x^(n-1)
        match = re.search(r"x\s*\^\s*([0-9]+)", question)
        if match:
            n = int(match.group(1))
            coef = n
            power = n - 1
            if power == 0:
                answer = f"f'(x) = {coef}"
            elif power == 1:
                answer = f"f'(x) = {coef}x"
            else:
                answer = f"f'(x) = {coef}x^{power}"
            
            reasoning_steps = [
                f"识别到幂函数 x^{n}",
                f"使用幂函数求导公式：(x^n)' = n*x^(n-1)",
                f"代入 n={n}：f'(x) = {coef}x^{power}" if power > 0 else f"代入 n={n}：f'(x) = {coef}",
            ]
            
            return RuleResult(
                answer=answer,
                reasoning_steps=reasoning_steps,
                source="基础导数（幂函数）",
            )

        # sin(x) 的导数
        if "sin" in question:
            reasoning_steps = [
                "识别到三角函数 sin(x)",
                "使用三角函数求导公式：(sin x)' = cos x",
                "答案：f'(x) = cos(x)",
            ]
            return RuleResult(
                answer="f'(x) = cos(x)",
                reasoning_steps=reasoning_steps,
                source="基础导数（三角函数）",
            )

        # cos(x) 的导数
        if "cos" in question:
            reasoning_steps = [
                "识别到三角函数 cos(x)",
                "使用三角函数求导公式：(cos x)' = -sin x",
                "答案：f'(x) = -sin(x)",
            ]
            return RuleResult(
                answer="f'(x) = -sin(x)",
                reasoning_steps=reasoning_steps,
                source="基础导数（三角函数）",
            )

        # e^x 的导数
        if "e^x" in question or "exp" in question:
            reasoning_steps = [
                "识别到指数函数 e^x",
                "使用指数函数求导公式：(e^x)' = e^x",
                "答案：f'(x) = e^x",
            ]
            return RuleResult(
                answer="f'(x) = e^x",
                reasoning_steps=reasoning_steps,
                source="基础导数（指数函数）",
            )

        return None

    # ==================== 基础积分 ====================

    def solve_basic_integral(self, question: str) -> Optional[RuleResult]:
        """基础积分求解"""
        
        if "积分" not in question and "∫" not in question:
            return None

        # 幂函数积分：∫x^n dx = x^(n+1)/(n+1) + C
        match = re.search(r"x\s*\^\s*([0-9]+)", question)
        if match:
            n = int(match.group(1))
            power = n + 1
            answer = f"∫x^{n}dx = x^{power}/{power} + C"
            reasoning_steps = [
                f"识别到幂函数 x^{n}",
                f"使用幂函数积分公式：∫x^n dx = x^(n+1)/(n+1) + C",
                f"代入 n={n}：∫x^{n}dx = x^{power}/{power} + C",
            ]
            return RuleResult(
                answer=answer,
                reasoning_steps=reasoning_steps,
                source="基础积分（幂函数）",
            )

        # sin(x) 的积分
        if "sin" in question:
            reasoning_steps = [
                "识别到三角函数 sin(x)",
                "使用三角函数积分公式：∫sin(x)dx = -cos(x) + C",
                "答案：∫sin(x)dx = -cos(x) + C",
            ]
            return RuleResult(
                answer="∫sin(x)dx = -cos(x) + C",
                reasoning_steps=reasoning_steps,
                source="基础积分（三角函数）",
            )

        # cos(x) 的积分
        if "cos" in question:
            reasoning_steps = [
                "识别到三角函数 cos(x)",
                "使用三角函数积分公式：∫cos(x)dx = sin(x) + C",
                "答案：∫cos(x)dx = sin(x) + C",
            ]
            return RuleResult(
                answer="∫cos(x)dx = sin(x) + C",
                reasoning_steps=reasoning_steps,
                source="基础积分（三角函数）",
            )

        return None

    # ==================== 基础线性代数 ====================

    def solve_matrix_rank(self, question: str) -> Optional[RuleResult]:
        """矩阵秩判断"""
        
        if "秩" not in question and "rank" not in question.lower():
            return None

        # 模式：n阶矩阵，det(A)≠0，求秩
        n_match = re.search(r"([0-9])[阶].*矩阵", question)
        det_match = re.search(r"det\(A\)\s*[≠!=]\s*0", question)

        if n_match and det_match:
            n = int(n_match.group(1))
            reasoning_steps = [
                f"识别到{n}阶矩阵A",
                f"已知det(A) ≠ 0，说明行列式非零",
                f"由矩阵秩的定义：行列式非零 ⟹ 秩为最大",
                f"因此rank(A) = {n}",
            ]
            return RuleResult(
                answer=f"秩 rank(A) = {n}",
                reasoning_steps=reasoning_steps,
                source="矩阵秩判断",
            )

        # 模式：特定矩阵的秩
        if "零矩阵" in question:
            reasoning_steps = [
                "识别到零矩阵",
                "零矩阵的秩定义为 0",
                "因此 rank(O) = 0",
            ]
            return RuleResult(
                answer="秩 rank(O) = 0",
                reasoning_steps=reasoning_steps,
                source="矩阵秩判断（零矩阵）",
            )

        return None
