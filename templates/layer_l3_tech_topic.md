---
name: {{ name }}
description: {{ description }}
layer: tech_topic
version: {{ version }}
version_type: {{ version_type }}
related_versions: {{ related_versions }}
template_version: v2-§4.4.2
run_id: {{ run_id }}
generated_by: ProtoGenius
---

# {{ name }} (Tech Topic)

{{ coverage_block }}

## 1. 专题基础信息

| 字段 | 值 |
|------|----|
| 专题名称 | {{ body.topic_name }} |
| 技术定义 | {{ body.tech_definition }} |
| 解决的技术问题 | {{ body.problem_statement }} |
| 技术研发目标 | {{ body.development_goal }} |
| 所属技术领域 | {{ body.tech_domain }} |

## 2. 技术体系脉络

- **技术发展历程**：{{ body.history }}
- **主流技术流派**：{{ body.schools }}
- **技术演进路线**：{{ body.evolution }}

## 3. 全维度实现方案

{{ body.solutions_md }}

## 4. 核心组件构成

| 字段 | 值 |
|------|----|
| 所依赖原子算法 | {{ body.depends_on_algorithms }} |
| 前后处理技术 | {{ body.pre_post_processing }} |
| 特征构建方式 | {{ body.feature_engineering }} |
| 目标设计方式 | {{ body.objective_design }} |

## 5. 技术评测体系

- **通用评测指标**：{{ body.evaluation_metrics }}
- **标准测试数据集**：{{ body.benchmark_datasets }}
- **对比评测方法**：{{ body.comparison_methods }}

## 6. 技术难点与优化方向

- **现存技术瓶颈**：{{ body.bottlenecks }}
- **前沿改进思路**：{{ body.frontier_improvements }}

## 7. 原型系统 & 代码库

| 字段 | 值 |
|------|----|
| 集成代码仓 | {{ body.integration_repo }} |
| 各方案独立工程 | {{ body.per_solution_repos }} |
| 批量测试脚本 | {{ body.batch_test_script }} |
| 环境配置文档 | {{ body.env_setup_doc }} |
| 一键运行指令 | {{ body.one_click_run }} |
| 结果对比工具 | {{ body.result_compare_tool }} |

## 8. 版本管理

| 字段 | 值 |
|------|----|
| 版本号 | {{ version }} |
| 版本类型 | {{ version_type }} |
| 关联历史版本号 | {{ related_versions }} |
| 版本更改点 | {{ change_summary }} |

## 9. 引用文档列表

{{ references_md }}

## 形式化定义

> v2 §4.4.5 — 必须包含本层的形式化要素。

- **问题形式化**：{{ body.formal_problem }}
- **方案族 \( \mathcal{F} \)**：{{ body.formal_solution_family }}
- **选型条件**：{{ body.formal_selection_conditions }}
- **评测指标向量**：{{ body.formal_eval_vector }}

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
