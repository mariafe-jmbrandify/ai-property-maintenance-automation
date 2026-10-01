# ADR-004: n8n as the orchestrator, with an event router

**Status:** Accepted (supersedes the Make.com-first design in v1.0)

## Context

Version 1.0 specified 14 Make.com scenarios that handed off to each other by polling status changes in Google Sheets. That works, but:

- the end-to-end process is spread across 14+ scenario canvases, so nobody can see the whole system at once;
- every hand-off waits for a "Watch Rows" poll;
- the AI parts (intake extraction, tenant conversation, reply classification, coordinator, SOP assistant) are agent-shaped, and Make's AI support was module-by-module;
- the rules engine (pricing, NTE, timers) is code that the orchestrator should be able to call or embed easily.

## Decision

Use **n8n** as the orchestrator:

1. **One main workflow** (`Maintenance Ops · Work Order Lifecycle`) implements Scenarios 1–10 on a single canvas: an intake branch (Gmail Trigger) plus an **event router** (one Webhook `POST /events/:event` → Switch) that sends each event to its branch.
2. **Google Sheets holds the state.** Each branch loads the work order, acts, writes the new status and exits. No execution waits days for a person.
3. **Short waits only** use Wait nodes (*On Webhook Call*), e.g. a technician accepting a dispatch within 15 minutes or a reviewer approving a card.
4. **Long timers** (PM approval, tenant replies, payments) live in a separate Exception Monitor workflow that reads timestamps every 10 minutes.
5. **AI work uses n8n's AI nodes**: AI Agent with chat model, memory and Structured Output Parser sub-nodes; Text Classifier for PM replies; vector-store tools for the SOP assistant.
6. **Rules stay in code** and are called with HTTP Request nodes (`/decide`, `/extraction`) or mirrored in Code nodes.
7. Always-on jobs (KPIs, exceptions, coordinator, SOP assistant) are separate workflows so they can be paused, re-run and permissioned independently.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Make.com scenarios (v1.0) | Process fragmented across many canvases; polling hand-offs; less natural for agents with tools. |
| One long n8n execution per work order with Wait nodes for every human step | Easy to draw, hard to operate: executions paused for days, painful to debug or re-run after a fix, and lost if a waiting execution is deleted. |
| Custom code service | Most flexible, but the office team loses the visual workflow they can read and adjust. |

## Consequences

- The whole system fits on one screen ([docs/images/n8n-system-canvas.png](../images/n8n-system-canvas.png)).
- External systems need a public n8n webhook URL (n8n Cloud, or self-hosted behind HTTPS).
- Self-hosting is possible for data control and cost; n8n Cloud avoids running infrastructure.
- Scenario specs keep their numbers; each now lists its n8n nodes and which branch it lives in.
