---
insight_id: {{ insight_id }}
insight_type: academic
title: {{ title }}
source_url: {{ source_url }}
source_doi: {{ source_doi }}
source_version: {{ source_version }}
accessed_at: {{ accessed_at }}
run_id: {{ run_id }}
generated_by: ProtoGenius
template_version: v2-§2.4.A
---

# 学术调研洞察报告 — {{ title }}

{{ coverage_block }}

## § 文献基本信息

| 字段 | 值 |
|------|----|
| 标题 | {{ body.title }} |
| 作者 | {{ body.authors }} |
| 实验室 / 机构 | {{ body.institutions }} |
| 发表时间 | {{ body.published_at }} |
| 核心关键词 | {{ body.keywords }} |

## § 研究动机

| 字段 | 值 |
|------|----|
| 本质瓶颈 | {{ body.bottleneck }} |
| 本文新方案 / 新视角 | {{ body.new_perspective }} |

## § 算法机制与方法论解构

| 字段 | 值 |
|------|----|
| 核心创新点 | {{ body.innovation }} |
| 核心数学 / 逻辑公式 | {{ body.formula }} |
| 技术架构 / 算法 Pipeline | {{ body.pipeline }} |

{% if body.pipeline_mermaid %}
```mermaid
{{ body.pipeline_mermaid }}
```
{% endif %}

## § 实验结论与消融实验

| 字段 | 值 |
|------|----|
| 基准测试 (Benchmark) | {{ body.benchmarks }} |
| 关键量化指标 | {{ body.metrics }} |
| 消融实验启示 | {{ body.ablation }} |

## § 实际项目落地价值评估

| 字段 | 值 |
|------|----|
| 工程可行性 | {{ body.engineering_feasibility }} |
| 可借鉴部分 | {{ body.transferable }} |
| 局限性与防御边界 | {{ body.limitations }} |

## § 核心结论

{{ body.core_conclusions }}

## § 引用与可审计来源

- URL: <{{ source_url }}>
{% if source_doi %}- DOI: `{{ source_doi }}`
{% endif %}{% if source_version %}- 版本: `{{ source_version }}`
{% endif %}- 访问日期: {{ accessed_at }}
{% if kb_ref %}- 知识库引用: `{{ kb_ref }}`
{% endif %}
