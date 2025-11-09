from openai import OpenAI  # type: ignore[import-untyped]
import json
import re
from typing import Dict, List, Any

class ErrorAnalyzer:
    """Analyzes log files for errors using OpenRouter LLM"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = "openai/gpt-4o-mini"  # Using cost-effective model via OpenRouter
    
    def extract_error_lines(self, log_content: str) -> List[str]:
        """Extract lines that likely contain errors"""
        error_keywords = [
            'error', 'exception', 'failed', 'failure', 'fatal',
            'traceback', 'stack trace', 'err', 'critical',
            'panic', 'abort', 'timeout', 'denied', 'forbidden'
        ]
        
        lines = log_content.split('\n')
        error_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in error_keywords):
                error_lines.append(line)
        
        # Return last 50 error lines to avoid token limits
        return error_lines[-50:] if len(error_lines) > 50 else error_lines
    
    def analyze_errors(self, log_content: str) -> Dict[str, Any]:
        """Analyze log content and return structured error analysis"""
        
        # Extract error lines
        error_lines = self.extract_error_lines(log_content)
        
        if not error_lines:
            return {
                'error_type': 'No errors found',
                'severity': 'Info',
                'causes': [],
                'solutions': []
            }
        
        # Prepare context for LLM
        error_context = '\n'.join(error_lines[-20:])  # Last 20 error lines
        
        # Create prompt for LLM
        prompt = f"""Analyze the following log errors and provide a structured analysis.

Log Error Context:
{error_context}

Please provide a JSON response with the following structure:
{{
    "error_type": "Brief error type/category (e.g., 'Database Connection Timeout', 'Authentication Failure', 'Memory Overflow')",
    "severity": "Critical|High|Medium|Low",
    "issue_category": "Network Issue|Database Issue|Security Issue|Resource Issue|Code Issue|General Error",
    "causes": [
        {{
            "title": "Cause title (be specific)",
            "description": "Detailed explanation of this root cause"
        }}
    ],
    "solutions": [
        {{
            "title": "Solution title (be specific and actionable)",
            "description": "What this solution does and why it works",
            "steps": ["Step 1 (specific action)", "Step 2 (specific action)", "Step 3 (specific action)"],
            "code_example": "Optional code example if applicable, otherwise empty string"
        }},
        {{
            "title": "Solution 2 title",
            "description": "What this solution does",
            "steps": ["Step 1", "Step 2"],
            "code_example": ""
        }},
        {{
            "title": "Solution 3 title",
            "description": "What this solution does",
            "steps": ["Step 1", "Step 2", "Step 3"],
            "code_example": ""
        }}
    ]
}}

Requirements:
- Provide exactly 3 solutions
- Solutions should be practical and actionable
- Include code examples if the solution involves code changes
- Be specific and technical
- Focus on root causes, not just symptoms
- Classify the issue_category based on the error type (Network, Database, Security, Resource, Code, or General)
- Make error_type descriptive and specific

Return ONLY valid JSON, no additional text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software engineer and DevOps specialist who analyzes log files and provides actionable solutions. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Validate structure
            if 'error_type' not in result:
                result['error_type'] = 'Unknown Error'
            if 'severity' not in result:
                result['severity'] = 'Medium'
            if 'issue_category' not in result:
                result['issue_category'] = 'General Error'
            if 'causes' not in result:
                result['causes'] = []
            if 'solutions' not in result:
                result['solutions'] = []
            
            # Ensure exactly 3 solutions
            if len(result['solutions']) < 3:
                # Pad with generic solutions if needed
                while len(result['solutions']) < 3:
                    result['solutions'].append({
                        'title': f'Alternative Solution {len(result["solutions"]) + 1}',
                        'description': 'Review the error context and apply appropriate fixes',
                        'steps': ['Analyze the error', 'Identify root cause', 'Apply fix'],
                        'code_example': ''
                    })
            elif len(result['solutions']) > 3:
                result['solutions'] = result['solutions'][:3]
            
            return result
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return {
                'error_type': 'JSON Parse Error',
                'severity': 'High',
                'causes': [{
                    'title': 'LLM Response Parsing Failed',
                    'description': f'Could not parse LLM response: {str(e)}'
                }],
                'solutions': [
                    {
                        'title': 'Retry Analysis',
                        'description': 'Try analyzing the log file again',
                        'steps': ['Click Analyze Errors again', 'Check API key', 'Verify log file format'],
                        'code_example': ''
                    },
                    {
                        'title': 'Check API Connection',
                        'description': 'Verify OpenRouter API is accessible',
                        'steps': ['Check internet connection', 'Verify API key', 'Check API quota'],
                        'code_example': ''
                    },
                    {
                        'title': 'Manual Review',
                        'description': 'Review the log file manually',
                        'steps': ['Open log file', 'Search for error keywords', 'Review stack traces'],
                        'code_example': ''
                    }
                ]
            }
        except Exception as e:
            return {
                'error_type': 'Analysis Error',
                'severity': 'High',
                'causes': [{
                    'title': 'Analysis Failed',
                    'description': f'Error during analysis: {str(e)}'
                }],
                'solutions': [
                    {
                        'title': 'Check API Key',
                        'description': 'Verify OpenRouter API key is correct',
                        'steps': ['Check API key in sidebar', 'Verify key is valid', 'Check API quota'],
                        'code_example': ''
                    },
                    {
                        'title': 'Retry Analysis',
                        'description': 'Try the analysis again',
                        'steps': ['Click Analyze Errors again', 'Wait for completion'],
                        'code_example': ''
                    },
                    {
                        'title': 'Contact Support',
                        'description': 'If issue persists, contact support',
                        'steps': ['Document the error', 'Check logs', 'Contact administrator'],
                        'code_example': ''
                    }
                ]
            }

