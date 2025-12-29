---
name: model-selection-skill
description: Choose the best Codex model (gpt-4 family, gpt-4o-mini, or legacy davinci) based on the workload described; use when the user asks for a model suggestion, wants to optimize quality vs cost/latency, or says “change model” for the current answer.
---

# Purpose
Use this skill whenever a user specifically asks you to switch models, wants a recommendation, or frames the task as “best model for …”. It instructs the next agent on how to evaluate the problem characteristics and pick the engine.

# Workflow
1. Assess the request: identify whether it is reasoning-heavy (architectural planning, complex algorithms), code-edit/refactor (short changes), interactive latency-sensitive, or compatibility-driven (legacy instructions).
2. Consult `references/models.md` for the current model capabilities and constraints before choosing; keep the table fresh if new offerings arrive.
3. Select the model that balances accuracy, cost, and latency:
   - Use `gpt-4.1` for analysis/design or long explanations (quality prioritized).
   - Use `gpt-4o-mini` for concise edits, rapid iterations, or when tokens/cost matter.
   - Use `gpt-4o-realtime-preview` only when the user explicitly needs streaming/real-time behavior.
   - Use `text-davinci-003` only if compatibility or deterministic formatting from legacy scripts is required.
4. Prefix your answer with the chosen model and why it is appropriate, e.g. `Model: gpt-4.1 — Deep reasoning is required for ...`.
5. If the user later asks for another change, repeat the evaluation before responding again.

# Resources
- `references/models.md` — quick overview of the available models and their ideal use cases.
