"""
Agent 2: Solution Finding Agent
Finds possible solutions for identified errors and provides top 3 options
"""
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json


class SolutionAgent:
    """Agent responsible for finding and ranking solutions"""
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini"):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.4  # Slightly higher for creative solutions
        )
        self.model = model
    
    def find_solutions(
        self,
        error_type: str,
        severity: str,
        error_details: Dict[str, Any],
        aggregated_analysis: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Find top 3 solutions for the given error"""
        
        # Build context from error details
        error_context = f"""
Error Type: {error_type}
Severity: {severity}
Error Details: {json.dumps(error_details, indent=2)}
"""
        
        if aggregated_analysis:
            error_context += f"\nAggregated Analysis: {json.dumps(aggregated_analysis, indent=2)}"
        
        prompt = f"""Based on the following error information, provide exactly 3 solutions ranked by effectiveness and practicality.

{error_context}

Provide a JSON response with this structure:
{{
    "solutions": [
        {{
            "rank": 1,
            "title": "Solution title (be specific and actionable)",
            "description": "What this solution does and why it works",
            "effectiveness": "High|Medium|Low",
            "complexity": "Low|Medium|High",
            "time_estimate": "Brief time estimate (e.g., '5 minutes', '1 hour', '1 day')",
            "steps": ["Step 1 (specific action)", "Step 2 (specific action)", "Step 3 (specific action)"],
            "code_example": "Optional code example if applicable, otherwise empty string",
            "prerequisites": ["prerequisite1", "prerequisite2"],
            "risk_level": "Low|Medium|High"
        }},
        {{
            "rank": 2,
            "title": "Solution 2 title",
            "description": "What this solution does",
            "effectiveness": "High|Medium|Low",
            "complexity": "Low|Medium|High",
            "time_estimate": "Brief time estimate",
            "steps": ["Step 1", "Step 2"],
            "code_example": "",
            "prerequisites": [],
            "risk_level": "Low|Medium|High"
        }},
        {{
            "rank": 3,
            "title": "Solution 3 title",
            "description": "What this solution does",
            "effectiveness": "High|Medium|Low",
            "complexity": "Low|Medium|High",
            "time_estimate": "Brief time estimate",
            "steps": ["Step 1", "Step 2", "Step 3"],
            "code_example": "",
            "prerequisites": [],
            "risk_level": "Low|Medium|High"
        }}
    ]
}}

Requirements:
- Provide exactly 3 solutions
- Rank them by effectiveness (rank 1 = best)
- Solutions should be practical and actionable
- Include code examples if applicable
- Be specific and technical
- Focus on root causes, not just symptoms

Return ONLY valid JSON, no additional text."""

        try:
            messages = [
                SystemMessage(content="You are an expert software engineer and DevOps specialist who provides actionable solutions. Always respond with valid JSON only."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            result_text = response.content.strip()
            
            # Clean JSON if wrapped in markdown
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            result = json.loads(result_text)
            solutions = result.get('solutions', [])
            
            # Ensure exactly 3 solutions
            if len(solutions) < 3:
                while len(solutions) < 3:
                    solutions.append({
                        'rank': len(solutions) + 1,
                        'title': f'Alternative Solution {len(solutions) + 1}',
                        'description': 'Review the error context and apply appropriate fixes',
                        'effectiveness': 'Medium',
                        'complexity': 'Medium',
                        'time_estimate': 'Unknown',
                        'steps': ['Analyze the error', 'Identify root cause', 'Apply fix'],
                        'code_example': '',
                        'prerequisites': [],
                        'risk_level': 'Medium'
                    })
            elif len(solutions) > 3:
                solutions = solutions[:3]
            
            # Sort by rank
            solutions.sort(key=lambda x: x.get('rank', 999))
            
            return solutions
            
        except json.JSONDecodeError as e:
            # Fallback solutions
            return [
                {
                    'rank': 1,
                    'title': 'Retry Analysis',
                    'description': 'Try analyzing the error again with more context',
                    'effectiveness': 'Medium',
                    'complexity': 'Low',
                    'time_estimate': '5 minutes',
                    'steps': ['Click Analyze Errors again', 'Check API key', 'Verify log file format'],
                    'code_example': '',
                    'prerequisites': [],
                    'risk_level': 'Low'
                },
                {
                    'rank': 2,
                    'title': 'Manual Review',
                    'description': 'Review the log file manually for errors',
                    'effectiveness': 'High',
                    'complexity': 'Medium',
                    'time_estimate': '30 minutes',
                    'steps': ['Open log file', 'Search for error keywords', 'Review stack traces'],
                    'code_example': '',
                    'prerequisites': [],
                    'risk_level': 'Low'
                },
                {
                    'rank': 3,
                    'title': 'Contact Support',
                    'description': 'If issue persists, contact support team',
                    'effectiveness': 'High',
                    'complexity': 'Low',
                    'time_estimate': '1 hour',
                    'steps': ['Document the error', 'Check logs', 'Contact administrator'],
                    'code_example': '',
                    'prerequisites': [],
                    'risk_level': 'Low'
                }
            ]
        except Exception as e:
            return [
                {
                    'rank': 1,
                    'title': 'Error in Solution Generation',
                    'description': f'Error occurred: {str(e)}',
                    'effectiveness': 'Low',
                    'complexity': 'Low',
                    'time_estimate': 'Unknown',
                    'steps': ['Check error message', 'Retry operation'],
                    'code_example': '',
                    'prerequisites': [],
                    'risk_level': 'Low'
                }
            ]
    
    def rank_solutions(self, solutions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank solutions by effectiveness and complexity"""
        def solution_score(sol):
            effectiveness_map = {'High': 3, 'Medium': 2, 'Low': 1}
            complexity_map = {'Low': 3, 'Medium': 2, 'High': 1}
            
            eff_score = effectiveness_map.get(sol.get('effectiveness', 'Medium'), 2)
            comp_score = complexity_map.get(sol.get('complexity', 'Medium'), 2)
            
            return eff_score * 2 + comp_score  # Effectiveness weighted more
        
        return sorted(solutions, key=solution_score, reverse=True)

