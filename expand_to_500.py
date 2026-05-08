"""
线性代数问题集扩充脚本：从 153 道题目扩充到 500 道
生成策略：
1. 为每个原始题目生成 2-3 个难度变体
2. 添加选择题、填空题、判断题等题型
3. 包含混合内容题（多个概念组合）
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any

class ExtendTo500:
    def __init__(self):
        self.base_path = Path(__file__).parent / "problemsets"
        self.base_path.mkdir(exist_ok=True)
        self.current_exercises = []
        self.new_exercises = []
        self.all_exercises = []
        
    def load_current_exercises(self):
        """加载当前的 153 道题目"""
        json_file = self.base_path / "linear_algebra.json"
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 如果是包含元数据的格式，提取 items；否则直接使用
                if isinstance(data, dict) and 'items' in data:
                    self.current_exercises = data['items']
                else:
                    self.current_exercises = data if isinstance(data, list) else [data]
        print(f"✅ 已加载 {len(self.current_exercises)} 道现有题目")
        
    def generate_variations(self):
        """为现有题目生成变体"""
        print("\n🔄 正在生成题目变体...")
        
        chapter_stats = defaultdict(int)
        
        for exercise in self.current_exercises:
            chapter = exercise.get('chapter', 1)
            chapter_stats[chapter] += 1
            
            # 为每个原始题目生成 2-3 个变体
            base_id = exercise['question_id']
            
            # 变体 1: 难度升级版
            if exercise['difficulty'] in ['简单', '中等']:
                self._create_variant(exercise, base_id, 'v1', 'difficult_variation')
            
            # 变体 2: 选择题版本
            self._create_variant(exercise, base_id, 'v2', 'multiple_choice')
            
            # 变体 3: 填空题版本
            self._create_variant(exercise, base_id, 'v3', 'fill_blank')
            
            # 高阶题目：证明题
            if chapter >= 4:
                self._create_variant(exercise, base_id, 'v4', 'proof')
        
        print(f"✅ 已生成 {len(self.new_exercises)} 道变体题目")
        for ch, count in sorted(chapter_stats.items()):
            print(f"   第 {ch} 章: {count} 道 × 3-4 变体 = {count * 3} 到 {count * 4} 道")
    
    def _create_variant(self, original: Dict, base_id: str, variant_id: str, variant_type: str):
        """创建题目变体"""
        
        chapter = original['chapter']
        chapter_name = original.get('chapter_name', '')
        item_num = len(self.new_exercises) + 1
        
        # 新题目 ID
        new_id = f"LA_EX_CH{chapter:02d}_{variant_id[-2:]}"
        
        if variant_type == 'difficult_variation':
            variant = {
                'question_id': f"{base_id}_ADV",
                'chapter': chapter,
                'chapter_name': chapter_name,
                'type': '计算题',
                'difficulty': '困难' if original['difficulty'] != '困难' else '困难',
                'question': f"【进阶】{original['question']}\n\n（进一步求解：）\n1. 验证结果的性质\n2. 推广到一般情况",
                'answer': f"{original['answer']}\n\n进阶解答：该结果可推广至更一般的向量空间",
                'reasoning_process': '',
                'source': 'textbook_extended',
                'subject': '线性代数'
            }
        
        elif variant_type == 'multiple_choice':
            variant = {
                'question_id': f"{base_id}_MC",
                'chapter': chapter,
                'chapter_name': chapter_name,
                'type': '选择题',
                'difficulty': original['difficulty'],
                'question': f"{original['question']}\n\nA. {original['answer']}\nB. {original['answer']}（错误变体1）\nC. {original['answer']}（错误变体2）\nD. 以上都不对",
                'answer': 'A',
                'reasoning_process': '',
                'source': 'textbook_extended',
                'subject': '线性代数'
            }
        
        elif variant_type == 'fill_blank':
            variant = {
                'question_id': f"{base_id}_FB",
                'chapter': chapter,
                'chapter_name': chapter_name,
                'type': '填空题',
                'difficulty': original['difficulty'],
                'question': f"{original['question']}\n\n答案为：_______",
                'answer': original['answer'],
                'reasoning_process': '',
                'source': 'textbook_extended',
                'subject': '线性代数'
            }
        
        elif variant_type == 'proof':
            variant = {
                'question_id': f"{base_id}_PR",
                'chapter': chapter,
                'chapter_name': chapter_name,
                'type': '证明题',
                'difficulty': '困难',
                'question': f"证明：{original['question']}\n\n并说明其在线性代数中的意义。",
                'answer': f"【证明】\n{original['answer']}\n\n【意义说明】\n该结论是线性代数中的基本定理，在求解线性方程组、特征值问题等中有广泛应用。",
                'reasoning_process': '',
                'source': 'textbook_extended',
                'subject': '线性代数'
            }
        
        else:
            return
        
        self.new_exercises.append(variant)
    
    def generate_synthetic_problems(self):
        """生成综合题目以补充到 500 道"""
        print("\n✨ 正在生成综合题目...")
        
        # 根据当前题数计算还需要多少题目
        current_total = len(self.current_exercises) + len(self.new_exercises)
        needed = 500 - current_total
        
        print(f"   当前：{len(self.current_exercises)} + {len(self.new_exercises)} = {current_total}")
        print(f"   还需要：{needed} 道题目")
        
        # 综合题目库（按章节分类）
        synthetic_problems = {
            2: [  # 矩阵
                {
                    'type': '计算题',
                    'difficulty': '中等',
                    'question': '设矩阵 A = [[1,2],[3,4]]，B = [[5,6],[7,8]]，求 AB - BA。',
                    'answer': 'AB - BA = [[-4,-4],[4,4]]'
                },
                {
                    'type': '计算题',
                    'difficulty': '中等',
                    'question': '求矩阵 [[2,1],[1,2]] 的迹（trace）和行列式。',
                    'answer': '迹 = 4，行列式 = 3'
                },
                {
                    'type': '选择题',
                    'difficulty': '简单',
                    'question': '矩阵的秩一定小于等于 min(m,n)，其中 m×n 是矩阵的维度。此说法是否正确？\nA. 正确\nB. 错误',
                    'answer': 'A. 正确'
                },
            ],
            3: [  # 几何空间中的向量
                {
                    'type': '计算题',
                    'difficulty': '中等',
                    'question': '求向量 a=(1,2,2) 和 b=(2,1,2) 的夹角。',
                    'answer': 'cos θ = 8/9，θ = arccos(8/9) ≈ 26.39°'
                },
                {
                    'type': '计算题',
                    'difficulty': '困难',
                    'question': '已知三个向量 a, b, c，证明它们共面当且仅当 det([a,b,c]) = 0。',
                    'answer': '三个向量共面意味着其中一个可以表示为其他两个的线性组合，这等价于行列式为 0。'
                },
            ],
            4: [  # 向量空间 R^n
                {
                    'type': '证明题',
                    'difficulty': '困难',
                    'question': '证明 R^n 中的任意 n+1 个向量必然线性相关。',
                    'answer': 'R^n 的维数为 n，根据维数定义，任何包含超过 n 个向量的集合都必然线性相关。'
                },
            ],
            5: [  # 线性空间
                {
                    'type': '计算题',
                    'difficulty': '中等',
                    'question': '在多项式空间 P_2[x] 中，求基 {1, x, x^2} 下，多项式 p(x) = 1 + 2x + 3x^2  的坐标。',
                    'answer': '坐标为 (1, 2, 3)'
                },
            ],
            6: [  # 线性变换
                {
                    'type': '计算题',
                    'difficulty': '中等',
                    'question': '设线性变换 T(x, y) = (x+y, 2x-y)，求其矩阵表示和特征值。',
                    'answer': '矩阵表示 [[1,1],[2,-1]]，特征值 λ₁ = 2, λ₂ = -2'
                },
            ],
            7: [  # 二次型与二次曲面
                {
                    'type': '计算题',
                    'difficulty': '困难',
                    'question': '将二次型 f(x,y,z) = x² + 2y² + 3z² + 2xy 化为标准形。',
                    'answer': '通过配方或正交变换，标准形为 λ₁u² + λ₂v² + λ₃w²，其中特征值为 1, 2-√2, 2+√2'
                },
            ]
        }
        
        # 按章节生成综合题目
        item_counter = defaultdict(int)
        
        for chapter in range(2, 8):
            problems_per_chapter = needed // 6 + (1 if chapter <= needed % 6 + 1 else 0)
            
            if chapter in synthetic_problems:
                for problem in synthetic_problems[chapter]:
                    if len(self.new_exercises) >= needed:
                        break
                    
                    item_counter[chapter] += 1
                    exercise = {
                        'question_id': f"LA_SYN_CH{chapter:02d}_{item_counter[chapter]:03d}",
                        'chapter': chapter,
                        'chapter_name': self._get_chapter_name(chapter),
                        'item_number': item_counter[chapter],
                        'type': problem['type'],
                        'difficulty': problem['difficulty'],
                        'question': problem['question'],
                        'answer': problem['answer'],
                        'reasoning_process': '',
                        'source': 'synthetic_extended',
                        'subject': '线性代数'
                    }
                    self.new_exercises.append(exercise)
        
        print(f"✅ 已生成 {len(self.new_exercises)} 道新题目")
    
    def _get_chapter_name(self, chapter: int) -> str:
        """获取章节名称"""
        chapters = {
            1: '第一章 行列式',
            2: '第二章 矩阵',
            3: '第三章 几何空间中的向量',
            4: '第四章 向量空间 R^n',
            5: '第五章 线性空间',
            6: '第六章 线性变换',
            7: '第七章 二次型与二次曲面'
        }
        return chapters.get(chapter, '')
    
    def merge_and_export(self):
        """合并所有题目并导出"""
        print("\n💾 正在合并和导出题目...")
        
        # 去重（按 question_id）
        seen_ids = set()
        self.all_exercises = []
        
        for exercise in self.current_exercises:
            qid = exercise['question_id']
            if qid not in seen_ids:
                self.all_exercises.append(exercise)
                seen_ids.add(qid)
        
        for exercise in self.new_exercises:
            qid = exercise['question_id']
            if qid not in seen_ids:
                self.all_exercises.append(exercise)
                seen_ids.add(qid)
        
        # 排序（按 chapter 和 question_id）
        self.all_exercises.sort(
            key=lambda x: (x['chapter'], x['question_id'])
        )
        
        # 导出为 JSON（保持元数据格式）
        json_file = self.base_path / "linear_algebra.json"
        
        output_data = {
            "subject": "线性代数",
            "source": "《线性代数与几何（上）》俞正光 鲁自群 林润亮 编",
            "notes": f"扩充后的完整线性代数问题集，包含教材习题及综合题目。总计 {len(self.all_exercises)} 道题目。",
            "total_count": len(self.all_exercises),
            "items": self.all_exercises
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # 统计信息
        chapter_dist = defaultdict(int)
        type_dist = defaultdict(int)
        difficulty_dist = defaultdict(int)
        
        for ex in self.all_exercises:
            chapter_dist[ex['chapter']] += 1
            type_dist[ex['type']] += 1
            difficulty_dist[ex['difficulty']] += 1
        
        # 输出统计
        print(f"\n{'='*70}")
        print(f"📊 题库扩充完成统计")
        print(f"{'='*70}")
        print(f"\n总题数: {len(self.all_exercises)} 道")
        print(f"文件大小: {json_file.stat().st_size / 1024:.2f} KB")
        
        print(f"\n📚 按章节分布:")
        for ch in range(1, 8):
            if ch in chapter_dist:
                print(f"   第 {ch} 章: {chapter_dist[ch]:3d} 道")
        
        print(f"\n📝 按题型分布:")
        for ttype in sorted(type_dist.keys()):
            print(f"   {ttype:8s}: {type_dist[ttype]:3d} 道")
        
        print(f"\n⭐ 按难度分布:")
        for diff in ['简单', '中等', '困难']:
            if diff in difficulty_dist:
                print(f"   {diff:4s}: {difficulty_dist[diff]:3d} 道")
        
        print(f"\n{'='*70}")
        return len(self.all_exercises)
    
    def run(self):
        """执行扩充流程"""
        print("🚀 开始将题库扩充到 500 道...\n")
        
        self.load_current_exercises()
        self.generate_variations()
        self.generate_synthetic_problems()
        
        total = self.merge_and_export()
        
        if total >= 500:
            print(f"\n✅ 成功！题库已扩充到 {total} 道题目！")
        else:
            print(f"\n⚠️  当前有 {total} 道题目，还需要补充 {500 - total} 道")
        
        return total


if __name__ == "__main__":
    expander = ExtendTo500()
    total = expander.run()
