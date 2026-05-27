---
insight_id: {{ insight_id }}
insight_type: enterprise
title: {{ title }}
vendor: {{ body.vendor }}
source_url: {{ source_url }}
accessed_at: {{ accessed_at }}
run_id: {{ run_id }}
generated_by: ProtoGenius
template_version: v2-§2.4.C
uncertainty: {{ body.uncertainty }}
---

# 头部企业洞察报告 — {{ title }}

> **不确定性提示**：{{ body.uncertainty }}

{{ coverage_block }}

## § 基本信息

| 字段 | 值 |
|------|----|
| 企业 / 组织 | {{ body.vendor }} |
| 技术 / 项目名称 | {{ body.tech_name }} |
| 技术分类 | {{ body.tech_category }} |

## § 商业痛点与技术演进

| 字段 | 值 |
|------|----|
| 业务倒逼技术 | {{ body.business_driven }} |
| 技术路线迭代 | {{ body.evolution }} |

## § 项目技术分析

| 字段 | 值 |
|------|----|
| 技术架构 | {{ body.architecture }} |
| 核心算法 | {{ body.core_algorithms }} |

## § 借鉴价值评估

| 字段 | 值 |
|------|----|
| 直接复用 | {{ body.direct_reuse }} |
| 可借鉴部分 | {{ body.transferable }} |

## § 核心结论

{{ body.core_conclusions }}

## § 引用与可审计来源

- 来源 URL: <{{ source_url }}>
- 来源类型: {{ body.source_label }}（{{ body.uncertainty }}）
- 访问日期: {{ accessed_at }}
{% if kb_ref %}- 知识库引用: `{{ kb_ref }}`
{% endif %}
