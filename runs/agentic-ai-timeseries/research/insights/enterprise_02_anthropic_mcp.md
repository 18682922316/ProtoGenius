# Insight Report — Enterprise #2: Anthropic MCP for TS Connectivity

> **coverage_note**: Covers MCP as the connectivity standard + Claude financial agents with forecasting. Low uncertainty for MCP (open spec); medium for financial agents (product-level, limited public benchmarks).

## Identification

| Field | Value |
|-------|-------|
| insight_id | `enterprise-02-anthropic-mcp` |
| insight_type | enterprise |
| title | Anthropic — Model Context Protocol (MCP) + Financial Forecasting Agents |
| company | Anthropic |
| source_type | Product docs + Official blog |
| date | Nov 2024 – May 2026 |
| uncertainty | low (MCP) / medium (financial agents) |

## Core Conclusions

1. **MCP is becoming the de facto standard** for agent-to-data-source connectivity. Adopted by OpenAI (Mar 2025), Google (ADK integration), and growing ecosystem.
2. **TS-relevant MCP servers already exist**: TimescaleDB, GreptimeDB, IoTDB, Prometheus — all time-series-native databases with MCP interfaces.
3. **Claude Financial Services Agents**: 10 ready-to-run agent templates including 13-week cash flow forecasting, revenue modeling, scenario planning.
4. **Managed Agents**: Anthropic's deployment platform for production agent workloads with observability.
5. **Key insight**: MCP provides the "plumbing" that makes agentic TS systems possible — without standardized data access, agents cannot reach time-series data.

## Adoption Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Technical maturity | ★★★★☆ | Open spec, growing ecosystem, but still evolving |
| Integration effort | ★★★★★ | Simple server/client pattern; many existing servers |
| Cost | ★★★★★ | Open protocol; no licensing |
| Vendor lock-in risk | ★★★★★ | Open standard, multi-vendor |
| Community | ★★★★☆ | Rapidly growing; 100+ MCP servers catalogued |

## Relevance to Platform

- **Connectivity layer**: MCP should be the standard for connecting internal agents to TS databases.
- **Server catalog**: Existing TimescaleDB/Prometheus MCP servers reduce development effort.
- **Financial templates**: Claude's financial agents demonstrate enterprise-grade TS forecasting patterns.

## Auditable Citation

```
MCP Specification: https://modelcontextprotocol.io/
Financial Agents: https://www.anthropic.com/news/finance-agents
Accessed: 2026-05-27
```
