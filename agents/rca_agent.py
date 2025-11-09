"""
Root Cause Analysis (RCA) Agent
Performs formal root cause analysis with structured methodology
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from config import Config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RCAAgent(BaseAgent):
    """Agent responsible for formal Root Cause Analysis"""
    
    def __init__(self, api_key: str = None):
        super().__init__(name="RCA Agent", api_key=api_key)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform formal Root Cause Analysis
        
        Args:
            input_data: Dict with 'issues_found', 'remediations', and 'log_analysis'
            
        Returns:
            Dict with complete RCA report
        """
        self.status = "processing"
        self.log_action("Starting Root Cause Analysis")
        
        try:
            issues = input_data.get("issues_found", [])
            remediations = input_data.get("remediations", [])
            log_analysis = input_data.get("log_analysis", {})
            
            if not issues:
                return {
                    "success": True,
                    "agent": self.name,
                    "message": "No issues to analyze",
                    "rca_report": None
                }
            
            # Perform comprehensive RCA
            rca_report = await self._generate_rca_report(issues, remediations, log_analysis)
            
            self.status = "completed"
            self.log_action("RCA report generated")
            
            return {
                "success": True,
                "agent": self.name,
                "rca_report": rca_report,
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
    
    async def _generate_rca_report(
        self, 
        issues: List[Dict], 
        remediations: List[Dict],
        log_analysis: Dict
    ) -> Dict[str, Any]:
        """Generate comprehensive RCA report"""
        
        # Get critical and error issues
        critical_issues = [i for i in issues if i["severity"] == "CRITICAL"]
        error_issues = [i for i in issues if i["severity"] == "ERROR"]
        
        # Basic RCA structure
        rca = {
            "metadata": {
                "incident_id": f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "analysis_date": datetime.now().isoformat(),
                "analyzer": "Multi-Agent DevOps Incident Suite",
                "total_issues": len(issues),
                "critical_count": len(critical_issues),
                "error_count": len(error_issues)
            },
            "executive_summary": "",
            "problem_statement": "",
            "timeline": [],
            "five_whys": {},
            "root_causes": [],
            "contributing_factors": [],
            "impact_assessment": {},
            "immediate_actions": [],
            "preventive_measures": [],
            "lessons_learned": []
        }
        
        # Generate enhanced analysis using LLM if available
        if self.llm:
            try:
                rca = await self._llm_enhanced_rca(rca, issues, remediations, log_analysis)
            except Exception as e:
                logger.error(f"LLM enhancement failed: {e}")
                # Fall back to rule-based analysis
                rca = self._rule_based_rca(rca, issues, remediations, log_analysis)
        else:
            # Rule-based analysis
            rca = self._rule_based_rca(rca, issues, remediations, log_analysis)
        
        return rca
    
    async def _llm_enhanced_rca(
        self,
        rca: Dict,
        issues: List[Dict],
        remediations: List[Dict],
        log_analysis: Dict
    ) -> Dict[str, Any]:
        """Use LLM to generate comprehensive RCA"""
        
        # Prepare context
        issues_text = "\n".join([
            f"- [{i['severity']}] {i['category']}: {i['message']}"
            for i in issues[:15]
        ])
        
        # Executive Summary
        summary_prompt = f"""As a senior DevOps engineer, provide a concise executive summary for this incident:

Issues Found:
{issues_text}

Total Issues: {len(issues)} ({rca['metadata']['critical_count']} CRITICAL, {rca['metadata']['error_count']} ERRORS)

Provide a 2-3 sentence executive summary highlighting the most critical aspects and overall impact."""

        summary_response = self.llm.invoke(summary_prompt)
        rca["executive_summary"] = summary_response.content.strip()
        
        # Problem Statement
        problem_prompt = f"""Create a clear problem statement for this incident:

Issues:
{issues_text}

Provide a single, clear problem statement (1-2 sentences) that describes what went wrong."""

        problem_response = self.llm.invoke(problem_prompt)
        rca["problem_statement"] = problem_response.content.strip()
        
        # Five Whys Analysis (for primary issue)
        if issues:
            primary_issue = issues[0]
            whys_prompt = f"""Perform a "5 Whys" root cause analysis for this issue:

Issue: {primary_issue['message']}
Category: {primary_issue['category']}
Severity: {primary_issue['severity']}

Provide exactly 5 "Why" questions and answers to drill down to the root cause.
Format as:
Why 1: [question]
Answer: [answer]
Why 2: [question]
Answer: [answer]
... (continue for all 5)"""

            whys_response = self.llm.invoke(whys_prompt)
            rca["five_whys"] = {
                "primary_issue": primary_issue['message'],
                "analysis": whys_response.content.strip()
            }
        
        # Root Causes
        root_causes_prompt = f"""Identify the root causes for these incidents:

{issues_text}

List 3-5 distinct root causes. For each, provide:
1. Root cause description
2. Evidence from logs
3. How it led to the incident

Format as a clear list."""

        root_causes_response = self.llm.invoke(root_causes_prompt)
        rca["root_causes"] = self._parse_root_causes(root_causes_response.content)
        
        # Contributing Factors
        factors_prompt = f"""Identify contributing factors that made this incident worse or allowed it to happen:

Issues: {issues_text}

List 3-5 contributing factors (not root causes, but things that contributed).
Examples: monitoring gaps, configuration issues, resource constraints, etc."""

        factors_response = self.llm.invoke(factors_prompt)
        rca["contributing_factors"] = self._parse_list_items(factors_response.content)
        
        # Impact Assessment
        impact_prompt = f"""Assess the impact of this incident:

Issues: {issues_text}

Provide:
1. User Impact (how users were affected)
2. Business Impact (revenue, reputation, etc.)
3. Technical Impact (systems affected)
4. Duration (estimated)
5. Severity Level (P1-P4)"""

        impact_response = self.llm.invoke(impact_prompt)
        rca["impact_assessment"] = self._parse_impact_assessment(impact_response.content)
        
        # Immediate Actions (from remediations)
        if remediations:
            immediate_actions = []
            for rem in remediations[:5]:
                immediate_actions.append({
                    "action": f"Address {rem['issue']['category']} issue",
                    "priority": rem['issue']['severity'],
                    "details": rem['remediation_plan'][:200] + "..."
                })
            rca["immediate_actions"] = immediate_actions
        
        # Preventive Measures
        preventive_prompt = f"""Based on this incident, suggest preventive measures to avoid similar issues:

Issues: {issues_text}

Provide 5-7 specific preventive measures including:
- Monitoring improvements
- Process changes
- Technical improvements
- Training needs

Format as actionable items."""

        preventive_response = self.llm.invoke(preventive_prompt)
        rca["preventive_measures"] = self._parse_list_items(preventive_response.content)
        
        # Lessons Learned
        lessons_prompt = f"""What are the key lessons learned from this incident?

Issues: {issues_text}

Provide 3-5 specific lessons learned that the team should remember."""

        lessons_response = self.llm.invoke(lessons_prompt)
        rca["lessons_learned"] = self._parse_list_items(lessons_response.content)
        
        # Timeline
        rca["timeline"] = self._extract_timeline(issues)
        
        return rca
    
    def _rule_based_rca(
        self,
        rca: Dict,
        issues: List[Dict],
        remediations: List[Dict],
        log_analysis: Dict
    ) -> Dict[str, Any]:
        """Generate RCA using rule-based analysis (when LLM not available)"""
        
        # Executive Summary
        critical_count = rca['metadata']['critical_count']
        error_count = rca['metadata']['error_count']
        rca["executive_summary"] = f"Incident involving {len(issues)} issues detected. {critical_count} critical issues and {error_count} errors identified across multiple system components. Immediate attention required for critical infrastructure components."
        
        # Problem Statement
        categories = set(i['category'] for i in issues)
        rca["problem_statement"] = f"Multiple system failures detected across {', '.join(categories)} components, resulting in service degradation and potential data loss."
        
        # Root Causes (rule-based)
        root_causes = []
        category_groups = {}
        for issue in issues:
            cat = issue['category']
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append(issue)
        
        for category, cat_issues in category_groups.items():
            if cat_issues:
                root_causes.append({
                    "cause": f"{category.capitalize()} system failure",
                    "evidence": f"Multiple {category} errors detected: {cat_issues[0]['message'][:100]}",
                    "impact": f"{len(cat_issues)} related incidents"
                })
        
        rca["root_causes"] = root_causes[:5]
        
        # Contributing Factors
        rca["contributing_factors"] = [
            "Insufficient monitoring coverage",
            "Lack of automated alerting",
            "Resource capacity constraints",
            "Configuration management gaps"
        ]
        
        # Impact Assessment
        rca["impact_assessment"] = {
            "user_impact": "Service degradation affecting end users",
            "business_impact": "Potential revenue loss and reputation damage",
            "technical_impact": f"{len(set(i['category'] for i in issues))} system components affected",
            "duration": "Ongoing - immediate action required",
            "severity": "P1" if critical_count > 0 else "P2"
        }
        
        # Immediate Actions
        rca["immediate_actions"] = [
            {
                "action": f"Resolve {i['category']} issue",
                "priority": i['severity'],
                "details": i['message']
            }
            for i in issues[:5]
        ]
        
        # Preventive Measures
        rca["preventive_measures"] = [
            "Implement comprehensive monitoring for all critical systems",
            "Set up automated alerting with escalation procedures",
            "Conduct regular capacity planning reviews",
            "Establish configuration management best practices",
            "Implement automated health checks",
            "Create incident response playbooks",
            "Schedule regular disaster recovery drills"
        ]
        
        # Lessons Learned
        rca["lessons_learned"] = [
            "Early detection systems are critical for incident prevention",
            "Multiple simultaneous failures indicate systemic issues",
            "Automated remediation can reduce incident response time",
            "Cross-functional collaboration improves incident resolution"
        ]
        
        # Timeline
        rca["timeline"] = self._extract_timeline(issues)
        
        return rca
    
    def _extract_timeline(self, issues: List[Dict]) -> List[Dict]:
        """Extract timeline of events from issues"""
        timeline = []
        for issue in sorted(issues, key=lambda x: x.get('timestamp', '')):
            timeline.append({
                "timestamp": issue.get('timestamp', 'Unknown'),
                "event": issue['message'][:100],
                "severity": issue['severity'],
                "category": issue['category']
            })
        return timeline
    
    def _parse_root_causes(self, llm_output: str) -> List[Dict]:
        """Parse root causes from LLM output"""
        causes = []
        lines = llm_output.strip().split('\n')
        current_cause = {}
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                if current_cause:
                    causes.append(current_cause)
                current_cause = {"cause": line.lstrip('0123456789.-* '), "evidence": "", "impact": ""}
            elif line and current_cause:
                if not current_cause["evidence"]:
                    current_cause["evidence"] = line
                else:
                    current_cause["impact"] = line
        
        if current_cause:
            causes.append(current_cause)
        
        return causes[:5] if causes else [{"cause": llm_output[:200], "evidence": "See analysis", "impact": "Multiple systems"}]
    
    def _parse_list_items(self, llm_output: str) -> List[str]:
        """Parse list items from LLM output"""
        items = []
        for line in llm_output.strip().split('\n'):
            line = line.strip().lstrip('0123456789.-* ')
            if line and len(line) > 10:
                items.append(line)
        return items[:10] if items else [llm_output.strip()]
    
    def _parse_impact_assessment(self, llm_output: str) -> Dict[str, str]:
        """Parse impact assessment from LLM output"""
        impact = {
            "user_impact": "",
            "business_impact": "",
            "technical_impact": "",
            "duration": "",
            "severity": ""
        }
        
        lines = llm_output.strip().split('\n')
        current_key = None
        
        for line in lines:
            line = line.strip()
            lower_line = line.lower()
            
            if "user" in lower_line and "impact" in lower_line:
                current_key = "user_impact"
            elif "business" in lower_line and "impact" in lower_line:
                current_key = "business_impact"
            elif "technical" in lower_line and "impact" in lower_line:
                current_key = "technical_impact"
            elif "duration" in lower_line:
                current_key = "duration"
            elif "severity" in lower_line:
                current_key = "severity"
            elif current_key and line:
                impact[current_key] += " " + line.lstrip(':-')
        
        # Clean up
        for key in impact:
            impact[key] = impact[key].strip() or "Not assessed"
        
        return impact

