"""
Query Validation Agent for MediScout.

Validates and refines user research queries for optimal results.
"""

from typing import Dict, Any
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from mediscout.config import get_settings
from mediscout.schemas import QueryValidation
from mediscout.state import ResearchState


VALIDATION_PROMPT = """You are a medical research query validator and optimizer.

Your task is to analyze the user's research query and:
1. Check if it's related to medical/health topics (BE LENIENT - accept anything health/medical/biology related)
2. Refine it for better search results (fix spelling, expand abbreviations, add medical context)
3. Extract key medical terms
4. Provide suggestions if the query is unclear

IMPORTANT: 
- Accept queries about medical documents, papers, research
- Accept anatomy topics (eyes, heart, brain, etc.)
- Accept biology and health-related questions
- ONLY reject completely non-medical topics (e.g., "best pizza recipe", "stock market")

Original query: {query}

Respond in JSON format:
{{
    "is_valid": true/false,
    "refined_query": "improved query text",
    "medical_terms": ["term1", "term2"],
    "suggestions": ["suggestion1 if needed"]
}}

Keep the refined query concise but specific. Extract important medical terms like drugs, diseases, procedures, anatomy.
"""


class ValidateQueryAgent:
    """Agent for validating and refining research queries."""
    
    def __init__(self):
        """Initialize the validation agent."""
        self.settings = get_settings()
        
        # Use the configured model from settings (works with your OpenRouter account)
        # This avoids issues with free model availability
        
        # Initialize LLM with OpenRouter
        self.llm = ChatOpenAI(
            model=self.settings.openrouter_model,
            temperature=0.0,
            api_key=self.settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=10  # 10 second timeout
        )
        
        self.prompt = ChatPromptTemplate.from_template(VALIDATION_PROMPT)
        self.parser = JsonOutputParser()
        
        self.chain = self.prompt | self.llm | self.parser
        
        logger.info("Query Validation Agent initialized")
    
    def __call__(self, state: ResearchState) -> Dict[str, Any]:
        """
        Validate and refine the research query.
        
        Args:
            state: Current research state
            
        Returns:
            Updated state with validation results
        """
        query = state["research_topic"]
        search_scope = state.get("search_scope", "local_and_pubmed")
        logger.info(f"Validating query: '{query}' (scope: {search_scope})")
        
        # Skip strict validation for local-only searches (user's own documents)
        if search_scope == "local_only":
            logger.info("⚡ Skipping validation for local-only search")
            return {
                "query_validation": QueryValidation(
                    is_valid=True,
                    refined_query=query,
                    medical_terms=[],
                    suggestions=[]
                ),
                "refined_query": query,
                "current_stage": "query_validated"
            }
        
        # FAST PATH: Auto-accept queries with medical/document keywords
        medical_keywords = [
            'document', 'paper', 'study', 'research', 'patient', 'disease', 
            'treatment', 'drug', 'therapy', 'medical', 'clinical', 'symptom',
            'diagnosis', 'eye', 'heart', 'brain', 'cancer', 'diabetes',
            'surgery', 'medication', 'health', 'gene', 'protein', 'cell',
            'tissue', 'organ', 'blood', 'infection', 'virus', 'bacteria'
        ]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in medical_keywords):
            logger.info(f"⚡ FAST PATH: Query contains medical keywords, skipping LLM validation")
            return {
                "query_validation": QueryValidation(
                    is_valid=True,
                    refined_query=query,
                    medical_terms=[],
                    suggestions=[]
                ),
                "refined_query": query,
                "current_stage": "query_validated"
            }
        
        try:
            # Run validation chain (only for ambiguous queries)
            logger.info("Running LLM validation...")
            result = self.chain.invoke({"query": query})
            
            validation = QueryValidation(
                is_valid=result.get("is_valid", True),
                refined_query=result.get("refined_query", query),
                medical_terms=result.get("medical_terms", []),
                suggestions=result.get("suggestions", [])
            )
            
            logger.info(f"Validation complete. Refined: '{validation.refined_query}'")
            
            # Check if query is valid - raise error for non-medical queries (only for PubMed searches)
            if not validation.is_valid:
                error_msg = (
                    f"❌ Invalid research query: This doesn't appear to be a medical research question.\n\n"
                    f"Original query: '{query}'\n\n"
                    f"Suggestions:\n" + "\n".join([f"  • {s}" for s in validation.suggestions])
                    if validation.suggestions else 
                    f"Please rephrase your question to focus on medical topics like:\n"
                    f"  • Diseases, conditions, or symptoms\n"
                    f"  • Treatments, medications, or therapies\n"
                    f"  • Medical procedures or diagnostics\n"
                    f"  • Clinical studies or evidence"
                )
                logger.warning(f"Non-medical query detected: {query}")
                
                return {
                    "query_validation": validation,
                    "refined_query": query,
                    "current_stage": "validation_failed",
                    "error_message": error_msg,
                    "final_report_markdown": self._create_validation_error_report(query, validation)
                }
            
            return {
                "query_validation": validation,
                "refined_query": validation.refined_query,
                "current_stage": "query_validated"
            }
        
        except Exception as e:
            logger.error(f"Query validation failed: {e}")
            # Fallback: use original query (assume valid to avoid blocking)
            return {
                "query_validation": QueryValidation(
                    is_valid=True,
                    refined_query=query,
                    medical_terms=[],
                    suggestions=[]
                ),
                "refined_query": query,
                "current_stage": "query_validated"
            }
    
    def _create_validation_error_report(self, query: str, validation: QueryValidation) -> str:
        """Create error report for invalid queries."""
        suggestions_text = "\n".join([f"- {s}" for s in validation.suggestions]) if validation.suggestions else "No specific suggestions provided."
        
        return f"""# Research Query Validation Failed

## ❌ Invalid Query

**Your query:** "{query}"

**Issue:** This does not appear to be a valid medical research question.

## 💡 Suggestions

{suggestions_text}

## ✅ Valid Medical Research Questions

MediScout is designed to help with medical research queries such as:

- **Treatment efficacy**: "What are the current treatment options for Type 2 Diabetes?"
- **Disease information**: "What are the early biomarkers for Alzheimer's disease?"
- **Drug effectiveness**: "What is the efficacy of metformin for diabetes prevention?"
- **Clinical evidence**: "What does recent evidence show about mRNA vaccine safety?"
- **Diagnostic methods**: "What are the latest diagnostic methods for pancreatic cancer?"

## 📋 Tips for Better Queries

1. **Be specific** about the medical condition or treatment
2. **Include medical terminology** when possible
3. **Focus on evidence-based questions** rather than general health advice
4. **Specify populations** if relevant (e.g., "in elderly patients")

## 🔄 Try Again

Please rephrase your question to focus on a medical research topic, and we'll be happy to help you find relevant evidence!

---
**Generated by:** MediScout AI Research Assistant  
**Status:** Query Validation Failed
"""

