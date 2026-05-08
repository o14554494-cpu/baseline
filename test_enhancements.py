"""本地测试脚本 - 测试方向B和方向C

用法：
    python test_enhancements.py

这个脚本在本地验证增强规则和输出清洗的功能，
确保在合并到main之前功能完全正常。
"""

import json
from enhanced_local_rules import EnhancedLocalRules, RuleResult
from output_cleaner import OutputCleaner


class TestEnhancements:
    """测试套件"""

    def __init__(self):
        self.rules = EnhancedLocalRules()
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 80)
        print("🧪 本地增强功能测试")
        print("=" * 80)

        self.test_inverse_functions()
        self.test_domain_solving()
        self.test_derivatives()
        self.test_integrals()
        self.test_matrix_rank()
        self.test_output_cleaning()
        self.test_output_validation()

        self.print_summary()

    # ==================== 方向B：本地规则测试 ====================

    def test_inverse_functions(self):
        """测试反函数求解"""
        print("\n📍 测试 - 反函数求解")
        print("-" * 80)

        test_cases = [
            {
                "question": "已知 f(x) = 2x + 3，求反函数 f^{-1}(x)",
                "check": lambda r: r and "(x - 3)/2" in r.answer or "x/2" in r.answer,
                "name": "一次函数反函数",
            },
            {
                "question": "求函数 f(x) = (2x - 1)/(x + 3) 的反函数 f^{-1}(x)",
                "check": lambda r: r and "反函数" in r.source,
                "name": "分式函数反函数",
            },
        ]

        for test in test_cases:
            result = self.rules.solve_inverse_function(test["question"])
            passed = test["check"](result)
            self._record_test(test["name"], passed, result, test["question"])

    def test_domain_solving(self):
        """测试定义域求解"""
        print("\n📍 测试 - 定义域求解")
        print("-" * 80)

        test_cases = [
            {
                "question": "求函数 f(x) = 1/(x - 2) 的定义域",
                "check": lambda r: r and "x" in r.answer and "2" in r.answer,
                "name": "分母约束定义域",
            },
            {
                "question": "求函数 f(x) = √(2x - 4) 的定义域",
                "check": lambda r: r and "定义域" in r.answer,
                "name": "根号约束定义域",
            },
        ]

        for test in test_cases:
            result = self.rules.solve_domain(test["question"])
            passed = test["check"](result)
            self._record_test(test["name"], passed, result, test["question"])

    def test_derivatives(self):
        """测试导数求解"""
        print("\n📍 测试 - 导数求解")
        print("-" * 80)

        test_cases = [
            {
                "question": "求函数 f(x) = x^2 的导数",
                "check": lambda r: r and ("2x" in r.answer or "2x^1" in r.answer),
                "name": "幂函数导数",
            },
            {
                "question": "求函数 f(x) = x^3 的导数",
                "check": lambda r: r and ("3x" in r.answer or "3x^2" in r.answer),
                "name": "三次幂导数",
            },
            {
                "question": "求 f(x) = sin(x) 的导数",
                "check": lambda r: r and "cos" in r.answer,
                "name": "三角函数导数",
            },
            {
                "question": "求 f(x) = e^x 的导数",
                "check": lambda r: r and "e^x" in r.answer,
                "name": "指数函数导数",
            },
        ]

        for test in test_cases:
            result = self.rules.solve_basic_derivative(test["question"])
            passed = test["check"](result)
            self._record_test(test["name"], passed, result, test["question"])

    def test_integrals(self):
        """测试积分求解"""
        print("\n📍 测试 - 积分求解")
        print("-" * 80)

        test_cases = [
            {
                "question": "求 ∫x^2 dx",
                "check": lambda r: r and ("x^3/3" in r.answer or "x^3" in r.answer),
                "name": "幂函数积分",
            },
            {
                "question": "求 ∫sin(x) dx",
                "check": lambda r: r and "cos" in r.answer,
                "name": "三角函数积分",
            },
        ]

        for test in test_cases:
            result = self.rules.solve_basic_integral(test["question"])
            passed = test["check"](result)
            self._record_test(test["name"], passed, result, test["question"])

    def test_matrix_rank(self):
        """测试矩阵秩判断"""
        print("\n📍 测试 - 矩阵秩判断")
        print("-" * 80)

        test_cases = [
            {
                "question": "设A是3阶矩阵，det(A)≠0，求秩",
                "check": lambda r: r and "3" in r.answer,
                "name": "秩计算",
            },
            {
                "question": "零矩阵的秩是多少",
                "check": lambda r: r and "0" in r.answer,
                "name": "零矩阵秩",
            },
        ]

        for test in test_cases:
            result = self.rules.solve_matrix_rank(test["question"])
            passed = test["check"](result)
            self._record_test(test["name"], passed, result, test["question"])

    # ==================== 方向C：输出清洗测试 ====================

    def test_output_cleaning(self):
        """测试输出清洗功能"""
        print("\n📍 测试 - 输出清洗")
        print("-" * 80)

        test_cases = [
            {
                "input": "答案是 ```json\n{\"result\": 42}\n```",
                "check": lambda r: "```" not in r and "json" not in r,
                "name": "移除代码块",
            },
            {
                "input": "最终答案：$$f'(x) = 2x$$",
                "check": lambda r: "$$" not in r and "f'(x) = 2x" in r,
                "name": "移除公式块",
            },
            {
                "input": "计算 \\frac{1}{2} \\times \\sqrt{3}",
                "check": lambda r: "\\\\" not in r and ("1/2" in r or "1） / （2" in r),
                "name": "清洗LaTeX公式",
            },
            {
                "input": "使用符号 \\times \\leq \\neq",
                "check": lambda r: "×" in r and "≤" in r and "≠" in r,
                "name": "替换LaTeX符号",
            },
            {
                "input": "结果  =   42   （多余空格）",
                "check": lambda r: "  " not in r and "结果 = 42" in r,
                "name": "标准化空格",
            },
        ]

        for test in test_cases:
            result = OutputCleaner.clean_text(test["input"])
            passed = test["check"](result)
            self._record_test(test["name"], passed, result, test["input"])

    def test_output_validation(self):
        """测试输出验证"""
        print("\n📍 测试 - 输出验证")
        print("-" * 80)

        test_cases = [
            {
                "response": {
                    "question_id": "test_001",
                    "reasoning_process": "分析过程",
                    "answer": "答案",
                },
                "check": lambda r: r[0] is True,
                "name": "有效格式验证",
            },
            {
                "response": {
                    "question_id": "test_001",
                    "reasoning_process": "分析过程",
                    # 缺少 answer
                },
                "check": lambda r: r[0] is False,
                "name": "缺少必需字段检测",
            },
            {
                "response": {
                    "question_id": "test_001",
                    "reasoning_process": "分析过程",
                    "answer": "答案中有```非法标记",
                },
                "check": lambda r: r[0] is False,
                "name": "非法标记检测",
            },
        ]

        for test in test_cases:
            result = OutputCleaner.validate_response(test["response"])
            passed = test["check"](result)
            self._record_test(test["name"], passed, result, json.dumps(test["response"], ensure_ascii=False))

    # ==================== 辅助方法 ====================

    def _record_test(self, test_name: str, passed: bool, result: any, input_text: str):
        """记录测试结果"""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status} | {test_name}")
        
        if not passed:
            print(f"       输入：{input_text[:50]}...")
            print(f"       结果：{str(result)[:100]}...")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "result": str(result)[:200],
        })

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 80)
        print("📊 测试总结")
        print("=" * 80)
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n总体成绩：{self.passed}/{total} ({pass_rate:.1f}%)")
        print(f"  ✓ 通过：{self.passed}")
        print(f"  ✗ 失败：{self.failed}")
        
        if self.failed == 0:
            print("\n🎉 所有测试通过！可以合并到main分支。")
        else:
            print(f"\n⚠️  还有{self.failed}个测试失败，请修复后再提交。")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    tester = TestEnhancements()
    tester.run_all_tests()
