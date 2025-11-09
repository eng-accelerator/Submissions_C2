"""
Log Reader/Classifier Agent
Parses, categorizes, and extracts fields from operational logs
"""
from typing import Dict, Any, List
import re
from datetime import datetime
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class LogReaderAgent(BaseAgent):
    """Agent responsible for reading and classifying log entries"""
    
    def __init__(self, api_key: str = None):
        super().__init__(name="Log Reader Agent", api_key=api_key)
        self.severity_patterns = {
            "CRITICAL": r"\b(critical|fatal|panic|emergency)\b",
            "ERROR": r"\b(error|err|exception|failed|failure)\b",
            "WARNING": r"\b(warning|warn|deprecated)\b",
            "INFO": r"\b(info|information|notice)\b",
            "DEBUG": r"\b(debug|trace|verbose)\b"
        }
        
        self.issue_categories = {
            "database": ["connection", "query", "timeout", "deadlock", "schema"],
            "network": ["timeout", "refused", "unreachable", "latency", "dns"],
            "memory": ["oom", "memory", "heap", "stack", "allocation"],
            "disk": ["disk", "storage", "space", "inode", "filesystem"],
            "cpu": ["cpu", "load", "throttling", "performance"],
            "security": ["auth", "permission", "unauthorized", "forbidden", "ssl"],
            "application": ["null", "exception", "crash", "segfault", "assertion"]
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and classify logs
        
        Args:
            input_data: Dict with 'logs' key containing raw log text
            
        Returns:
            Dict with parsed and classified log entries
        """
        self.status = "processing"
        self.log_action("Starting log analysis")
        
        try:
            raw_logs = input_data.get("logs", "")
            
            if not raw_logs:
                return {
                    "success": False,
                    "error": "No logs provided",
                    "agent": self.name
                }
            
            # Parse log entries
            log_entries = self._parse_logs(raw_logs)
            self.log_action(f"Parsed {len(log_entries)} log entries")
            
            # Classify each entry
            classified_logs = []
            issues_found = []
            
            for entry in log_entries:
                classified = self._classify_entry(entry)
                classified_logs.append(classified)
                
                # Track issues (ERROR and above)
                if classified["severity"] in ["ERROR", "CRITICAL"]:
                    issues_found.append({
                        "severity": classified["severity"],
                        "category": classified["category"],
                        "message": classified["message"],
                        "timestamp": classified["timestamp"],
                        "extracted_fields": classified["extracted_fields"]
                    })
            
            # Generate summary using LLM
            summary = await self._generate_summary(classified_logs, issues_found)
            
            self.status = "completed"
            self.log_action(f"Found {len(issues_found)} issues")
            
            return {
                "success": True,
                "agent": self.name,
                "total_entries": len(log_entries),
                "classified_logs": classified_logs,
                "issues_found": issues_found,
                "critical_count": sum(1 for i in issues_found if i["severity"] == "CRITICAL"),
                "error_count": sum(1 for i in issues_found if i["severity"] == "ERROR"),
                "summary": summary,
                "execution_log": self.execution_log
            }
            
        except Exception as e:
            self.status = "failed"
            self.log_action(f"Error: {str(e)}")
            logger.error(f"{self.name} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def _parse_logs(self, raw_logs: str) -> List[Dict[str, Any]]:
        """Parse raw log text into structured entries"""
        entries = []
        lines = raw_logs.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            entry = {
                "raw": line,
                "timestamp": self._extract_timestamp(line),
                "message": line
            }
            entries.append(entry)
        
        return entries
    
    def _extract_timestamp(self, log_line: str) -> str:
        """Extract timestamp from log line"""
        # Common timestamp patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',  # ISO format
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',      # Apache format
            r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}',      # Custom format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log_line)
            if match:
                return match.group()
        
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _classify_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a single log entry"""
        message_lower = entry["message"].lower()
        
        # Determine severity
        severity = "INFO"
        for sev, pattern in self.severity_patterns.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                severity = sev
                break
        
        # Determine category
        category = "general"
        for cat, keywords in self.issue_categories.items():
            if any(keyword in message_lower for keyword in keywords):
                category = cat
                break
        
        # Extract additional fields
        extracted_fields = self._extract_fields(entry["message"])
        
        return {
            **entry,
            "severity": severity,
            "category": category,
            "extracted_fields": extracted_fields
        }
    
    def _extract_fields(self, message: str) -> Dict[str, Any]:
        """Extract useful fields from log message"""
        fields = {}
        
        # Extract IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, message)
        if ips:
            fields["ip_addresses"] = ips
        
        # Extract HTTP status codes
        status_pattern = r'\b[45]\d{2}\b'
        statuses = re.findall(status_pattern, message)
        if statuses:
            fields["http_status"] = statuses
        
        # Extract error codes
        error_pattern = r'error[_ ]code[:\s]+(\w+)'
        errors = re.findall(error_pattern, message, re.IGNORECASE)
        if errors:
            fields["error_codes"] = errors
        
        # Extract service names
        service_pattern = r'service[:\s]+(\w+)'
        services = re.findall(service_pattern, message, re.IGNORECASE)
        if services:
            fields["services"] = services
        
        return fields
    
    async def _generate_summary(self, classified_logs: List[Dict], issues: List[Dict]) -> str:
        """Generate intelligent summary using LLM"""
        if not self.llm or not issues:
            return f"Analyzed {len(classified_logs)} log entries. Found {len(issues)} issues."
        
        try:
            # Prepare context for LLM
            issue_text = "\n".join([
                f"- [{i['severity']}] {i['category']}: {i['message'][:100]}"
                for i in issues[:10]  # Limit to top 10
            ])
            
            prompt = f"""Analyze these log issues and provide a brief summary:

{issue_text}

Provide a concise 2-3 sentence summary highlighting:
1. Most critical issues
2. Common patterns
3. Overall system health"""

            response = self.llm.invoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"Analyzed {len(classified_logs)} log entries. Found {len(issues)} issues requiring attention."

