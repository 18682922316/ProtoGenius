---
name: {{ name }}
description: {{ description }}
layer: ai_application
version: {{ version }}
version_type: {{ version_type }}
related_versions: {{ related_versions }}
template_version: v2-§4.4.1
run_id: {{ run_id }}
generated_by: ProtoGenius
---

# {{ name }} (AI Application)

{{ coverage_block }}

## 1. 应用基础信息

| 字段 | 值 |
|------|----|
| 应用名称 | {{ body.app_name }} |
| 产品定位 | {{ body.positioning }} |
| 目标用户 | {{ body.target_users }} |
| 核心业务痛点 | {{ body.pain_points }} |
| 业务价值 | {{ body.business_value }} |

## 2. 整体业务架构

- **核心功能清单**：{{ body.core_features }}
- **业务流程**：{{ body.business_flow }}
- **用户操作流程**：{{ body.user_flow }}
- **场景使用范式**：{{ body.usage_patterns }}

## 3. 完整技术架构

{{ body.architecture_overview_md }}

### 3.1 前端架构

| 字段 | 值 |
|------|----|
| 技术栈 | {{ body.frontend_stack }} |
| 页面架构 | {{ body.frontend_pages }} |
| 交互逻辑 | {{ body.frontend_interaction }} |
| 部署方式 | {{ body.frontend_deploy }} |

### 3.2 中台架构

| 字段 | 值 |
|------|----|
| 调度中心 | {{ body.midplatform_scheduler }} |
| 能力编排 | {{ body.midplatform_orchestration }} |
| 权限架构 | {{ body.midplatform_authz }} |
| 流程编排 | {{ body.midplatform_workflow }} |

### 3.3 后端架构

| 字段 | 值 |
|------|----|
| 开发语言 | {{ body.backend_language }} |
| 服务架构 | {{ body.backend_services }} |
| 接口协议 | {{ body.backend_interfaces }} |
| 中间件 | {{ body.backend_middleware }} |
| 数据库架构 | {{ body.backend_database }} |

### 3.4 AI 能力架构

| 字段 | 值 |
|------|----|
| 依赖技术专题 | {{ body.ai_depends_topics }} |
| 依赖原子算法 | {{ body.ai_depends_algorithms }} |
| 模型调用链路 | {{ body.ai_model_chain }} |
| 知识库调用逻辑 | {{ body.ai_kb_logic }} |

### 3.5 部署运维架构

| 字段 | 值 |
|------|----|
| 集群架构 | {{ body.deploy_cluster }} |
| 算力分配 | {{ body.deploy_compute }} |
| 扩容方案 | {{ body.deploy_scaling }} |

## 4. 数据体系

| 字段 | 值 |
|------|----|
| 业务数据格式 | {{ body.data_formats }} |
| 数据流转链路 | {{ body.data_flow }} |
| 数据存储规范 | {{ body.data_storage }} |
| 数据安全规则 | {{ body.data_security }} |

## 5. 交互规范

| 字段 | 值 |
|------|----|
| 用户输入规则 | {{ body.input_rules }} |
| 标准输出范式 | {{ body.output_paradigm }} |
| 多轮对话逻辑 | {{ body.multiturn_logic }} |
| 意图匹配规则 | {{ body.intent_matching }} |

## 6. 应用挑战与优化方向

- **面临的问题**：{{ body.challenges }}
- **改进思路**：{{ body.improvements }}

## 7. 应用原型系统 & 代码库

| 字段 | 值 |
|------|----|
| 应用整体源码仓库 | {{ body.repo_url }} |
| 前后端工程目录 | {{ body.project_tree }} |
| 配置文件 | {{ body.config_files }} |
| Docker 部署脚本 | {{ body.docker_deploy }} |
| 演示 Demo | {{ body.demo_link }} |
| 下层知识库对接调用代码 | {{ body.kb_integration_code }} |
| 线上投产部署流程 | {{ body.prod_deploy_flow }} |

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

- **用户目标函数**：{{ body.formal_user_objective }}
- **系统状态机**：{{ body.formal_state_machine }}
- **服务级约束 (SLA / 安全 / 合规)**：{{ body.formal_sla_security }}

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
