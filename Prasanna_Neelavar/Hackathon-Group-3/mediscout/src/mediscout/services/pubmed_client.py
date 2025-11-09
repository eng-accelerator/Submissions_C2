"""
PubMed API client for MediScout.

Interfaces with NCBI E-utilities API to search and fetch medical literature.
"""

import time
from typing import List, Optional
from urllib.parse import urlencode

import httpx
from Bio import Entrez
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from mediscout.config import get_settings
from mediscout.schemas import Document


class PubMedClient:
    """Client for querying PubMed/NCBI databases."""
    
    def __init__(self):
        """Initialize PubMed client."""
        self.settings = get_settings()
        
        # Configure Entrez
        Entrez.email = self.settings.pubmed_email
        if hasattr(self.settings, 'pubmed_api_key') and self.settings.pubmed_api_key:
            Entrez.api_key = self.settings.pubmed_api_key
        
        self.max_results = self.settings.pubmed_max_results
        
        logger.info(f"PubMed client initialized (email: {self.settings.pubmed_email})")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def search(self, query: str, max_results: Optional[int] = None) -> List[Document]:
        """
        Search PubMed for articles matching the query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results (default from config)
            
        Returns:
            List of Document objects with PubMed articles
        """
        max_results = max_results or self.max_results
        
        logger.info(f"Searching PubMed for: '{query}' (max_results={max_results})")
        
        try:
            # Step 1: Search for article IDs
            search_handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance",
                usehistory="y"
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()
            
            id_list = search_results.get("IdList", [])
            
            if not id_list:
                logger.info("No PubMed results found")
                return []
            
            logger.info(f"Found {len(id_list)} PubMed article IDs")
            
            # Step 2: Fetch article details
            time.sleep(0.34)  # Rate limit: ~3 requests/sec without API key
            
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=id_list,
                rettype="abstract",
                retmode="xml"
            )
            articles = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            # Step 3: Parse articles into Document objects
            documents = []
            
            for article_data in articles.get('PubmedArticle', []):
                try:
                    doc = self._parse_article(article_data)
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    logger.warning(f"Failed to parse article: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(documents)} PubMed articles")
            return documents
        
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            raise
    
    def _parse_article(self, article_data: dict) -> Optional[Document]:
        """
        Parse PubMed article XML data into Document object.
        
        Args:
            article_data: Article data from Entrez
            
        Returns:
            Document object or None if parsing fails
        """
        try:
            medline = article_data.get('MedlineCitation', {})
            article = medline.get('Article', {})
            
            # Extract PMID
            pmid = str(medline.get('PMID', ''))
            if not pmid:
                return None
            
            # Extract title
            title = article.get('ArticleTitle', 'No title')
            
            # Extract abstract
            abstract_data = article.get('Abstract', {})
            abstract_texts = abstract_data.get('AbstractText', [])
            
            if isinstance(abstract_texts, list):
                abstract = " ".join([str(text) for text in abstract_texts])
            else:
                abstract = str(abstract_texts)
            
            if not abstract:
                abstract = title  # Use title if no abstract
            
            # Extract authors
            author_list = article.get('AuthorList', [])
            authors = []
            for author in author_list[:5]:  # Limit to first 5 authors
                last_name = author.get('LastName', '')
                initials = author.get('Initials', '')
                if last_name:
                    authors.append(f"{last_name} {initials}".strip())
            
            # Extract publication date
            pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
            year = pub_date.get('Year', 'Unknown')
            
            # Extract journal
            journal = article.get('Journal', {}).get('Title', 'Unknown Journal')
            
            # Build metadata
            metadata = {
                "pmid": pmid,
                "authors": authors,
                "year": year,
                "journal": journal,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source_type": "pubmed_article"
            }
            
            # Create Document
            doc = Document(
                id=f"pmid:{pmid}",
                source="pubmed",
                title=title,
                content=abstract,
                metadata=metadata,
                relevance_score=None  # Will be set during reranking
            )
            
            return doc
        
        except Exception as e:
            logger.warning(f"Failed to parse article: {e}")
            return None
    
    def fetch_by_ids(self, pmids: List[str]) -> List[Document]:
        """
        Fetch specific articles by PubMed IDs.
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of Document objects
        """
        if not pmids:
            return []
        
        logger.info(f"Fetching {len(pmids)} PubMed articles by ID")
        
        try:
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=pmids,
                rettype="abstract",
                retmode="xml"
            )
            articles = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            documents = []
            for article_data in articles.get('PubmedArticle', []):
                doc = self._parse_article(article_data)
                if doc:
                    documents.append(doc)
            
            return documents
        
        except Exception as e:
            logger.error(f"Failed to fetch PubMed articles: {e}")
            return []

