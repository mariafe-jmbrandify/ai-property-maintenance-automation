# Prompt: Trade Classification (Scenario 5)

Runs only when Scenario 1 left `trade` empty.

```text
Classify this maintenance request into exactly one trade.

Allowed values:
Plumbing, Electrical, HVAC, Appliance, Roofing, Drywall, Painting, Carpentry, General Maintenance

Return only the value, with no punctuation or explanation.
If the request involves more than one trade, return the trade needed FIRST to stop damage
(for example, a ceiling stain from a leak is Plumbing, not Drywall).

Request:
{{issue_description}}
Tenant notes:
{{tenant_notes}}
```

Validate the response against the allowed list. Anything else → `General Maintenance` and flag for dispatcher review.
