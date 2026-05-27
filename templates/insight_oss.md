---
insight_id: {{ insight_id }}
insight_type: oss
title: {{ title }}
source_url: {{ source_url }}
source_version: {{ source_version }}
accessed_at: {{ accessed_at }}
run_id: {{ run_id }}
generated_by: ProtoGenius
template_version: v2-§2.4.B
---

# 开源项目洞察报告 — {{ title }}

{{ coverage_block }}

## § 项目画像

| 字段 | 值 |
|------|----|
| 项目名称与仓库地址 | [{{ body.repo_name }}]({{ source_url }}) |
| Star 趋势与活跃度 | {{ body.star_activity }} |
| 开源协议 (License) | {{ body.license }} |

## § 项目能力

| 字段 | 值 |
|------|----|
| 项目主要能力 | {{ body.capabilities }} |
| 相对同类项目的优势 | {{ body.differentiators }} |

## § 项目技术分析

| 字段 | 值 |
|------|----|
| 技术架构 | {{ body.architecture }} |
| 核心算法 | {{ body.core_algorithms }} |

## § 实际项目落地价值评估

| 字段 | 值 |
|------|----|
| 性能 | {{ body.performance }} |
| 权限与安全 | {{ body.security }} |
| 可借鉴部分 | {{ body.transferable }} |
| 局限性 | {{ body.limitations }} |

## § 核心结论

{{ body.core_conclusions }}

## § 引用与可审计来源

- 仓库 URL: <{{ source_url }}>
{% if source_version %}- 版本 / 默认分支: `{{ source_version }}`
{% endif %}- 访问日期: {{ accessed_at }}
{% if kb_ref %}- 知识库引用: `{{ kb_ref }}`
{% endif %}
