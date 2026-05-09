#!/usr/bin/env python3
"""
测试脚本：一次性测试所有题库中的题目表现。

运行方式：
python test_all.py

输出：
- 每个题目的 question_id
- Agent 的输出 (reasoning_process 和 answer)
- 如果有预期答案，显示匹配情况
"""

import json
import os
from pathlib import Path
from baseline_agent import BaselineAgent

def load_all_problems():
    """从 problemsets/ 目录加载所有题目。"""
    problems = []
    problemsets_dir = Path(__file__).parent / "problemsets"
    if not problemsets_dir.exists():
        print("problemsets/ 目录不存在")
        return problems

    for json_file in problemsets_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            items = data.get("items", [])
            for item in items:
                item['source_file'] = json_file.name
                problems.append(item)
        except Exception as e:
            print(f"加载 {json_file} 失败: {e}")
    return problems

def main():
    agent = BaselineAgent()
    problems = load_all_problems()

    if not problems:
        print("没有找到任何题目")
        return

    print(f"共加载 {len(problems)} 道题目\n")

    correct_count = 0
    total_count = len(problems)

    for i, problem in enumerate(problems, 1):
        print(f"=== 题目 {i}/{total_count} ===")
        print(f"ID: {problem.get('question_id', 'N/A')}")
        print(f"来源: {problem.get('source_file', 'N/A')}")
        print(f"题目: {problem.get('question', 'N/A')}")
        print()

        # 运行 agent
        result = agent.solve(problem)

        print("Agent 输出:")
        print(f"  reasoning_process: {result['reasoning_process']}")
        print(f"  answer: {result['answer']}")
        print()

        # 检查答案匹配
        expected_answer = problem.get('answer', '').strip()
        actual_answer = result['answer'].strip()
        if expected_answer and actual_answer:
            # 简单字符串匹配，忽略大小写和空格
            if expected_answer.lower().replace(' ', '') == actual_answer.lower().replace(' ', ''):
                print("答案匹配: ✓")
                correct_count += 1
            else:
                print("答案不匹配: ✗")
                print(f"  预期: {expected_answer}")
        else:
            print("无法比较答案")

        print("-" * 50)
        print()

    print(f"测试完成: {correct_count}/{total_count} 答案匹配")

if __name__ == "__main__":
    main()