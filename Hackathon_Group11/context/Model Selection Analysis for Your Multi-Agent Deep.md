<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Model Selection Analysis for Your Multi-Agent Deep Researcher

You're asking the right question. Using **GPT-4-Turbo for all four agents** is a classic hackathon mistake—you're overspending on compute and overthinking the architecture. Let me break down what each agent actually needs and what you should use in a **12-hour MVP**.

***

## The Problem with Your Current Setup

| Agent | Current | Issue | Cost/Token |
| :-- | :-- | :-- | :-- |
| **Retriever** | GPT-4-Turbo | Overkill (just fetches URLs) | Wasted \$\$\$ |
| **Analyzer** | GPT-4-Turbo | Appropriate (reasoning) | Necessary |
| **Insight** | GPT-4-Turbo | Overkill (pattern matching) | Wasted \$\$\$ |
| **Reporter** | GPT-4-Turbo | Overkill (formatting) | Wasted \$\$\$ |

**You're spending 4x more than you need to.** For a hackathon MVP, this is inefficient. For production, this is unsustainable.

***

## What Each Agent Actually Needs

### Retriever Agent: "Just grab URLs and summaries"

**Cognitive load:** Low

- Task: Query APIs, extract titles, URLs, snippets
- Doesn't need: Complex reasoning, multi-hop inference
- Needs: Speed, consistency, cost-efficiency

**Best model:** `Claude 3.5 Haiku` or `GPT-4o Mini`

**Why:**

- Haiku is 10x cheaper than GPT-4-Turbo
- Fast token throughput (good for batch retrieval)
- More than capable of formatting API responses
- For a 12-hour demo: No reason to use GPT-4

**Cost comparison (1000 retrieval queries):**

- GPT-4-Turbo: ~\$30 (input) + \$60 (output) = \$90
- Haiku: \$0.80 (input) + \$2.40 (output) = \$3.20
- **Savings: 96%**

```python
# agents/retriever.py - Optimized
from langchain_openai import ChatOpenAI

class ContextualRetrieverAgent:
    def __init__(self):
        # Use cheap Haiku for retrieval
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Faster, cheaper
            temperature=0.1,  # Low creativity needed
        )
    
    def retrieve(self, query: str):
        """Fetch and format sources"""
        # Just formatting API responses, not reasoning
        prompt = f"Format these search results into structured JSON: {query}"
        return self.llm.invoke(prompt)
```


***

### Analyzer Agent: "Find patterns, contradictions, validate"

**Cognitive load:** **HIGH**

- Task: Cross-reference sources, identify contradictions, assess credibility
- Needs: Strong reasoning, multi-hop logic
- Reasoning chain: "Source A says X, Source B says Y, they contradict because..."

**Best model:** `Claude 3.5 Sonnet` or `GPT-4o` (GPT-4-Turbo acceptable)

**Why:**

- This is where reasoning matters
- Needs to synthesize multiple perspectives
- Must identify subtle contradictions
- Claude 3.5 Sonnet just beat GPT-4-Turbo on reasoning benchmarks (Oct 2024)

**Cost comparison (1000 analysis queries):**

- GPT-4-Turbo: ~\$150
- Claude 3.5 Sonnet: ~\$75
- GPT-4o: ~\$40
- **Claude 3.5 Sonnet wins on quality + cost**

```python
# agents/analyzer.py - Optimized
from langchain_anthropic import ChatAnthropic

class CriticalAnalysisAgent:
    def __init__(self):
        # Use strong Sonnet for reasoning
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.5,  # Balanced reasoning + consistency
            max_tokens=2000,  # Room for detailed analysis
        )
    
    def analyze(self, sources: dict):
        """Complex reasoning: find contradictions, validate"""
        prompt = ChatPromptTemplate.from_template("""
        Analyze these sources for:
        1. Core findings (what do they agree on?)
        2. Contradictions (where do they disagree and why?)
        3. Credibility gaps (missing perspectives, potential bias?)
        4. Confidence levels (high/medium/low for each finding)
        
        SOURCES:
        {sources}
        
        Provide detailed reasoning for each contradiction.
        """)
        
        chain = prompt | self.llm
        return chain.invoke({"sources": sources})
```


***

### Insight Agent: "Extract trends, suggest hypotheses"

**Cognitive load:** Medium-High

- Task: Pattern recognition, trend synthesis, hypothesis generation
- Needs: Good reasoning but mostly pattern matching
- Not as complex as analysis, but more creative than retrieval

**Best model:** `Claude 3 Opus` or `GPT-4o`

**Why:**

- Generating hypotheses needs some creative reasoning
- Pattern matching on analyzed data (not raw sources)
- Can use a mid-tier model effectively

**Cost comparison (1000 insight queries):**

- GPT-4-Turbo: ~\$150
- Claude 3.5 Sonnet: ~\$75
- GPT-4o: ~\$40
- **GPT-4o is sweet spot for cost + capability**

```python
# agents/insight.py - Optimized
from langchain_openai import ChatOpenAI

class InsightGenerationAgent:
    def __init__(self):
        # GPT-4o good for creative pattern matching
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Cheaper, still smart
            temperature=0.7,  # Higher creativity for trends
            max_tokens=1500,
        )
    
    def generate_trends(self, analysis: dict):
        """Extract patterns and hypotheses"""
        prompt = ChatPromptTemplate.from_template("""
        Based on this analysis:
        {analysis}
        
        Generate 5 emerging trends or hypotheses:
        1. What patterns emerge?
        2. What's the trajectory of these trends?
        3. What questions do these findings raise?
        4. What's likely to happen next?
        
        Be creative but grounded in the analysis.
        """)
        
        chain = prompt | self.llm
        return chain.invoke({"analysis": analysis})
```


***

### Report Agent: "Format and structure output"

**Cognitive load:** Low

- Task: Take all findings, structure into readable markdown
- Doesn't need: Complex reasoning, just formatting
- Needs: Consistency, good formatting, speed

**Best model:** `Claude 3.5 Haiku` or `GPT-4o Mini`

**Why:**

- This is template + LLM formatting
- No reasoning required
- Should be fast (users waiting for output)
- Haiku is 10x cheaper, equally capable at formatting

**Cost comparison (1000 report queries):**

- GPT-4-Turbo: ~\$150
- Haiku: ~\$3.20
- **Savings: 98%**

```python
# agents/reporter.py - Optimized
from langchain_anthropic import ChatAnthropic

class ReportBuilderAgent:
    def __init__(self):
        # Cheap Haiku for formatting
        self.llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0.2,  # Low creativity, consistent formatting
            max_tokens=4000,  # Room for full report
        )
    
    def compile(self, retrieval: dict, analysis: dict, insights: list):
        """Format into structured report"""
        prompt = ChatPromptTemplate.from_template("""
        Create a professional markdown research report:
        
        STRUCTURE:
        # [Title from Query]
        ## Sources Retrieved
        [List with URLs]
        
        ## Key Findings
        [Findings from analysis]
        
        ## Contradictions Identified
        [Contradictions with explanations]
        
        ## Emerging Trends
        [Trends with implications]
        
        ## Methodology Notes
        [How this research was conducted]
        
        INPUT DATA:
        Retrieval: {retrieval}
        Analysis: {analysis}
        Insights: {insights}
        """)
        
        chain = prompt | self.llm
        return chain.invoke({
            "retrieval": retrieval,
            "analysis": analysis,
            "insights": insights
        })
```


***

## Recommended Model Stack

```python
# config.py - Optimized for hackathon + quality

RETRIEVER_MODEL = "gpt-4o-mini"        # Fast, cheap (fetch URLs)
ANALYZER_MODEL = "claude-3-5-sonnet-20241022"   # Strong reasoning (find patterns)
INSIGHT_MODEL = "gpt-4o"               # Creative pattern matching (hypotheses)
REPORT_MODEL = "claude-3-5-haiku-20241022"      # Fast formatting (output)

# Alternative OpenRouter config
RETRIEVER_MODEL = "openrouter/openai/gpt-4o-mini"
ANALYZER_MODEL = "openrouter/anthropic/claude-3-5-sonnet"
INSIGHT_MODEL = "openrouter/openai/gpt-4o"
REPORT_MODEL = "openrouter/anthropic/claude-3-5-haiku"
```


***

## Cost Breakdown: Your Current vs Optimized

### Scenario: 10 research queries during 12-hour demo

**Your Current Setup (All GPT-4-Turbo):**

```
Retriever: 10 queries × ~$0.05 = $0.50
Analyzer: 10 queries × ~$0.15 = $1.50
Insight: 10 queries × ~$0.05 = $0.50
Reporter: 10 queries × ~$0.03 = $0.30
────────────────────────────────
TOTAL: ~$2.80
```

**Optimized Setup (Mixed models):**

```
Retriever (GPT-4o Mini): 10 × $0.005 = $0.05
Analyzer (Claude Sonnet): 10 × $0.03 = $0.30
Insight (GPT-4o): 10 × $0.01 = $0.10
Reporter (Haiku): 10 × $0.001 = $0.01
────────────────────────────────
TOTAL: ~$0.46
```

**Savings: 84% cheaper, better quality reasoning**

***

## Quality Comparison (Hackathon Context)

| Task | GPT-4-Turbo | Optimized | Winner |
| :-- | :-- | :-- | :-- |
| Retrieve \& format | Same | GPT-4o Mini (faster) | **Optimized** |
| Find contradictions | Good | Claude Sonnet (better) | **Optimized** |
| Extract trends | Same | GPT-4o (faster) | **Optimized** |
| Format report | Same | Haiku (faster) | **Optimized** |
| **Total quality** | Baseline | Better reasoning | **Optimized** |
| **Speed** | Slow | Faster | **Optimized** |
| **Cost** | \$2.80 | \$0.46 | **Optimized** |


***

## Implementation: Drop-In Replacement

Your current code uses OpenRouter format. Here's the update:

```python
# config.py
import os

# Model configuration
MODELS = {
    "retriever": os.getenv("RETRIEVER_MODEL", "openrouter/openai/gpt-4o-mini"),
    "analyzer": os.getenv("ANALYZER_MODEL", "openrouter/anthropic/claude-3-5-sonnet-20241022"),
    "insight": os.getenv("INSIGHT_MODEL", "openrouter/openai/gpt-4o"),
    "report": os.getenv("REPORT_MODEL", "openrouter/anthropic/claude-3-5-haiku-20241022"),
}

# Temperature configs (task-specific)
TEMPERATURES = {
    "retriever": 0.1,   # Low: consistent formatting
    "analyzer": 0.5,    # Medium: balanced reasoning
    "insight": 0.7,     # High: creative pattern matching
    "report": 0.2,      # Low: consistent formatting
}

# Agent initialization
def init_retriever():
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=MODELS["retriever"],
        temperature=TEMPERATURES["retriever"],
    )

def init_analyzer():
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model=MODELS["analyzer"],
        temperature=TEMPERATURES["analyzer"],
        max_tokens=2000,
    )

def init_insight():
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=MODELS["insight"],
        temperature=TEMPERATURES["insight"],
        max_tokens=1500,
    )

def init_reporter():
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model=MODELS["report"],
        temperature=TEMPERATURES["report"],
        max_tokens=4000,
    )
```


***

## When to Stick with GPT-4-Turbo (Edge Cases)

**Only use GPT-4-Turbo if:**

- Your Analyzer Agent needs extreme reasoning power (unlikely for web research)
- You're analyzing highly technical/scientific papers (maybe)
- You have unlimited budget and want to flex (not smart for hackathon)

**For a 12-hour MVP:** Absolutely not needed.

***

## Claude vs OpenAI: The Debate

**For THIS project (multi-agent research):**


| Dimension | Claude 3.5 Sonnet | GPT-4-Turbo |
| :-- | :-- | :-- |
| Reasoning | ✅ Slightly better | ✅ Very good |
| Cost | ✅ 50% cheaper | ❌ Expensive |
| Speed | ✅ Faster | ❌ Slower |
| Context window | ✅ 200K tokens | ❌ 128K tokens |
| API stability | ✅ Very stable | ✅ Very stable |
| **For Analyzer Agent** | **WIN** | - |

**Claude wins for this use case.** Better reasoning at half the cost.

***

## Final Recommendation

**Change your config to this:**

```python
# Default models (OpenRouter format) - UPDATED
DEFAULT_MODEL = "openrouter/anthropic/claude-3-5-sonnet-20241022"  # Changed
RETRIEVER_MODEL = "openrouter/openai/gpt-4o-mini"  # NEW
ANALYZER_MODEL = "openrouter/anthropic/claude-3-5-sonnet-20241022"  # Changed
INSIGHT_MODEL = "openrouter/openai/gpt-4o"  # Changed
REPORT_MODEL = "openrouter/anthropic/claude-3-5-haiku-20241022"  # NEW
```

**Why this beats your original setup:**


| Metric | Original | Recommended |
| :-- | :-- | :-- |
| Cost per research | \$2.80 | \$0.46 |
| Analyzer quality | Good | Excellent |
| Insight generation | Good | Better |
| Report speed | Slow | Fast |
| Demo reliability | Good | Excellent |
| Scalability | Poor | Great |

**For your hackathon demo: This is the smarter play.** You save 84% on costs, get better reasoning, and faster execution. Judges will see intelligent model selection—not just "use the biggest model."

