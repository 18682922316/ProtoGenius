# L1 基础理论层 — Foundation Theory
## 时间序列分析与预测的数学基础

> **coverage_note**: 本文档覆盖 Agentic TS 系统所依赖的核心数学理论。省略了纯概率测度论细节（过于基础）和具体实现算法（属于 L2 层）。重点放在 Agent 系统需要"理解"的时序数据本质特征。

---

## 1. 概述

时间序列分析的基础理论为 Agentic AI 系统提供了：
- **数据特征的形式化描述**（平稳性、季节性、趋势）
- **预测问题的数学框架**（条件期望、分位数回归）
- **不确定性量化的理论基础**（置信区间、预测区间）
- **因果推断的时序扩展**（Granger 因果、结构方程模型）

---

## 2. 核心概念

### 2.1 随机过程与时间序列

时间序列 $\{X_t\}_{t \in T}$ 是定义在概率空间 $(\Omega, \mathcal{F}, P)$ 上的随机过程，其中 $T \subseteq \mathbb{Z}$（离散时间）或 $T \subseteq \mathbb{R}$（连续时间）。

### 2.2 平稳性

**严格平稳**: $(X_{t_1}, ..., X_{t_k}) \overset{d}{=} (X_{t_1+h}, ..., X_{t_k+h})$ 对所有 $h, k, t_1, ..., t_k$

**弱平稳（二阶平稳）**:
- $E[X_t] = \mu$ （常数均值）
- $\text{Cov}(X_t, X_{t+h}) = \gamma(h)$ （自协方差仅依赖于滞后 $h$）

### 2.3 自相关结构

**自协方差函数 (ACVF)**: $\gamma(h) = \text{Cov}(X_t, X_{t+h})$

**自相关函数 (ACF)**: $\rho(h) = \gamma(h) / \gamma(0)$

**偏自相关函数 (PACF)**: $\phi_{hh}$ 为 $X_t$ 对 $X_{t-h}$ 的偏相关（控制中间变量）

### 2.4 谱分析

**功率谱密度**: $f(\omega) = \frac{1}{2\pi} \sum_{h=-\infty}^{\infty} \gamma(h) e^{-i\omega h}$

谱分析将时域的自相关结构转换为频域表示，揭示周期性成分。

### 2.5 分解定理

**经典分解**: $X_t = T_t + S_t + R_t$（趋势 + 季节 + 残差）

**STL 分解**: Seasonal-Trend decomposition using LOESS，迭代估计各分量。

---

## 3. 预测理论

### 3.1 最优预测

给定信息集 $\mathcal{F}_t = \sigma(X_s : s \leq t)$，最优 $h$ 步预测为：

$$\hat{X}_{t+h|t} = E[X_{t+h} | \mathcal{F}_t]$$

此为均方误差 (MSE) 意义下的最优预测。

### 3.2 预测区间

**分位数预测**: 预测 $X_{t+h}$ 的 $\alpha$-分位数 $q_\alpha$ 满足 $P(X_{t+h} \leq q_\alpha | \mathcal{F}_t) = \alpha$

**覆盖率保证**: 理想的 $[q_{\alpha/2}, q_{1-\alpha/2}]$ 区间应有 $(1-\alpha)$ 的覆盖率。

### 3.3 多步预测误差累积

对于自回归模型，$h$ 步预测误差方差通常以 $O(h)$ 或更快的速度增长：

$$\text{Var}(\hat{X}_{t+h|t} - X_{t+h}) = \sigma^2 \sum_{j=0}^{h-1} \psi_j^2$$

这是 LangTime (ICML 2025) 用 PPO 缓解的核心问题。

---

## 4. 因果与信息论基础

### 4.1 Granger 因果

$X$ Granger-causes $Y$ 当且仅当：
$$P(Y_{t+1} | Y_t, Y_{t-1}, ...) \neq P(Y_{t+1} | Y_t, Y_{t-1}, ..., X_t, X_{t-1}, ...)$$

Augur (2025) 使用 LLM 提取有向因果关联，本质是 Granger 因果的 LLM 近似。

### 4.2 信息论视角

**转移熵**: $T_{X \to Y} = H(Y_{t+1} | Y_t^{(k)}) - H(Y_{t+1} | Y_t^{(k)}, X_t^{(l)})$

量化 $X$ 对预测 $Y$ 的信息增益——Agent 系统中用于判断是否引入外部信号。

---

## 5. 形式化定义

### 5.1 时间序列预测问题

$$\mathcal{P} = (\mathcal{X}, \mathcal{H}, \mathcal{F}, \mathcal{L})$$

其中：
- $\mathcal{X} = \{x_1, x_2, ..., x_T\} \in \mathbb{R}^{T \times d}$ — 观测序列（$d$ 维，$T$ 个时间步）
- $\mathcal{H} \in \mathbb{Z}^+$ — 预测窗口（horizon）
- $\mathcal{F}: \mathbb{R}^{T \times d} \to \mathbb{R}^{\mathcal{H} \times d}$ — 预测映射
- $\mathcal{L}: \mathbb{R}^{\mathcal{H} \times d} \times \mathbb{R}^{\mathcal{H} \times d} \to \mathbb{R}^+$ — 损失函数

### 5.2 Agentic 预测系统（ATSF 形式化）

$$\mathcal{A} = (\mathcal{S}, \mathcal{O}, \mathcal{P}lan, \mathcal{A}ct, \mathcal{R}ef, \mathcal{M})$$

其中（引自 Cheng et al., 2026 — ATSF Position Paper）：
- $\mathcal{S}$: 状态空间 — 包含当前时间序列数据、元数据、历史交互
- $\mathcal{O}$: 观测函数 — Agent 对时间序列的感知（数值/视觉/文本）
- $\mathcal{P}lan$: 规划函数 — 选择工具/模型/策略
- $\mathcal{A}ct$: 执行函数 — 调用工具、生成预测
- $\mathcal{R}ef$: 反思函数 — 评估输出质量、决定是否重试
- $\mathcal{M}$: 记忆 — 持久化的经验和上下文

### 5.3 多 Agent 协作形式化

$$\mathcal{MAS} = (\{A_i\}_{i=1}^n, \mathcal{C}, \mathcal{T}, \Gamma)$$

其中：
- $\{A_i\}_{i=1}^n$: $n$ 个专业化 Agent（Curator, Planner, Forecaster, Detector, Reporter, Critic）
- $\mathcal{C}: A_i \times A_j \to \text{Message}$ — Agent 间通信协议
- $\mathcal{T}: \text{Task} \to 2^{\{A_i\}}$ — 任务到 Agent 子集的路由映射
- $\Gamma$: 协调策略（串行管道 / 并行扇出 / 反馈环路）

### 5.4 工具增强推理形式化

$$\mathcal{TAR} = (\mathcal{LLM}, \mathcal{R}_{tool}, \pi_{select}, \pi_{chain})$$

其中（引自 TimeART, 2026）：
- $\mathcal{LLM}$: 基础语言模型（推理引擎）
- $\mathcal{R}_{tool} = \{t_1, ..., t_K\}$: 工具注册表（$K \geq 15$ 个分析工具）
- $\pi_{select}: (\text{query}, \mathcal{S}) \to t_i$: 工具选择策略
- $\pi_{chain}: (t_{i_1}, ..., t_{i_m}) \to \text{Result}$: 工具链组合策略

---

## 6. 参考文献

| 引用 | 与本层关系 |
|------|-----------|
| Cheng et al. (2026) ATSF Position Paper | §5.2 ATSF 形式化来源 |
| TimeART (2026) | §5.4 工具增强推理形式化 |
| Box, Jenkins, Reinsel (2015) Time Series Analysis | §2-4 经典理论基础 |
| Hamilton (1994) Time Series Analysis | §4 因果与谱分析 |
| LangTime — Niu et al. (ICML 2025) | §3.3 误差累积问题 |
