# core/knowledge_crawler.py
# Autonomous agent to crawl and build financial knowledge base

from typing import List, Dict
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class FinancialKnowledgeCrawler:
    """
    Autonomous agent to crawl and build financial knowledge base.
    
    Crawls:
    - Tax laws and regulations
    - Investment strategies
    - Insurance guides
    - Loan information
    - Financial planning advice
    
    Note: Requires TAVILY_API_KEY for web search (optional)
    """
    
    def __init__(self, openai_api_key: str, tavily_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.tavily_api_key = tavily_api_key
        
        # Initialize search tool if available
        if tavily_api_key:
            try:
                from langchain_community.tools import TavilySearchResults
                self.search_tool = TavilySearchResults(
                    api_key=tavily_api_key,
                    max_results=5
                )
            except:
                print("Warning: Tavily not available, using fallback")
                self.search_tool = None
        else:
            self.search_tool = None
    
    def crawl_tax_laws(self, region: str = "India") -> List[Dict]:
        """Crawl tax laws and regulations for region."""
        queries = [
            f"{region} income tax rates {datetime.now().year}",
            f"{region} tax deductions and exemptions",
            f"{region} capital gains tax rules",
            f"{region} tax saving investment options"
        ]
        
        return self._crawl_queries(queries, "taxation", region)
    
    def crawl_investment_strategies(self, region: str = "India") -> List[Dict]:
        """Crawl investment strategies and guides."""
        queries = [
            f"{region} mutual fund investment guide",
            f"{region} stock market investing basics",
            f"{region} retirement planning strategies",
            f"{region} SIP investment benefits"
        ]
        
        return self._crawl_queries(queries, "investment", region)
    
    def crawl_insurance_info(self, region: str = "India") -> List[Dict]:
        """Crawl insurance guides and information."""
        queries = [
            f"{region} term insurance buying guide",
            f"{region} health insurance coverage details",
            f"{region} life insurance types comparison"
        ]
        
        return self._crawl_queries(queries, "insurance", region)
    
    def crawl_loan_information(self, region: str = "India") -> List[Dict]:
        """Crawl loan and debt management information."""
        queries = [
            f"{region} home loan eligibility criteria",
            f"{region} personal loan interest rates",
            f"loan prepayment vs investment decision"
        ]
        
        return self._crawl_queries(queries, "debt", region)
    
    def crawl_financial_planning(self, region: str = "India") -> List[Dict]:
        """Crawl financial planning guides."""
        queries = [
            f"{region} retirement planning guide",
            f"{region} emergency fund recommendations",
            f"financial planning for {region} families"
        ]
        
        return self._crawl_queries(queries, "financial_planning", region)
    
    def build_complete_knowledge_base(self, region: str = "India") -> Dict[str, List[Dict]]:
        """
        Crawl ALL categories and build complete knowledge base.
        This runs autonomously and takes 30-60 minutes.
        """
        print(f"Building knowledge base for {region}...")
        
        knowledge_base = {
            'tax_laws': self.crawl_tax_laws(region),
            'investment_strategies': self.crawl_investment_strategies(region),
            'insurance_info': self.crawl_insurance_info(region),
            'loan_information': self.crawl_loan_information(region),
            'financial_planning': self.crawl_financial_planning(region)
        }
        
        total_docs = sum(len(docs) for docs in knowledge_base.values())
        print(f"\nKnowledge base built! Total documents: {total_docs}")
        
        return knowledge_base
    
    def _crawl_queries(self, queries: List[str], category: str, region: str) -> List[Dict]:
        """Crawl multiple queries and return documents."""
        documents = []
        
        for query in queries:
            print(f"Searching: {query}")
            results = self._web_search(query)
            
            for result in results:
                content = self._extract_content(result.get('url', ''))
                
                if content:
                    documents.append({
                        'content': content,
                        'title': result.get('title', ''),
                        'source': result.get('url', ''),
                        'category': category,
                        'region': region,
                        'query': query,
                        'crawled_at': datetime.now().isoformat()
                    })
        
        return documents
    
    def _web_search(self, query: str) -> List[Dict]:
        """Search web using Tavily or fallback."""
        if self.search_tool:
            try:
                results = self.search_tool.invoke(query)
                return results if isinstance(results, list) else []
            except Exception as e:
                print(f"Search error: {e}")
                return []
        else:
            # No search available
            print("Warning: No search API available. Please configure TAVILY_API_KEY.")
            return []
    
    def _extract_content(self, url: str, max_length: int = 5000) -> str:
        """Extract text content from URL."""
        if not url:
            return ""
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:max_length] if len(text) > max_length else text
            
        except Exception as e:
            print(f"Error extracting from {url}: {e}")
            return ""
