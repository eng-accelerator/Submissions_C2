# Hackathon Topics to Choose From

Below are suggested hackathon project topics. Each section includes what the project demonstrates, why it’s a good fit, and relevant agents or tech where applicable.

---

## 1. Multi-agent DevOps Incident Analysis Suite

### What it demonstrates
- An app that lets users upload ops logs for live analysis.
- Multiple agents collaborate to analyze logs and drive remediation.
	- Log reader / classifier agent: parses logs, categorizes events, extracts structured fields.
	- Remediation agent: maps detected issues to fixes and rationale.
	- Notification agent: pushes solutions to Slack (or other channels).
	- Cookbook synthesizer agent: generates actionable checklists.
	- JIRA ticket agent: creates tickets for critical incidents.
	- Orchestrator (e.g., Langgraph): manages flow between agents.

### Why it's ideal
- Demonstrates multi-agent orchestration, automated remediation, and integrated notifications.
- Produces traceable, actionable output for operators.

### Perfect for
- DevOps, SRE, and incident management teams.

---

## 2. Multimodal AI Design Analysis Suite

### What it demonstrates
- An app where users upload product or app designs for automated critique and benchmarking.
- Example agents:
	- Visual analysis agent: extracts layout/color/element details from images.
	- UX critique agent: evaluates flows, clarity, and accessibility.
	- Market research agent: compares designs to competitors and trends.

### Why it's ideal
- Leverages image RAG, multimodal LLMs, and domain-specific UX heuristics.
- Produces structured, actionable suggestions for designers and product teams.

### Perfect for
- Product managers, UI/UX designers, and product teams.

---

## 3. AI Financial Coach Agent

### What it demonstrates
- A personalized multi-agent financial advisor that ingests user financial data (documents, transactions) and recommends plans.
- Example agents:
	- Debt analyzer agent
	- Custom savings strategy agent
	- Actionable budgeting advisor
	- Debt payoff optimizer

### Why it's ideal
- Combines agent orchestration, tabular RAG, user-data integration, and LLM workflows with dashboards.

### Perfect for
- Personal finance apps, fintech demos, and financial literacy tools.

---

## 4. Multi-Agent AI Deep Researcher

### What it demonstrates
- An AI research assistant for multi-hop, multi-source investigations using specialized agents.
- Example agents:
	- Contextual Retriever Agent: pulls data from papers, news, reports, and APIs.
	- Critical Analysis Agent: summarizes findings, flags contradictions, and validates sources.
	- Insight Generation Agent: proposes hypotheses or trends via reasoning chains.
	- Report Builder Agent: compiles structured reports from the findings.

### Why it's ideal
- Showcases agent collaboration, retrieval-augmented reasoning, and synthesis over long contexts.

### Tech / frameworks
- LangChain / Langgraph, LlamaIndex, or similar retrieval/agent frameworks.

---

## 5. Cyber Security AI Agent

### What it demonstrates
- A multi-agent cybersecurity system that monitors logs, detects threats, and recommends fixes.
- Example agents:
	- Log Monitor Agent: detects unusual activity from system and network logs.
	- Threat Intelligence Agent: checks CVEs and external threat feeds.
	- Vulnerability Scanner Agent: scans code, APIs, or containers for weaknesses.
	- Incident Response Agent: generates step-by-step remediation plans.
	- Policy Checker Agent: evaluates setups against standards (ISO, NIST, SOC2).

### Why it's ideal
- Demonstrates real-time threat detection, RAG-enabled context checks, and automated response planning.

### Perfect for
- Security engineers, DevOps, and IT teams.

---

## 6. Browser Automation AI Agent

### What it does
- An AI system that automates browser tasks (testing, form-filling, scraping, user journeys) and self-heals when things break.
- Example agents:
	- Flow Discovery Agent: identifies key user flows to automate (login, signup, checkout).
	- Script Generator Agent: writes Playwright / Puppeteer / Selenium scripts.
	- Execution Agent: runs scripts, records results, takes screenshots/videos.
	- Error Diagnosis Agent: inspects failures (broken selectors, timeouts, missing elements) and explains root causes.
	- Adaptive Repair Agent: attempts fixes and retries.
	- Regression Monitor Agent (optional): compares UI screenshots to catch layout regressions.

### Why it's useful
- Turns browser automation into a smart, self-healing system that reduces manual test maintenance.

### Typical tech stack
- Language: Python or Node.js
- Automation: Playwright, Puppeteer, StageHand, or Selenium
- AI layer: LLMs (GPT, CodeLlama) for code generation and reasoning
- Optional: visual diff tools (Pixelmatch, Playwright Test), CI/CD integration (GitHub Actions, Docker)


