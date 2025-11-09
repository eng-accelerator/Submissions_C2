"""
Cookbook Synthesizer Agent
Creates actionable checklists and incident playbooks
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from config import Config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CookbookAgent(BaseAgent):
    """Agent responsible for creating reusable incident playbooks"""
    
    def __init__(self, api_key: str = None):
        super().__init__(name="Cookbook Agent", api_key=api_key)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create incident playbook/cookbook
        
        Args:
            input_data: Dict with 'remediations' and 'summary'
            
        Returns:
            Dict with cookbook/playbook
        """
        self.status = "processing"
        self.log_action("Starting cookbook synthesis")
        
        try:
            remediations = input_data.get("remediations", [])
            summary = input_data.get("summary", "")
            
            if not remediations:
                return {
                    "success": True,
                    "agent": self.name,
                    "message": "No remediations to create cookbook from",
                    "cookbook": None
                }
            
            # Generate structured cookbook
            cookbook = await self._create_cookbook(remediations, summary)
            
            # Save cookbook
            self._save_cookbook(cookbook)
            
            self.status = "completed"
            self.log_action("Cookbook created successfully")
            
            return {
                "success": True,
                "agent": self.name,
                "cookbook": cookbook,
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
    
    async def _create_cookbook(self, remediations: List[Dict], summary: str) -> Dict[str, Any]:
        """Create a structured cookbook from remediations"""
        
        # Group by category
        categories = {}
        for rem in remediations:
            category = rem["issue"]["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(rem)
        
        # Create playbook sections
        playbook_sections = []
        
        for category, items in categories.items():
            section = {
                "category": category.upper(),
                "issue_count": len(items),
                "checklists": []
            }
            
            for item in items:
                checklist = self._create_checklist(item)
                section["checklists"].append(checklist)
            
            playbook_sections.append(section)
        
        # Generate enhanced playbook using LLM if available
        enhanced_summary = summary
        if self.llm:
            try:
                enhanced_summary = await self._generate_enhanced_summary(remediations, summary)
            except Exception as e:
                logger.warning(f"Failed to enhance summary: {e}")
        
        cookbook = {
            "title": f"Incident Response Playbook - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now().isoformat(),
            "summary": enhanced_summary,
            "total_issues": len(remediations),
            "categories_affected": list(categories.keys()),
            "playbook_sections": playbook_sections,
            "quick_reference": self._create_quick_reference(remediations)
        }
        
        return cookbook
    
    def _create_checklist(self, remediation: Dict[str, Any]) -> Dict[str, Any]:
        """Create actionable checklist from remediation"""
        issue = remediation["issue"]
        plan = remediation["remediation_plan"]
        
        # Extract steps from plan (simple extraction)
        steps = []
        for line in plan.split('\n'):
            line = line.strip()
            # Look for numbered items or bullet points
            if line and (line[0].isdigit() or line.startswith(('-', '*', '•'))):
                # Clean up the step
                step = line.lstrip('0123456789.-*• ')
                if step:
                    steps.append(step)
        
        # If no steps found, create generic ones
        if not steps:
            steps = [
                f"Investigate {issue['category']} issue",
                "Review relevant logs and metrics",
                "Apply recommended fix",
                "Verify resolution",
                "Document outcome"
            ]
        
        return {
            "issue_type": issue["category"],
            "severity": issue["severity"],
            "trigger": issue["message"][:100],
            "steps": steps[:10],  # Limit to 10 steps
            "confidence": remediation["confidence"]
        }
    
    def _create_quick_reference(self, remediations: List[Dict]) -> Dict[str, Any]:
        """Create quick reference guide"""
        
        # Count by severity
        severity_counts = {}
        category_counts = {}
        
        for rem in remediations:
            severity = rem["issue"]["severity"]
            category = rem["issue"]["category"]
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Top issues
        top_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            "severity_breakdown": severity_counts,
            "top_affected_categories": [cat for cat, _ in top_categories],
            "total_remediations": len(remediations),
            "recommended_priority": "CRITICAL" if "CRITICAL" in severity_counts else "HIGH"
        }
    
    async def _generate_enhanced_summary(self, remediations: List[Dict], base_summary: str) -> str:
        """Generate enhanced summary using LLM"""
        try:
            # Prepare context
            issues_text = "\n".join([
                f"- {rem['issue']['severity']}: {rem['issue']['category']} - {rem['issue']['message'][:80]}"
                for rem in remediations[:10]
            ])
            
            prompt = f"""Based on these incidents, create an enhanced executive summary for an incident playbook:

{base_summary}

Key Issues:
{issues_text}

Provide a comprehensive 3-4 sentence summary that:
1. Highlights the overall incident pattern
2. Notes the most critical areas
3. Suggests preventive measures
4. Sets priority level

Keep it professional and actionable."""

            response = self.llm.invoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Enhanced summary generation failed: {e}")
            return base_summary
    
    def _save_cookbook(self, cookbook: Dict[str, Any]):
        """Save cookbook to file for future reference"""
        try:
            import json
            
            filename = f"incident_playbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = Config.BASE_DIR / "cookbooks" / filename
            
            # Create directory if needed
            filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(cookbook, f, indent=2)
            
            logger.info(f"Cookbook saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save cookbook: {e}")

