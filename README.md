# 未央城智能体大赛 · 基础赛道（工科方向）

这是我们当前的赛道一协作仓库。目标不是做通用聊天，而是做一个能稳定输出比赛格式答案的工科解题智能体。

输出格式固定为：

```json
{
  "question_id": "...",
  "reasoning_process": "...",
  "answer": "..."
}
```

当前版本已经具备：

- Kimi K2.5 接口调用
- 含图题图片传入
- 本地规则兜底
- 样题检索与 few-shot 提示
- 可继续扩展的题库结构

当前默认配置里，`thinking` 已关闭，以减少超时风险。

---

## 1. 文件结构

```text
.
├── baseline_agent.py           # 核心智能体实现，评测时调用的就是它
├── debug.py                    # 本地调试入口，手动塞题测试
├── prob.txt                    # 旧的混合样题池，当前仍会被 agent 读取
├── problemsets/                # 新的正式题库目录，后续优先往这里加题
│   ├── physics.json            # 基础物理学题库
│   ├── circuits.json           # 电路原理题库
│   ├── linear_algebra.json     # 线性代数题库
│   └── calculus.json           # 微积分题库
├── submission.json             # 提交配置
├── requirements.txt            # 依赖声明
├── README.md                   # 当前文档
├── baseline.ipynb              # baseline 参考说明
└── 赛题文档.pdf                 # 官方赛题文档
```

---

## 2. 每个文件的作用

### `baseline_agent.py`

这是主文件，比赛最终最重要的就是它。

当前结构包括：

1. `solve()`
   统一处理输入，组织解题流程，返回标准输出。
2. 题目解析
   识别题型、课程、难度、是否含图。
3. 样题加载
   从 `problemsets/*.json` 和 `prob.txt` 中读取样题。
4. few-shot 检索
   对新题检索相似样题，并把少量高相关示例拼到 prompt。
5. Kimi API 调用
   调用 Moonshot OpenAI 兼容接口。
6. 本地规则兜底
   API 不可用时，处理基础表达式、基础物理、电路题。

### `debug.py`

本地调试脚本。改 `item` 后直接运行，就能看到：

- 是否调用了远程模型
- 输出字段是否正确
- 当前题的推导和答案

### `prob.txt`

这是旧的混合题库，当前 agent 仍会读取它做 few-shot 检索。

但从现在开始，不建议继续只往这里堆题。它更适合：

- 历史样题池
- 临时整理池
- 人工筛题前的混合存放区

### `problemsets/physics.json`

基础物理学题库。后续和速度、加速度、牛顿定律、电磁学等相关的题优先加到这里。

### `problemsets/circuits.json`

电路原理题库。后续串并联、等效电阻、欧姆定律、KCL、KVL 等相关题优先加到这里。

### `problemsets/linear_algebra.json`

线性代数题库。后续矩阵、行列式、方程组、特征值、特征向量等相关题优先加到这里。

### `problemsets/calculus.json`

微积分题库。后续函数、反函数、定义域、极限、导数、积分、相关证明题优先加到这里。

### `submission.json`

评测配置文件。评测系统会按这个文件实例化类并调用方法。

### `requirements.txt`

依赖声明。当前只用标准库。如果以后加 `sympy`、`faiss-cpu` 等，必须同步写进去。

---

## 3. 当前 agent 是怎么工作的

主流程如下：

1. 输入一道题
2. 识别课程和题型
3. 从题库中检索 0 到 3 道相似题
4. 把这些样题作为 few-shot 示例拼进 prompt
5. 如果检测到 `MOONSHOT_API_KEY` 或 `KIMI_API_KEY`，调用 Kimi K2.5
6. 如果调用失败，退回本地规则
7. 输出 `question_id / reasoning_process / answer`

也就是说，当前 `problemsets/*.json` 和 `prob.txt` 都已经接入 agent 了。

---

## 4. 如何运行

### 环境要求

- Python 3.12 推荐
- 安装依赖：`pip install -r requirements.txt`

### 本地调试

```bash
python3 debug.py
```

如果没有设置 API Key，会走本地兜底。

### 使用 Kimi API

```bash
export MOONSHOT_API_KEY='你的key'
python3 debug.py
```

也可以：

```bash
export KIMI_API_KEY='你的key'
python3 debug.py
```

### 安全说明

- 不要把 API Key 写进代码
- 不要把 API Key 提交到 GitHub
- 如果 key 已经在公开场景暴露，建议立即轮换

### 当前默认推理配置

当前在 [baseline_agent.py](/Users/oliver/Library/Mobile%20Documents/com~apple~CloudDocs/大二下/baseline/baseline_agent.py) 中的默认配置是：

- `thinking_enabled = False`
- `request_timeout_seconds = 45`
- `few_shot_example_count = 3`

其中：

- 关闭 `thinking` 是为了减少接口超时风险
- few-shot 默认取 3 道相似题
- 如果题目较复杂、网络较慢，可以适当调大超时

如果想在本地临时覆盖这些配置，可以这样写：

```python
from baseline_agent import BaselineAgent, BaselineConfig

agent = BaselineAgent(
    BaselineConfig(
        thinking_enabled=False,
        request_timeout_seconds=120,
        few_shot_example_count=1,
    )
)
```

---

## 5. 如何测试一道题

直接修改 `debug.py` 里的 `item`：

```python
from baseline_agent import BaselineAgent

agent = BaselineAgent()

item = {
    "question_id": "test-002",
    "type": "计算题",
    "difficulty": "中等",
    "question": "已知函数 f(x)=\\frac{x-1}{x+2}，求函数的反函数 f^{-1}(x)。",
}

print(agent.solve(item))
```

然后运行：

```bash
export MOONSHOT_API_KEY='你的key'
python3 debug.py
```

如果输出里有：

```text
求解方式: 外部大模型。
```

说明这次走了 Kimi。

如果输出里有：

```text
当前未开启外部大模型，使用本地兜底策略。
```

说明这次没走到远程模型。

---

## 5.1 如何测试所有题目

要一次性测试题库中所有题目的表现，使用 `test_all.py` 脚本：

```bash
python3 test_all.py
```

该脚本会：

- 加载 `problemsets/*.json` 中的所有题目
- 对每道题运行 `agent.solve()`
- 输出每个题目的结果，包括推理过程和答案
- 尝试与预期答案比较，统计匹配率

适合用于回归测试和评估本地规则的覆盖率。

---

## 6. 题库格式规范

`problemsets/*.json` 使用下面的结构：

```json
{
  "subject": "微积分",
  "items": [
    {
      "question_id": "CAL_001",
      "type": "计算题",
      "difficulty": "基础",
      "question": "已知函数 f(x)=\\frac{x-1}{x+2}，求反函数。",
      "reasoning_process": "先设 y=f(x)，再解出 x 关于 y 的表达式，最后交换 x 与 y。",
      "answer": "f^{-1}(x)=..."
    }
  ]
}
```

每条题目至少包含：

- `question_id`
- `type`
- `difficulty`
- `question`
- `reasoning_process`
- `answer`

推荐额外保持：

- 解题风格统一
- 公式书写一致
- 答案表达尽量简洁

---

## 7. `prob.txt` 的筛题标准

这套标准同样适用于 `problemsets/*.json`。只是 `prob.txt` 现在更像混合池，`problemsets/*.json` 是正式维护入口。

### 该留的题

优先保留这几类：

1. 高频题型题
   例如反函数、定义域、函数图像、电路基础计算、基础物理运动学、矩阵基础题、导数积分基础题。
2. 代表一种标准套路的题
   例如“先设 y 再解 x”的反函数套路，“根号/分母/对数”的定义域套路，“构造函数/归纳法”的证明套路。
3. 推导过程完整的题
   `reasoning_process` 要清楚、分步、不跳步。
4. 风格统一的题
   让模型学到一致的输出风格，而不是一会儿很详细、一会儿很敷衍。
5. 容易混淆的题
   比如 `f(f(f(x)))` 和 `f^3(x)`、反函数和复合函数、串联和并联、定义域和值域混淆等。

### 该删的题

建议删除：

1. 错题
   题目、推导或答案有明显错误的，不能留下来污染样题库。
2. 重复题
   只换数字、解法完全一样的题，不要堆太多。
3. 低质量题
   推导过程缺步骤、跳步严重、描述模糊的题。
4. 风格不一致题
   例如有的样题写得像讲义，有的像聊天回复，会干扰模型风格学习。
5. 超偏题或超怪题
   非主流、比赛中很难出现、不能代表常规题型的题。

### 还应该补的题

当前建议优先补：

1. 基础物理学
   速度、加速度、受力分析、动能功、简单电磁学。
2. 电路原理
   串并联、等效电阻、总电流、分压分流、KCL、KVL。
3. 线性代数
   行列式、矩阵运算、线性方程组、秩、特征值与特征向量。
4. 微积分
   反函数、定义域、值域、极限、导数、积分、常见证明题。
5. 比赛风格题
   尤其是步骤分明显、推导要求强的题。

### 每道样题的最低质量要求

建议至少满足下面 6 条：

1. 题目来源清楚，题干完整
2. 标注了 `type`
3. 标注了 `difficulty`
4. `reasoning_process` 至少有 3 步以上有效推导
5. `answer` 和推导一致
6. 没有明显格式问题或乱码

---

## 8. 从现在开始怎么维护题库

推荐流程：

1. 新找到的题，先临时放进 `prob.txt` 或本地草稿
2. 做人工筛选
3. 判断属于哪个学科
4. 清洗格式
5. 再写入对应的 `problemsets/*.json`

建议以后优先往对应学科文件里加题，不要让 `prob.txt` 无限膨胀。

换句话说：

- `prob.txt`：历史混合池 / 临时整理池
- `problemsets/*.json`：正式题库

---

## 9. 推荐开发方向

当前最值得做的优化顺序：

1. 把高质量题逐步迁移到 `problemsets/*.json`
2. 提高相似题检索质量
3. 增强本地规则
4. 加输出格式清洗
5. 增加回归测试题集

### 方向 A：继续优化 few-shot 检索

当前是轻量关键词检索，后面可以升级为：

- 更细的学科分类
- 更好的关键词打分
- embedding 检索
- 按题型模板做路由

### 方向 B：增强本地规则

当前本地规则还比较弱，建议优先补：

- 反函数题
- 定义域题
- 基础矩阵题
- 基础导数积分题

### 方向 C：清洗模型输出

当前模型可能输出：

- `$...$`
- `$$...$$`
- Markdown 公式块
- 多余换行

建议加一层后处理，把提交结果清洗成更稳定的纯文本。

---

## 10. 推荐协作方式

### 分工建议

- 一人负责 `baseline_agent.py` 主流程和 prompt
- 一人负责 `problemsets/` 题库整理
- 一人负责本地规则增强
- 一人负责测试和回归验证

### Git 建议

- `main` 只放稳定版本
- 新功能单开分支
- 每个分支只做一类改动
- 合并前先跑本地测试

推荐分支名：

- `feature/problemset-retrieval`
- `feature/inverse-function-rules`
- `feature/output-cleanup`
- `feature/circuit-samples`

---

## 11. 提交前检查

- `baseline_agent.py` 可以直接被实例化
- `solve()` 输入输出字段没改
- `question_id` 原样返回
- 没有提交 API Key
- `submission.json` 正确
- `requirements.txt` 和实际依赖一致
- 样题文件是合法 JSON
- 至少本地跑过若干题

---

## 12. 当前版本总结

当前版本不是最终最优解，但已经具备完整骨架：

- 远程模型调用
- 本地兜底
- 题库加载
- few-shot 检索
- 多学科题库目录

后续开发重点不是推翻重写，而是在这套结构上持续补题、增强检索、补本地规则、清洗输出。
