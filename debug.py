from baseline_agent import BaselineAgent

agent = BaselineAgent()

item = {
    "question_id": "test-002",
    "type": "计算题",
    "difficulty": "中等",
    "question": "已知函数 f(x)=\\frac{x-1}{x+2}，求函数的反函数 f^{-1}(x)。",
}

expected = {
    "reasoning_process": "要求反函数，先设 y=\\frac{x-1}{x+2}。为了把 x 用 y 表示，先两边同时乘以 x+2，得到 y(x+2)=x-1。展开得 yx+2y=x-1。把含 x 的项移到一边，得 yx-x=-1-2y。提取公因式，得 x(y-1)=-(1+2y)。因此 x=\\frac{-(1+2y)}{y-1}=\\frac{1+2y}{1-y}。再将 y 改写为 x，就得到反函数表达式。由于原式中分母不能为 0，且反函数分母 1-x 也不能为 0，因此反函数定义时需满足 x\\ne1。",
    "answer": "f^{-1}(x)=\\frac{1+2x}{1-x}\\,(x\\ne1)"
}

result = agent.solve(item)

print("=== Agent Output ===")
print(result)
print("\n=== Expected Answer ===")
print(expected)
