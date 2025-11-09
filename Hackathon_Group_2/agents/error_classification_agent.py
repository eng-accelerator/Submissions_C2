"""
Agent 1: Error Classification Agent
Processes multiple log files, classifies errors, aggregates issues, and provides analysis
"""
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re
from datetime import datetime


class ErrorClassificationAgent:
    """Agent responsible for error classification and aggregation"""
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini"):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.3
        )
        self.model = model
    
    def extract_error_lines(self, log_content: str) -> List[str]:
        """Extract lines that likely contain errors"""
        error_keywords = [
            'error', 'exception', 'failed', 'failure', 'fatal',
            'traceback', 'stack trace', 'err', 'critical',
            'panic', 'abort', 'timeout', 'denied', 'forbidden',
            'warning', 'warn', 'alert'
        ]
        
        lines = log_content.split('\n')
        error_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in error_keywords):
                error_lines.append(line)
        
        return error_lines[-100:] if len(error_lines) > 100 else error_lines
    
    def classify_single_log(self, log_content: str, filename: str = "unknown") -> Dict[str, Any]:
        """Classify errors in a single log file"""
        error_lines = self.extract_error_lines(log_content)
        
        if not error_lines:
            return {
                'filename': filename,
                'error_count': 0,
                'errors': [],
                'status': 'no_errors'
            }
        
        # Prepare context for LLM
        error_context = '\n'.join(error_lines[-30:])  # Last 30 error lines
        
        prompt = f"""Analyze the following log errors and provide a structured classification.

Log File: {filename}
Error Context:
{error_context}

Provide a JSON response with this structure:
{{
    "error_count": <number>,
    "errors": [
        {{
            "error_type": "Brief error type",
            "severity": "Critical|High|Medium|Low",
            "frequency": <number of occurrences>,
            "first_occurrence": "timestamp or line number",
            "last_occurrence": "timestamp or line number",
            "message": "Error message summary"
        }}
    ],
    "categories": ["Network", "Database", "Security", "Resource", "Code", "General"],
    "summary": "Brief summary of all errors"
}}

Return ONLY valid JSON."""

        try:
            messages = [
                SystemMessage(content="You are an expert log analyst. Always respond with valid JSON only."),
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
            result['filename'] = filename
            result['status'] = 'analyzed'
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                'filename': filename,
                'error_count': len(error_lines),
                'errors': [{'error_type': 'Parse Error', 'severity': 'Medium', 'message': str(e)}],
                'status': 'parse_error'
            }
        except Exception as e:
            return {
                'filename': filename,
                'error_count': len(error_lines),
                'errors': [{'error_type': 'Analysis Error', 'severity': 'High', 'message': str(e)}],
                'status': 'error'
            }
    
    def process_multiple_logs(self, log_files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Process multiple log files and aggregate results"""
        all_results = []
        total_errors = 0
        error_types = {}
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        
        for log_file in log_files:
            filename = log_file.get('filename', 'unknown')
            content = log_file.get('content', '')
            
            result = self.classify_single_log(content, filename)
            all_results.append(result)
            
            total_errors += result.get('error_count', 0)
            
            # Aggregate error types
            for error in result.get('errors', []):
                error_type = error.get('error_type', 'Unknown')
                severity = error.get('severity', 'Medium')
                
                if error_type not in error_types:
                    error_types[error_type] = {
                        'count': 0,
                        'severity': severity,
                        'files': set()
                    }
                
                error_types[error_type]['count'] += error.get('frequency', 1)
                error_types[error_type]['files'].add(filename)
                
                if severity in severity_counts:
                    severity_counts[severity] += 1
        
        # Convert sets to lists for JSON serialization
        for error_type in error_types:
            error_types[error_type]['files'] = list(error_types[error_type]['files'])
        
        # Aggregate analysis
        aggregated_analysis = self._aggregate_analysis(all_results, error_types, severity_counts)
        
        return {
            'files_processed': len(log_files),
            'total_errors': total_errors,
            'file_results': all_results,
            'aggregated_errors': error_types,
            'severity_distribution': severity_counts,
            'aggregated_analysis': aggregated_analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def _aggregate_analysis(self, results: List[Dict], error_types: Dict, severity_counts: Dict) -> Dict[str, Any]:
        """Create aggregated analysis using LLM"""
        summary_data = {
            'total_files': len(results),
            'total_errors': sum(r.get('error_count', 0) for r in results),
            'error_types': list(error_types.keys()),
            'severity_breakdown': severity_counts,
            'top_errors': sorted(error_types.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        }
        
        prompt = f"""Based on the following aggregated error data, provide a comprehensive analysis:

{json.dumps(summary_data, indent=2)}

Provide a JSON response with:
{{
    "overall_severity": "Critical|High|Medium|Low",
    "primary_issue_category": "Network|Database|Security|Resource|Code|General",
    "key_findings": ["finding1", "finding2", "finding3"],
    "recommended_actions": ["action1", "action2", "action3"],
    "risk_assessment": "Brief risk assessment"
}}

Return ONLY valid JSON."""

        try:
            messages = [
                SystemMessage(content="You are an expert DevOps analyst. Always respond with valid JSON only."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            result_text = response.content.strip()
            
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            return json.loads(result_text)
            
        except Exception as e:
            return {
                'overall_severity': 'Medium',
                'primary_issue_category': 'General',
                'key_findings': ['Analysis completed with errors'],
                'recommended_actions': ['Review logs manually'],
                'risk_assessment': f'Analysis error: {str(e)}'
            }

