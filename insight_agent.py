import json
import re
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from config import Config

class LLMClient:
    """Unified LLM client for multiple providers"""
    
    def __init__(self):
        self.config = Config()
        self.setup_client()
    
    def setup_client(self):
        """Setup the appropriate LLM client based on configuration"""
        if self.config.LLM_PROVIDER == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
            self.model = self.config.DEFAULT_MODEL
        elif self.config.LLM_PROVIDER == "anthropic":
            # For Anthropic Claude
            self.client = None  # You would initialize Anthropic client here
            self.model = "claude-3-sonnet-20240229"
        else:
            # For local models
            self.client = None
            self.model = "local"
    
    def generate_text(self, prompt: str, system_message: str = None, max_tokens: int = 1000) -> str:
        """Generate text using the configured LLM"""
        try:
            if self.config.LLM_PROVIDER == "openai":
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            else:
                # Fallback for other providers or local models
                return self._fallback_generation(prompt)
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt: str) -> str:
        """Fallback generation when LLM is not available"""
        # Simple rule-based fallback - REPLACE WITH ACTUAL LLM CALLS
        if "hypothesis" in prompt.lower():
            return "Based on the analysis, there appears to be a correlation between the key variables that warrants further investigation."
        elif "trend" in prompt.lower():
            return "The data shows a consistent upward trend over the observed period with seasonal variations."
        else:
            return "Analysis suggests significant patterns in the data that require additional validation."

class ReasoningType(Enum):
    CAUSAL = "causal"
    CORRELATIONAL = "correlational"
    TEMPORAL = "temporal"
    COMPARATIVE = "comparative"
    PREDICTIVE = "predictive"

@dataclass
class Hypothesis:
    statement: str
    reasoning_chain: List[str]
    confidence: float
    evidence_sources: List[str]
    reasoning_type: ReasoningType
    testable_implications: List[str]

class InsightGenerationAgent:
    def __init__(self, model_name: str = None):
        self.llm = LLMClient()
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.reasoning_patterns = self._initialize_reasoning_patterns()
    
    def _initialize_reasoning_patterns(self) -> Dict[str, List[str]]:
        """Initialize common reasoning patterns for insight generation"""
        return {
            "causal": [
                "If {factor} increases/decreases, then {outcome} changes because...",
                "{Event} likely causes {effect} through mechanism: {mechanism}",
                "The relationship between {A} and {B} suggests {A} influences {B} via {pathway}"
            ],
            "correlational": [
                "When {X} occurs, {Y} tends to co-occur, suggesting potential relationship: {relationship}",
                "Patterns in {dataset} show correlation between {var1} and {var2} with implications for {domain}"
            ],
            "temporal": [
                "Following {event}, we observe {trend} over time, indicating {conclusion}",
                "Historical pattern: {pattern} suggests future {prediction}"
            ],
            "comparative": [
                "Compared to {baseline}, {subject} shows {difference} because {reason}",
                "Analysis of {group1} vs {group2} reveals key differences: {differences}"
            ]
        }
    
    def generate_insights(self, 
                         analysis_data: Dict[str, Any],
                         contradictions: List[str],
                         source_validations: Dict[str, bool]) -> List[Hypothesis]:
        """
        Generate insights and hypotheses from analyzed data using LLM
        """
        print("🔍 Generating insights with LLM...")
        
        # Prepare context for LLM
        context = self._prepare_llm_context(analysis_data, contradictions, source_validations)
        
        # Generate insights using LLM
        llm_insights = self._generate_insights_with_llm(context)
        
        # Parse and structure the insights
        structured_insights = self._parse_llm_insights(llm_insights)
        
        return structured_insights
    
    def _prepare_llm_context(self, analysis_data: Dict, contradictions: List[str], validations: Dict[str, bool]) -> str:
        """Prepare context for LLM processing"""
        context = f"""
        RESEARCH ANALYSIS CONTEXT:
        
        KEY FINDINGS:
        {json.dumps(analysis_data.get('key_findings', []), indent=2)}
        
        CONTRADICTIONS IDENTIFIED:
        {chr(10).join(f"- {contradiction}" for contradiction in contradictions)}
        
        SOURCE VALIDATIONS:
        {json.dumps(validations, indent=2)}
        
        ADDITIONAL CONTEXT:
        {analysis_data.get('summary', 'No additional context available')}
        """
        return context
    
    def _generate_insights_with_llm(self, context: str) -> str:
        """Use LLM to generate insights"""
        
        system_prompt = """You are an expert research analyst. Your task is to generate insightful hypotheses and trends based on research data.

        Generate 3-5 key insights with:
        1. Clear, testable hypotheses
        2. Logical reasoning chains
        3. Confidence estimates (0.0-1.0)
        4. Specific, testable implications
        5. Reasoning type (causal, correlational, temporal, comparative, predictive)

        Format your response as JSON with this structure:
        {
            "insights": [
                {
                    "statement": "Clear hypothesis statement",
                    "reasoning_chain": ["step1", "step2", "step3"],
                    "confidence": 0.85,
                    "reasoning_type": "causal",
                    "testable_implications": ["implication1", "implication2"]
                }
            ]
        }"""
        
        user_prompt = f"""
        Based on the following research analysis, generate key insights and hypotheses:
        
        {context}
        
        Please provide your analysis in the specified JSON format.
        """
        
        response = self.llm.generate_text(user_prompt, system_prompt, max_tokens=1500)
        return response
    
    def _parse_llm_insights(self, llm_response: str) -> List[Hypothesis]:
        """Parse LLM response into structured Hypothesis objects"""
        insights = []
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                for insight_data in data.get('insights', []):
                    try:
                        hypothesis = Hypothesis(
                            statement=insight_data.get('statement', ''),
                            reasoning_chain=insight_data.get('reasoning_chain', []),
                            confidence=float(insight_data.get('confidence', 0.5)),
                            evidence_sources=['llm_analysis'],
                            reasoning_type=ReasoningType(insight_data.get('reasoning_type', 'correlational')),
                            testable_implications=insight_data.get('testable_implications', [])
                        )
                        insights.append(hypothesis)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Failed to parse insight: {e}")
                        continue
            
            # Fallback: if no JSON found, create basic insights
            if not insights:
                insights = self._create_fallback_insights()
                
        except json.JSONDecodeError:
            print("Warning: Failed to parse LLM response as JSON, using fallback insights")
            insights = self._create_fallback_insights()
        
        return insights
    
    def _create_fallback_insights(self) -> List[Hypothesis]:
        """Create fallback insights when LLM fails"""
        return [
            Hypothesis(
                statement="Further investigation needed to validate preliminary findings",
                reasoning_chain=["Initial analysis completed", "Data patterns observed", "Requires additional validation"],
                confidence=0.5,
                evidence_sources=["fallback_analysis"],
                reasoning_type=ReasoningType.CORRELATIONAL,
                testable_implications=["Conduct controlled experiments", "Gather additional data sources"]
            )
        ]
    
    def format_insights_report(self, insights: List[Hypothesis]) -> Dict[str, Any]:
        """Format insights for consumption by Report Builder"""
        return {
            "summary": f"Generated {len(insights)} key insights",
            "insights": [
                {
                    "statement": insight.statement,
                    "reasoning_chain": insight.reasoning_chain,
                    "confidence": insight.confidence,
                    "reasoning_type": insight.reasoning_type.value,
                    "testable_implications": insight.testable_implications
                }
                for insight in insights
            ],
            "metadata": {
                "total_insights": len(insights),
                "average_confidence": sum(i.confidence for i in insights) / len(insights) if insights else 0,
                "reasoning_types_used": list(set(i.reasoning_type.value for i in insights))
            }
        }