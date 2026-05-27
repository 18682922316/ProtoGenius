# L2 原子算法层 — Atomic Algorithm
## Agentic TS 系统的核心算法组件

> **coverage_note**: 覆盖 Agentic TS 系统中被各框架反复引用的核心算法。省略了纯工程优化（如量化推理）和特定硬件适配（TPU/NPU kernel）。每个算法以"Agent 如何使用它"为视角描述。

---

## 1. 概述

Agentic TS 系统将传统的"模型训练→推理"流程替换为"Agent 选择工具→调用→评估→迭代"的循环。本层描述的"原子算法"是 Agent 工具箱中的基本单元——Agent 不需要理解算法内部实现，但需要知道：
1. 何时选择该算法（适用条件）
2. 输入/输出格式
3. 计算代价
4. 期望精度范围

---

## 2. 统计基础算法

### 2.1 ARIMA (AutoRegressive Integrated Moving Average)

**Agent 使用场景**: 短期预测、平稳/近平稳序列、基线对比

**模型**: $\phi(B)(1-B)^d X_t = \theta(B)\epsilon_t$

其中 $\phi(B) = 1 - \phi_1 B - ... - \phi_p B^p$, $\theta(B) = 1 + \theta_1 B + ... + \theta_q B^q$

**Agent 决策规则**: 
- 序列长度 < 100 → 优先选择 ARIMA
- ACF 截尾 → MA 模型
- PACF 截尾 → AR 模型
- 需要差分 → 增加 $d$

### 2.2 STL 分解 (Seasonal-Trend using LOESS)

**Agent 使用场景**: 预分析（理解数据结构）、特征提取、异常检测前处理

**算法流程**:
1. 初始化趋势为 0
2. 外层循环（鲁棒性权重更新）:
   - 内层循环:
     - 去趋势 → 提取季节分量（LOESS 平滑）
     - 去季节 → 提取趋势分量（LOESS 平滑）
3. 残差 $R_t = X_t - T_t - S_t$

### 2.3 ADF 检验 (Augmented Dickey-Fuller)

**Agent 使用场景**: 判断序列是否需要差分（平稳性检验）

**假设检验**: $H_0$: 序列有单位根（非平稳） vs $H_1$: 序列平稳

**Agent 决策**: p-value < 0.05 → 平稳，直接建模；否则差分后重新检验

---

## 3. 基础模型算法

### 3.1 Patch-based Tokenization (TimesFM/Chronos)

**Agent 使用场景**: 将连续时间序列转化为 Token 序列，供 Transformer 处理

**算法**:
1. 将序列 $\{x_1, ..., x_T\}$ 分割为长度 $P$ 的 patch: $\{p_1, ..., p_{T/P}\}$
2. 每个 patch 通过线性投影映射到 $d$-维嵌入空间
3. 添加位置编码（绝对或旋转）
4. 输入 Transformer decoder

**TimesFM 特有**: 输出层为分位数回归头（同时预测多个分位数）

### 3.2 Mixture-of-Experts for Time Series (Time-MoE)

**Agent 使用场景**: 需要高参数容量但受限于推理计算时

**算法**:
1. 输入 token 经过共享注意力层
2. Router 网络为每个 token 选择 top-k 个 expert（k=2 通常）
3. 仅激活选中的 expert FFN
4. 加权合并 expert 输出

**效率**: 2.4B 总参数，仅 1.1B 激活 → <8GB VRAM

### 3.3 Serial-Token Prediction (Timer-S1)

**Agent 使用场景**: 长 horizon 预测避免误差累积

**传统**: $\hat{x}_{T+1} \to \hat{x}_{T+2} \to ...$ （每步用前一步预测作为输入 → 误差累积）

**Timer-S1**: 每个输出 token 直接预测对应时间步，不依赖前序预测 token。训练目标：
$$\mathcal{L} = \sum_{h=1}^{H} \ell(\hat{x}_{T+h}, x_{T+h})$$

---

## 4. Agent 特有算法

### 4.1 ReAct (Reasoning + Acting)

**Agent 使用场景**: TS-Agent、TimeART 的核心推理循环

**算法**:
```
while not done:
    thought = LLM.reason(observation, history)
    action = LLM.select_tool(thought)
    observation = execute_tool(action)
    history.append((thought, action, observation))
    if LLM.judge_complete(history):
        done = True
```

### 4.2 Multi-Agent Role Decomposition

**Agent 使用场景**: Nexus, TimeSeriesScientist, CastClaw

**算法**（以 Nexus 为例）:
1. **Macro Agent**: 分析长期趋势和周期性变化
2. **Micro Agent**: 分析短期波动和局部模式  
3. **Context Agent**: 整合外部知识和领域约束
4. **Integration**: 加权融合三个 Agent 的输出

**路由决策**:
$$\text{route}(\text{task}) = \arg\max_{A_i} \text{competence}(A_i, \text{task\_features})$$

### 4.3 Tool Selection via Learned Policy (TimeART)

**Agent 使用场景**: 从 21 个工具中选择最优工具或工具链

**训练**: 在 TimeToolBench (100K 轨迹) 上微调 8B LLM
- 输入: (series_features, task_description, available_tools)
- 输出: tool_sequence + parameters

**推理时**: LLM 生成工具调用序列，按序执行，每步检查中间结果

### 4.4 Temporal-Aware Reinforcement Learning (TimerPO)

**Agent 使用场景**: ANOMSEER — 对齐 MLLM 与经典 TSAD 方法

**算法**:
1. MLLM 生成异常检测结果
2. 经典 TSAD 方法作为 reward model
3. 基于最优传输的语义偏差信号计算 reward
4. PPO 更新 MLLM 参数

---

## 5. 形式化定义

### 5.1 时间序列 Foundation Model

$$\mathcal{FM} = (E, D, H_{out}, \theta)$$

其中：
- $E: \mathbb{R}^{T \times d} \to \mathbb{R}^{L \times d_{model}}$ — 编码器（patch tokenization + embedding）
  - Patch 划分: $E_{patch}(x) = \{x_{[iP:(i+1)P]}\}_{i=0}^{L-1}$, $L = \lceil T/P \rceil$
  - 线性投影: $E_{proj}(p_i) = W_E p_i + b_E$, $W_E \in \mathbb{R}^{d_{model} \times P}$
- $D: \mathbb{R}^{L \times d_{model}} \to \mathbb{R}^{L' \times d_{model}}$ — 解码器（Transformer layers）
  - 自注意力: $\text{Attn}(Q, K, V) = \text{softmax}(QK^T / \sqrt{d_k})V$
  - 因果掩码确保自回归性
- $H_{out}: \mathbb{R}^{d_{model}} \to \mathbb{R}^{P \times |\mathcal{Q}|}$ — 输出头（分位数预测）
  - $|\mathcal{Q}|$ 个分位数同时输出（如 0.1, 0.5, 0.9）
- $\theta$: 可学习参数集合（TimesFM: 200M; Timer-S1: 8.3B; Time-MoE: 2.4B）

### 5.2 Mixture-of-Experts 路由

$$\text{MoE}(x) = \sum_{i=1}^{N} g_i(x) \cdot E_i(x)$$

其中：
- $g(x) = \text{TopK}(\text{softmax}(W_g x), k)$ — 门控函数，选择 top-k 个 expert
- $E_i$: 第 $i$ 个 expert 网络（FFN）
- $N$: expert 总数
- $k$: 每 token 激活的 expert 数（Time-MoE: $k=2$, $N$ 使得 1.1B/2.4B 激活比）

### 5.3 ReAct 推理循环

$$\pi_{ReAct}(a_t | s_t) = \text{LLM}(a_t | s_t, \text{thought}_t, \text{history}_{<t})$$

其中：
- $s_t = (x_{obs}, \text{task}, \text{tool\_results}_{<t})$ — 当前状态
- $\text{thought}_t = \text{LLM}_{reason}(s_t)$ — 推理步骤（Chain-of-Thought）
- $a_t \in \mathcal{R}_{tool}$ — 工具调用动作
- 终止条件: $\text{LLM}_{judge}(\text{history}) > \tau_{confidence}$

### 5.4 分位数回归损失

$$\mathcal{L}_{quantile}(\hat{q}_\alpha, y) = \begin{cases} \alpha(y - \hat{q}_\alpha) & \text{if } y \geq \hat{q}_\alpha \\ (1-\alpha)(\hat{q}_\alpha - y) & \text{if } y < \hat{q}_\alpha \end{cases}$$

TSFM 输出层同时优化多个分位数:
$$\mathcal{L}_{total} = \frac{1}{|\mathcal{Q}|} \sum_{\alpha \in \mathcal{Q}} \mathcal{L}_{quantile}(\hat{q}_\alpha, y)$$

---

## 6. 算法选择指南（供 Planner Agent 使用）

| 数据特征 | 推荐算法 | 理由 |
|----------|----------|------|
| 短序列 (< 100 点) | ARIMA / ETS | 样本不足以支撑 TSFM |
| 长序列 + 零样本 | TimesFM / Chronos-2 | 无需训练，直接推理 |
| 长序列 + 低 VRAM | Time-MoE | MoE 效率：< 8GB |
| 超长 horizon | Timer-S1 (Serial-Token) | 避免误差累积 |
| 多变量 + 因果 | Augur (LLM-causal) | LLM 提取因果关系 |
| 异常检测 | STL + 统计检验 + MLLM | 分层：粗筛 → 精检 → 解释 |
| 需要解释 | ReAct + Reporter Agent | 每步推理可追溯 |

---

## 7. 参考文献

| 引用 | 与本层关系 |
|------|-----------|
| TimesFM 2.5 (Google, 2025) | §3.1, §5.1 Patch tokenization + 分位数输出 |
| Time-MoE (Alibaba, ICLR 2025) | §3.2, §5.2 MoE 路由 |
| Timer-S1 (ByteDance, 2026) | §3.3 Serial-Token Prediction |
| TimeART (2026) | §4.3 工具选择策略 |
| ANOMSEER (2026) | §4.4 TimerPO |
| TS-Agent (2025) | §4.1 ReAct 循环 |
| Nexus (Google, 2026) | §4.2 多 Agent 分解 |
