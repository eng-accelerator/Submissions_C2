"""
Remediation Agent with RAG
Maps detected issues to fixes and provides rationale using knowledge base
"""
from typing import Dict, Any, List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .base_agent import BaseAgent
from config import Config
import logging
import os

logger = logging.getLogger(__name__)


class RemediationAgent(BaseAgent):
    """Agent responsible for finding remediation solutions using RAG"""
    
    def __init__(self, api_key: str = None):
        super().__init__(name="Remediation Agent", api_key=api_key)
        self.embeddings = self._initialize_embeddings()
        self.vector_store = None
        self._load_knowledge_base()
    
    def _initialize_embeddings(self) -> Optional[HuggingFaceEmbeddings]:
        """Initialize embedding model"""
        try:
            return HuggingFaceEmbeddings(
                model_name=Config.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'}
            )
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            return None
    
    def _load_knowledge_base(self):
        """Load or create knowledge base from documents"""
        vector_store_path = Config.VECTOR_STORE_DIR / "remediation_kb.faiss"
        
        try:
            # Try to load existing vector store
            if vector_store_path.exists():
                self.vector_store = FAISS.load_local(
                    str(Config.VECTOR_STORE_DIR / "remediation_kb"),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Loaded existing knowledge base")
            else:
                # Create from default knowledge
                self._create_default_knowledge_base()
                
        except Exception as e:
            logger.warning(f"Failed to load knowledge base: {e}")
            self._create_default_knowledge_base()
    
    def _create_default_knowledge_base(self):
        """Create a default knowledge base with common DevOps issues"""
        knowledge_docs = [
            {
                "issue": "Database Connection Timeout",
                "category": "database",
                "solution": "1. Check database server status\n2. Verify network connectivity\n3. Review connection pool settings\n4. Check for long-running queries\n5. Increase timeout settings if necessary",
                "rationale": "Connection timeouts typically occur due to network issues, overloaded database, or exhausted connection pools."
            },
            {
                "issue": "Out of Memory Error",
                "category": "memory",
                "solution": "1. Identify memory-intensive processes\n2. Review application memory leaks\n3. Increase heap size allocation\n4. Enable garbage collection logging\n5. Scale horizontally if needed",
                "rationale": "OOM errors indicate insufficient memory allocation or memory leaks. Monitoring and profiling are essential."
            },
            {
                "issue": "High CPU Usage",
                "category": "cpu",
                "solution": "1. Identify CPU-intensive processes\n2. Check for infinite loops or stuck threads\n3. Review algorithmic efficiency\n4. Enable CPU profiling\n5. Consider load balancing",
                "rationale": "High CPU usage can be caused by inefficient code, excessive load, or runaway processes."
            },
            {
                "issue": "Disk Space Full",
                "category": "disk",
                "solution": "1. Identify large files and logs\n2. Clean up old logs and temporary files\n3. Set up log rotation\n4. Expand disk capacity\n5. Archive old data",
                "rationale": "Running out of disk space can cause system instability. Regular cleanup and monitoring are crucial."
            },
            {
                "issue": "Network Connection Refused",
                "category": "network",
                "solution": "1. Verify service is running\n2. Check firewall rules\n3. Validate port configuration\n4. Review service health checks\n5. Check network connectivity",
                "rationale": "Connection refused errors indicate the service is not listening on the expected port or network issues exist."
            },
            {
                "issue": "Authentication Failed",
                "category": "security",
                "solution": "1. Verify credentials are correct\n2. Check token expiration\n3. Review permission settings\n4. Validate authentication service status\n5. Check certificate validity",
                "rationale": "Authentication failures can result from expired credentials, misconfigured permissions, or service outages."
            },
            {
                "issue": "Null Pointer Exception",
                "category": "application",
                "solution": "1. Review stack trace for exact location\n2. Add null checks in code\n3. Validate input parameters\n4. Review recent code changes\n5. Add defensive programming practices",
                "rationale": "Null pointer exceptions indicate missing data validation. Proper error handling prevents cascading failures."
            },
            {
                "issue": "HTTP 500 Internal Server Error",
                "category": "application",
                "solution": "1. Check application logs for exceptions\n2. Review recent deployments\n3. Verify configuration settings\n4. Check database connectivity\n5. Review upstream service dependencies",
                "rationale": "500 errors indicate server-side failures. Logs and monitoring provide insights into root causes."
            },
            {
                "issue": "HTTP 503 Service Unavailable",
                "category": "network",
                "solution": "1. Check service health status\n2. Review load balancer configuration\n3. Verify autoscaling settings\n4. Check for resource exhaustion\n5. Review circuit breaker status",
                "rationale": "503 errors indicate temporary unavailability. Often related to overload or maintenance."
            },
            {
                "issue": "DNS Resolution Failed",
                "category": "network",
                "solution": "1. Verify DNS server status\n2. Check DNS configuration\n3. Review /etc/hosts file\n4. Test with nslookup/dig\n5. Check network connectivity to DNS",
                "rationale": "DNS failures prevent service discovery. Proper DNS configuration is critical for distributed systems."
            }
        ]
        
        # Convert to documents
        texts = []
        for doc in knowledge_docs:
            text = f"""Issue: {doc['issue']}
Category: {doc['category']}
Solution:
{doc['solution']}

Rationale: {doc['rationale']}
"""
            texts.append(text)
        
        # Create vector store
        if self.embeddings and texts:
            try:
                self.vector_store = FAISS.from_texts(
                    texts,
                    self.embeddings
                )
                # Save for future use
                self.vector_store.save_local(
                    str(Config.VECTOR_STORE_DIR / "remediation_kb")
                )
                logger.info("Created default knowledge base")
            except Exception as e:
                logger.error(f"Failed to create knowledge base: {e}")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find remediation solutions for detected issues
        
        Args:
            input_data: Dict with 'issues_found' from LogReaderAgent
            
        Returns:
            Dict with remediation recommendations
        """
        self.status = "processing"
        self.log_action("Starting remediation analysis")
        
        try:
            issues = input_data.get("issues_found", [])
            
            if not issues:
                return {
                    "success": True,
                    "agent": self.name,
                    "message": "No issues to remediate",
                    "remediations": []
                }
            
            # Find remediations for each issue
            remediations = []
            for issue in issues[:10]:  # Limit to top 10 critical issues
                remediation = await self._find_remediation(issue)
                if remediation:
                    remediations.append(remediation)
            
            self.status = "completed"
            self.log_action(f"Generated {len(remediations)} remediation plans")
            
            return {
                "success": True,
                "agent": self.name,
                "total_issues": len(issues),
                "remediations": remediations,
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
    
    async def _find_remediation(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find remediation for a specific issue using RAG"""
        try:
            # Create query from issue
            query = f"{issue['category']} {issue['severity']} {issue['message']}"
            
            # Retrieve relevant knowledge
            relevant_docs = []
            if self.vector_store:
                try:
                    relevant_docs = self.vector_store.similarity_search(
                        query,
                        k=Config.TOP_K_RESULTS
                    )
                except Exception as e:
                    logger.warning(f"Vector search failed: {e}")
            
            # Generate remediation using LLM with context
            if self.llm:
                context = "\n\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else "No specific knowledge available."
                
                prompt = f"""You are a DevOps expert. Given this incident and relevant knowledge, provide a clear remediation plan.

**Incident Details:**
- Severity: {issue['severity']}
- Category: {issue['category']}
- Message: {issue['message']}
- Timestamp: {issue.get('timestamp', 'Unknown')}

**Relevant Knowledge:**
{context}

Provide:
1. **Root Cause**: Brief explanation (1-2 sentences)
2. **Immediate Action**: What to do right now (3-5 steps)
3. **Long-term Fix**: Prevent recurrence (2-3 points)
4. **Priority**: Critical/High/Medium/Low

Format as clear, actionable steps."""

                response = self.llm.invoke(prompt)
                
                return {
                    "issue": issue,
                    "remediation_plan": response.content.strip(),
                    "knowledge_sources": len(relevant_docs),
                    "confidence": "high" if relevant_docs else "medium"
                }
            else:
                # Fallback without LLM
                return {
                    "issue": issue,
                    "remediation_plan": f"Manual investigation required for {issue['category']} issue: {issue['message'][:100]}",
                    "knowledge_sources": 0,
                    "confidence": "low"
                }
                
        except Exception as e:
            logger.error(f"Remediation failed for issue: {e}")
            return None

