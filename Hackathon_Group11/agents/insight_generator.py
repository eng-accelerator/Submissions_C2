"""
Insight Generation Agent
Suggests hypotheses or trends using reasoning chains.
"""

import logging
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_config import create_insight_llm, INSIGHT_MODEL, TEMPERATURES

logger = logging.getLogger(__name__)


class InsightGenerationAgent:
    """Generates insights, hypotheses, and trends from analyzed sources."""
    
    def __init__(self, model: str = None, temperature: float = None):
        """Initialize the insight generation agent with LLM via OpenRouter.
        
        Uses GPT-4o for creative pattern matching and hypothesis generation.
        Default temperature: 0.7 (higher creativity for trends).
        """
        # Use optimized insight LLM with GPT-4o
        if model or temperature is not None:
            from utils.llm_config import create_llm
            self.llm = create_llm(
                model=model or INSIGHT_MODEL,
                temperature=temperature if temperature is not None else TEMPERATURES["insight"],
                max_tokens=1500
            )
        else:
            self.llm = create_insight_llm()
        if not self.llm:
            logger.warning("OpenRouter API key not found. Insights will use mock data.")
    
    def generate(self, analysis: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Generate insights, hypotheses, and trends from analysis.
        
        Args:
            analysis: Analysis results from CriticalAnalysisAgent
            query: Original research query
            
        Returns:
            Insights including hypotheses, trends, and reasoning chains
        """
        logger.info("Insight Generator: Generating insights and hypotheses")
        
        if not self.llm:
            return self._mock_insights(analysis, query)
        
        # Format analysis for prompt
        analysis_text = self._format_analysis(analysis)
        
        # Create insight generation prompt
        prompt = ChatPromptTemplate.from_template("""
You are an expert research analyst generating insights from research findings.

ORIGINAL QUERY: {query}

ANALYSIS FINDINGS:
{analysis_text}

Based on this analysis, generate:

1. **Key Insights** (3-5 insights): High-level observations that synthesize the findings
2. **Hypotheses** (2-3 hypotheses): Testable propositions based on the evidence
3. **Trends** (2-3 trends): Patterns or directions identified across sources
4. **Reasoning Chains** (2-3 chains): Logical if-then reasoning paths connecting evidence to conclusions

Format your response as:
INSIGHTS:
- Insight 1
- Insight 2
- Insight 3

HYPOTHESES:
- Hypothesis 1 (with brief reasoning)
- Hypothesis 2 (with brief reasoning)

TRENDS:
- Trend 1: Description
- Trend 2: Description

REASONING CHAINS:
- Chain 1: If [evidence] then [conclusion] because [reasoning]
- Chain 2: If [evidence] then [conclusion] because [reasoning]
""")
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "query": query,
                "analysis_text": analysis_text
            })
            
            insights_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse the response
            parsed_insights = self._parse_insights(insights_text)
            
            logger.info(f"Insight Generator: Generated {len(parsed_insights.get('insights', []))} insights")
            
            return {
                "insights": parsed_insights.get("insights", []),
                "hypotheses": parsed_insights.get("hypotheses", []),
                "trends": parsed_insights.get("trends", []),
                "reasoning_chains": parsed_insights.get("reasoning_chains", []),
                "raw_insights": insights_text
            }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Insight generation failed: {error_msg}")
            
            # Check for authentication errors
            if "401" in error_msg or "Unauthorized" in error_msg or "User not found" in error_msg:
                logger.error("=" * 60)
                logger.error("OPENROUTER API KEY ERROR:")
                logger.error("The API key is invalid, expired, or not set correctly.")
                logger.error("")
                logger.error("Please check:")
                logger.error("1. OPEN_ROUTER_KEY is set in your .env file")
                logger.error("2. API key is correct (starts with 'sk-or-')")
                logger.error("3. API key is active at https://openrouter.ai/keys")
                logger.error("4. API key has sufficient credits")
                logger.error("5. No extra quotes or spaces in .env file")
                logger.error("")
                logger.error("Get your API key from: https://openrouter.ai/keys")
                logger.error("=" * 60)
            
            return self._mock_insights(analysis, query)
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results for the LLM prompt."""
        formatted = []
        
        if analysis.get("summary"):
            formatted.append("SUMMARY:")
            for point in analysis["summary"]:
                formatted.append(f"- {point}")
            formatted.append("")
        
        if analysis.get("key_claims"):
            formatted.append("KEY CLAIMS:")
            for claim in analysis["key_claims"]:
                formatted.append(f"- {claim}")
            formatted.append("")
        
        if analysis.get("contradictions"):
            formatted.append("CONTRADICTIONS:")
            for contradiction in analysis["contradictions"]:
                formatted.append(f"- {contradiction}")
            formatted.append("")
        
        if analysis.get("credibility"):
            formatted.append("CREDIBILITY ASSESSMENT:")
            for cred in analysis["credibility"]:
                formatted.append(f"- {cred}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _parse_insights(self, insights_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        parsed = {
            "insights": [],
            "hypotheses": [],
            "trends": [],
            "reasoning_chains": []
        }
        
        current_section = None
        for line in insights_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if 'INSIGHTS:' in line.upper():
                current_section = "insights"
                continue
            elif 'HYPOTHESES:' in line.upper():
                current_section = "hypotheses"
                continue
            elif 'TRENDS:' in line.upper():
                current_section = "trends"
                continue
            elif 'REASONING CHAINS:' in line.upper():
                current_section = "reasoning_chains"
                continue
            
            if current_section and (line.startswith('-') or line.startswith('*')):
                content = line[1:].strip()
                if content:
                    parsed[current_section].append(content)
            elif current_section == "trends" and ':' in line:
                parsed[current_section].append(line)
        
        return parsed
    
    def _mock_insights(self, analysis: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Return mock insights if LLM is not available."""
        return {
            "insights": [
                "The research reveals significant developments in the field",
                "Multiple perspectives indicate ongoing evolution",
                "Recent trends suggest increasing importance"
            ],
            "hypotheses": [
                "Hypothesis 1: The trend will continue based on current evidence",
                "Hypothesis 2: Multiple factors are driving the observed patterns"
            ],
            "trends": [
                "Trend 1: Increasing adoption and interest",
                "Trend 2: Convergence of different approaches"
            ],
            "reasoning_chains": [
                "If current evidence holds, then we can expect continued growth because of strong foundational support",
                "If contradictions are resolved, then consensus will emerge because of converging research"
            ],
            "raw_insights": "Mock insights - LLM not configured"
        }

