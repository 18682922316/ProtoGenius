---
name: {{ name }}
description: {{ description }}
layer: foundation_theory
version: {{ version }}
version_type: {{ version_type }}
related_versions: {{ related_versions }}
template_version: v2-§4.4.4
run_id: {{ run_id }}
generated_by: ProtoGenius
---

# {{ name }} (Foundation Theory)

{{ coverage_block }}

## 1. 基础信息

| 字段 | 值 |
|------|----|
| 理论名称 | {{ body.theory_name }} |
| 所属领域 | {{ body.domain }} |
| 研究背景 | {{ body.background }} |
| 核心出处 | {{ body.canonical_source }} |
| 适用范围 | {{ body.applicability_scope }} |
| 使用约束 | {{ body.constraints }} |

## 2. 核心定义

- **专业术语**：{{ body.terminology }}
- **基础公理**：{{ body.axioms }}
- **核心定理**：{{ body.theorems }}
- **推导公式**：{{ body.derivations }}
- **基础推论**：{{ body.corollaries }}

## 3. 底层原理

- **核心思想**：{{ body.core_idea }}
- **运行机理**：{{ body.mechanism }}
- **内在逻辑**：{{ body.internal_logic }}
- **成立条件**：{{ body.preconditions }}
- **限制条件**：{{ body.limitations }}

## 4. 知识关联

- **前置必备理论**：{{ body.prerequisites }}
- **同级关联理论**：{{ body.peers }}
- **延伸衍生理论**：{{ body.derivatives }}

## 5. 易错要点

{{ body.pitfalls }}

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

- **符号表**：{{ body.formal_symbols }}
- **公理 / 定理**：{{ body.formal_axioms_theorems }}
- **核心推导式**：{{ body.formal_derivation }}
- **适用域 \( \mathcal{D} \)**：{{ body.formal_domain }}

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
