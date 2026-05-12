---
name: mermaid-diagram
description: Build small Mermaid flowcharts (architecture / algorithm).
inputs:
  - components
  - edges
outputs: Mermaid flowchart string
code: protogenius.utils.mermaid.flowchart
---

# mermaid-diagram skill

No rendering — produces text only. Output is embedded in SRS / TDD / research
reports; rendering is delegated to whatever consumes the Markdown.
