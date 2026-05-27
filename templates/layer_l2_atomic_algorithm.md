---
name: {{ name }}
description: {{ description }}
layer: atomic_algorithm
version: {{ version }}
version_type: {{ version_type }}
related_versions: {{ related_versions }}
template_version: v2-§4.4.3
run_id: {{ run_id }}
generated_by: ProtoGenius
---

# {{ name }} (Atomic Algorithm)

{{ coverage_block }}

## 1. 算法基础信息

| 字段 | 值 |
|------|----|
| 算法名称 | {{ body.algorithm_name }} |
| 英文标识 | {{ body.algorithm_en }} |
| 算法类别 | {{ body.algorithm_category }} |
| 依赖基础理论 | {{ body.depends_on_theories }} |
| 适配场景 | {{ body.applicable_scenarios }} |
| 禁用场景 | {{ body.forbidden_scenarios }} |

## 2. 算法核心要素

- **输入规范**：{{ body.input_spec }}
- **输出格式**：{{ body.output_format }}
- **核心计算逻辑**：{{ body.core_logic }}
- **执行步骤**：{{ body.steps }}
- **超参数释义**：{{ body.hyperparameters }}
- **收敛判定规则**：{{ body.convergence }}
- **复杂度**：{{ body.complexity }}

## 3. 性能指标

| 字段 | 值 |
|------|----|
| 精度指标 | {{ body.accuracy }} |
| 效率指标 | {{ body.efficiency }} |
| 资源消耗 | {{ body.resource_usage }} |
| 最优 / 常规表现 | {{ body.best_vs_typical }} |

## 4. 算法挑战与优化方向

- **技术瓶颈**：{{ body.bottlenecks }}
- **改进思路**：{{ body.improvements }}

## 5. 原型系统 & 代码库

| 字段 | 值 |
|------|----|
| 代码仓库地址 | {{ body.repo_url }} |
| 运行环境 | {{ body.runtime_env }} |
| 依赖包清单 | {{ body.dependencies }} |
| 主执行脚本 | {{ body.entry_script }} |
| 测试用例 | {{ body.tests }} |
| 启动命令 | {{ body.launch_cmd }} |
| 接口调用方式 | {{ body.api_usage }} |
| 部署方式 | {{ body.deployment }} |

## 6. 版本管理

| 字段 | 值 |
|------|----|
| 版本号 | {{ version }} |
| 版本类型 | {{ version_type }} |
| 关联历史版本号 | {{ related_versions }} |
| 版本更改点 | {{ change_summary }} |

## 7. 引用文档列表

{{ references_md }}

## 形式化定义

> v2 §4.4.5 — 必须包含本层的形式化要素。

- **输入输出空间**：{{ body.formal_io_space }}
- **目标函数 / 判定规则**：{{ body.formal_objective }}
- **时间复杂度**：{{ body.formal_time_complexity }}
- **空间复杂度**：{{ body.formal_space_complexity }}
- **正确性条件**：{{ body.formal_correctness }}

{% if kb_refs %}
## 知识库引用 (`kb_ref`)

{% for ref in kb_refs %}- `{{ ref }}`
{% endfor %}
{% endif %}
{% if conflicts %}
## ⚠ 与知识库冲突

{% for conflict in conflicts %}- {{ conflict }}
{% endfor %}
{% endif %}
