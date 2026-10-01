# Scenario 14 — AI Knowledge Base & SOP Assistant

| | |
|---|---|
| **n8n workflow** | `Maintenance Ops · SOP Assistant` (separate workflow) |
| **Build as** | **Chat Trigger** (or Slack Trigger) → **AI Agent** with a **Vector Store Tool** over the SOP documents (Supabase, Pinecone or the in-memory store for a demo), **OpenAI Chat Model**, **Simple Memory** per user; questions and gaps logged to Google Sheets |
| **Sources** | SOP library, troubleshooting library, PM company rules, pricing rules, warranty policy |
| **Sheets** | `sop_library`, `troubleshooting_library`, `pm_companies` |

## Objective

Give technicians, dispatchers, and admins instant, consistent answers from the company's own procedures, so training is faster and answers don't depend on who you ask.

## Flow

```mermaid
flowchart LR
    A[Question from team member] --> B[Identify role]
    B --> C[Search knowledge base]
    C --> D[Apply company + PM-specific rules]
    D --> E[Answer with source SOP]
    E --> F[Log question · flag gaps]
```

## Knowledge sources

| Source | Examples |
|--------|----------|
| Operations SOPs | Intake (required info, priority, emergencies, tenant communication) · Assessment (photos, notes, troubleshooting, scope format) · Completion (checklist, documentation, QA) |
| Technician library | Plumbing (leaks, faucets, toilets, water heaters) · Electrical (outlets, breakers, lighting, safety) · HVAC (filters, thermostats, cooling) · General (drywall, painting, doors, locks) |
| PM company rules | Approval limits, emergency process, communication channel, required photos, invoice format, portal requirements |
| Policies | Pricing rules, assessment fee, warranty, callbacks |

## Example questions by role

| Role | Question | Answer draws on |
|------|----------|-----------------|
| Technician | "No hot water. What do I check first?" | Troubleshooting library: power/gas → thermostat → element → document → photos |
| Technician | "What do I need before closing a plumbing job?" | Completion SOP: findings, action taken, repair completed, before/after photos, tenant confirmation |
| Technician | "Does this repair need approval?" | Answer: "Submit your assessment; the system will tell you." (No limits disclosed.) |
| Dispatcher | "Tenant won't provide access. What now?" | Scenario 12 playbook #2 |
| Admin | "What happens when an estimate is declined?" | Mark declined → assessment invoice → notify accounting → close |
| New hire | "Walk me through dispatcher training." | Onboarding path: intake → tenant communication → scheduling → escalations |

## Guardrails

- Answers cite the SOP name and version.
- Technicians never receive PM limits, client prices, or margins from the assistant.
- Unanswered or low-confidence questions are logged as SOP gaps for the operations manager.
- Before a job closes, the assistant's QA check lists missing items, e.g. "Upload after-repair photos before closing."

## Test checklist

- [ ] Ten common questions per role answered correctly with a cited SOP.
- [ ] A technician asking for the NTE limit is redirected.
- [ ] Gap log captures a question the SOPs don't cover.
