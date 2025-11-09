"""
Critical Analysis Agent
Summarizes findings, highlights contradictions, and validates sources.
"""

import logging
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_config import create_analyzer_llm, ANALYZER_MODEL, TEMPERATURES

logger = logging.getLogger(__name__)


class CriticalAnalysisAgent:
    """Analyzes retrieved sources for contradictions, credibility, and key findings."""
    
    def __init__(self, model: str = None, temperature: float = None):
        """Initialize the analysis agent with LLM via OpenRouter.
        
        Uses Claude 3.5 Sonnet for strong reasoning capabilities.
        Default temperature: 0.5 (balanced reasoning).
        """
        # Use optimized analyzer LLM with Claude 3.5 Sonnet
        if model or temperature is not None:
            from utils.llm_config import create_llm
            self.llm = create_llm(
                model=model or ANALYZER_MODEL,
                temperature=temperature if temperature is not None else TEMPERATURES["analyzer"],
                max_tokens=2000
            )
        else:
            self.llm = create_analyzer_llm()
        if not self.llm:
            logger.warning("OpenRouter API key not found. Analysis will use mock data.")
    
    def analyze(self, sources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sources for contradictions, credibility, and key findings.
        
        Args:
            sources: Dictionary with web, papers, and news sources
            
        Returns:
            Analysis results with summaries, contradictions, and credibility scores
        """
        logger.info("Analyzer: Starting analysis of sources")
        
        if not self.llm:
            return self._mock_analysis(sources)
        
        # Format sources for prompt
        sources_text = self._format_sources(sources)
        
        # Create analysis prompt
        prompt = ChatPromptTemplate.from_template("""
You are a critical research analyst. Analyze the following sources retrieved for the query: "{query}"

SOURCES:
{sources_text}

Provide a comprehensive analysis with:
1. **Summary**: 3-5 bullet points summarizing the key findings across all sources
2. **Contradictions**: List any contradictory claims or conflicting information between sources
3. **Credibility Assessment**: Rate each source's credibility (High/Medium/Low) with brief reasoning
4. **Key Claims**: Extract 3-5 main claims or statements from the sources

Format your response as:
SUMMARY:
- Point 1
- Point 2
- Point 3

CONTRADICTIONS:
- Contradiction 1 (if any)
- Contradiction 2 (if any)

CREDIBILITY:
- Source 1: [High/Medium/Low] - Reason
- Source 2: [High/Medium/Low] - Reason

KEY CLAIMS:
- Claim 1
- Claim 2
- Claim 3
""")
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "query": sources.get("query", ""),
                "sources_text": sources_text
            })
            
            analysis_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse the response
            parsed_analysis = self._parse_analysis(analysis_text)
            
            logger.info(f"Analyzer: Analysis complete. Found {len(parsed_analysis.get('contradictions', []))} contradictions")
            
            return {
                "summary": parsed_analysis.get("summary", []),
                "contradictions": parsed_analysis.get("contradictions", []),
                "credibility": parsed_analysis.get("credibility", []),
                "key_claims": parsed_analysis.get("key_claims", []),
                "raw_analysis": analysis_text
            }
        
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._mock_analysis(sources)
    
    def _format_sources(self, sources: Dict[str, Any]) -> str:
        """Format sources into readable text for the LLM."""
        formatted = []
        
        if sources.get("web"):
            formatted.append("WEB SOURCES:")
            for i, web in enumerate(sources["web"][:5], 1):
                formatted.append(f"{i}. {web.get('title', 'No title')}")
                formatted.append(f"   {web.get('snippet', 'No snippet')}")
                formatted.append(f"   URL: {web.get('url', 'No URL')}")
                formatted.append("")
        
        if sources.get("papers"):
            formatted.append("RESEARCH PAPERS:")
            for i, paper in enumerate(sources["papers"][:5], 1):
                formatted.append(f"{i}. {paper.get('title', 'No title')}")
                formatted.append(f"   Authors: {paper.get('authors', 'Unknown')}")
                formatted.append(f"   Summary: {paper.get('summary', 'No summary')[:200]}...")
                formatted.append(f"   URL: {paper.get('url', 'No URL')}")
                formatted.append("")
        
        if sources.get("news"):
            formatted.append("NEWS SOURCES:")
            for i, news in enumerate(sources["news"][:5], 1):
                formatted.append(f"{i}. {news.get('title', 'No title')}")
                formatted.append(f"   {news.get('snippet', 'No snippet')}")
                formatted.append(f"   URL: {news.get('url', 'No URL')}")
                formatted.append("")
        
        return "\n".join(formatted)
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        parsed = {
            "summary": [],
            "contradictions": [],
            "credibility": [],
            "key_claims": []
        }
        
        current_section = None
        for line in analysis_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if 'SUMMARY:' in line.upper():
                current_section = "summary"
                continue
            elif 'CONTRADICTIONS:' in line.upper():
                current_section = "contradictions"
                continue
            elif 'CREDIBILITY:' in line.upper():
                current_section = "credibility"
                continue
            elif 'KEY CLAIMS:' in line.upper():
                current_section = "key_claims"
                continue
            
            if current_section and (line.startswith('-') or line.startswith('*')):
                content = line[1:].strip()
                if content:
                    parsed[current_section].append(content)
            elif current_section == "credibility" and ':' in line:
                parsed[current_section].append(line)
        
        return parsed
    
    def _mock_analysis(self, sources: Dict[str, Any]) -> Dict[str, Any]:
        """Return mock analysis if LLM is not available."""
        return {
            "summary": [
                "Sources provide comprehensive coverage of the topic",
                "Multiple perspectives identified across different source types",
                "Recent developments highlighted in news sources"
            ],
            "contradictions": [
                "Some sources present conflicting viewpoints on key aspects"
            ],
            "credibility": [
                "Research papers: High - Peer-reviewed sources",
                "News sources: Medium - Recent but need verification",
                "Web sources: Medium - Mixed credibility"
            ],
            "key_claims": [
                "Topic shows significant recent development",
                "Multiple stakeholders involved",
                "Ongoing research and discussion"
            ],
            "raw_analysis": "Mock analysis - LLM not configured"
        }

