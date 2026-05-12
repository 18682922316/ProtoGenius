---
name: industry-research
description: Vendor-blog and docs survey for the seven targeted companies.
inputs: SearchQuery
outputs: list[ResearchItem]
code: protogenius.research.industry.IndustryAdapter
---

# industry-research skill

Scope is frozen: Anthropic, OpenAI, DeepMind, ByteDance, Alibaba, Tencent,
Meituan. Items carry `extra.uncertainty = "Inferred from public web; may be
incomplete or stale."` because there is no official API to authoritatively
list capabilities.
