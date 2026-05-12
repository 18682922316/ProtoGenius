---
name: pre-search-quota-guard
event: pre_search
code: protogenius.hooks.quota_guard.quota_guard_hook
---

# pre-search quota guard

Charges the search-results quota **before** the network call. Also rechecks
the walltime cap (6h hard) so very long-running adapters can't quietly
exceed it.
