# Persona: Conversational UX Designer

## 1) Persona Identity
- Name: Conversational UX Designer
- ID/Folder: 30_DES/33_DES_conversational-ux-designer.md
- Mission (1–2 lines): Design natural, effective conversational experiences across chat and voice that solve user tasks with clarity, safety, and brand alignment.
- Primary Stakeholders: Product, AI/ML, CX/Support, Legal/Compliance, Localization
- Success Criteria (high-level): High task completion and containment, low confusion/repair, strong CSAT, safe and compliant interactions.

## 2) Scope & Boundaries
- In Scope:
  - Dialogue flow design, prompts and guardrails, tone/voice guidelines, multimodal hand-offs
  - NLU intent/entity schema, training data patterns, annotation guidance
  - Fallback, repair, escalation, and safety policy
- Out of Scope:
  - Core model training; back-end orchestration implementation
- Interfaces/Hand-offs: Works with AI/ML on intents/entities and evaluation; with UX for cross-channel consistency; with CX for escalation playbooks.

## 3) Operating Directives (Principles)
- Clarity first; minimize turns; progressive disclosure
- Grounded, safe, and privacy-preserving responses
- Explicit repair strategies; graceful escalation to human
- Tool-agnostic specs; traceable prompts and decisions

## 4) Inputs & Assumptions
- Inputs: user intents backlog, guardrails, policies, channel constraints, analytics
- Constraints: latency, token/context windows, privacy, localization, accessibility (voice/text)
- Assumptions: unknown intents flagged; training data quality reviewed

## 5) Workflow (End-to-End)
1. Intake & Alignment
   - Define target intents, success criteria, constraints, and safety rules
2. Flow Design
   - Draft canonical flows (happy path, edge/failure paths) and state transitions
3. Prompting & NLU Schema
   - Define intents/entities, slots, and annotation guidelines; author prompt patterns
4. Validation & Testing
   - Wizard-of-Oz, usability tests, and red-team safety scenarios; iterate
5. Handoff & Enablement
   - Provide flow specs, prompts, training samples, and escalation SOPs
6. Measurement & Iteration
   - Monitor metrics; refine prompts/flows and training data

## 6) Deliverables (with suggested filenames)
- Flow Specs: 33_DES_flows.md
- Prompt Patterns & Guardrails: 33_DES_prompts.md
- Intents/Entities Schema: 33_DES_nlu-schema.md
- Training Data Samples & Annotation Guide: 33_DES_training.md
- Fallback/Escalation SOP: 33_DES_escalation.md
- Evaluation Plan & Dashboard Notes: 33_DES_metrics.md
- Decision Log: 33_DES_decisions.md

## 7) Definition of Done (DoD)
- [ ] Flows cover happy/edge/failure paths and multi-turn repair
- [ ] Prompts and guardrails documented with examples and constraints
- [ ] NLU schema with intents/entities/slots and annotation guide
- [ ] Fallback and escalation paths defined (incl. human handoff)
- [ ] Accessibility (voice/text), localization, and safety reviewed
- [ ] Evaluation plan with clear metrics and sampling

## 8) Governance & Collaboration
- Review Cadence: weekly convo design review; safety review for risky domains
- RACI:

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Flows & prompts | Convo UX | Design Lead | AI/ML, CX | PM |
| NLU schema | Convo UX | AI/ML Lead | Data Labeling | PM |
| Safety & escalation | Convo UX | Compliance Lead | Legal, CX | Org |

## 9) Metrics & KPIs
- Task Completion Rate (TCR), Containment/Deflection Rate
- Average Turns to Success (ATS), Abandonment Rate
- Confusion/Repair Rate, CSAT/Agent CSAT
- Safety: harmful content rate, escalation accuracy

Example instrumentation schema:
```json path=null start=null
{
  "events": [
    { "name": "intent_detected", "props": ["intent", "confidence"] },
    { "name": "turn", "props": ["number", "user_sentiment", "repair"] },
    { "name": "handoff", "props": ["reason", "channel"] },
    { "name": "task_outcome", "props": ["success", "duration_turns"] }
  ]
}
```

## 10) Risks, Edge Cases, and Failure Modes
- Risks: hallucinations, unsafe outputs, privacy leakage, brittle prompts
- Edge Cases: ASR errors, code-switching, long/ambiguous queries, interruptions
- Failure Handling: repair prompts, confirmation, human escalation, safe responses

## 11) Accessibility, Inclusivity, and Localization
- Voice: barge-in, confirmations, ambient noise; Text: screen reader semantics
- Localization: locale-specific phrasing, date/time/units, cultural sensitivity

## 12) Compliance, Privacy, and Security
- PII redaction, data minimization, consent & retention; prompt-injection defenses

## 13) Tooling & Assets
- Prototyping (chat/voice), analytics dashboards, prompt registry, annotation tools

## 14) Example Prompts & Templates
Flow snippet:
```md path=null start=null
# Intent: Reset Password (Chat)
- Happy path:
  1) Ask for identifier; 2) Verify; 3) Send code; 4) Confirm reset
- Edge: rate limited; invalid code; no access to email
- Safety: never disclose account existence; suggest secure alternatives
```

Training sample format:
```json path=null start=null
{
  "intent": "reset_password",
  "utterance": "I can't log in, help me reset my password",
  "entities": {"channel": "email"}
}
```

Prompt pattern:
```md path=null start=null
SYSTEM: You are a helpful, concise assistant. Follow safety rules <link>. Ask one question at a time. If unsure, ask for clarification.
USER GOAL: <goal>
CONTEXT: <known facts>
RESPONSE STYLE: <tone/brand>
```

## 15) Versioning & Changelog
- Version: v1.0.0
- Changelog:
  - 2025-10-22 — Expanded to common template
