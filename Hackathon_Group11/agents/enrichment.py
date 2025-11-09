"""
Data Enrichment Agent
Enriches search results with metadata, sentiment analysis, and topic extraction.
Provides domain authority scores, sentiment analysis, and categorization.
"""

import logging
import os
import re
from typing import Dict, List, Any
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv
from utils.llm_config import create_llm

load_dotenv()
logger = logging.getLogger(__name__)


class DataEnrichmentAgent:
    """Enriches search results with metadata and analysis."""
    
    def __init__(self):
        """Initialize enrichment agent."""
        # Initialize LLM for advanced enrichment (optional)
        self.llm = create_llm(temperature=0.3, max_tokens=500)
        if not self.llm:
            logger.warning("LLM not available. Enrichment will use heuristics only.")
        
        logger.info("Data Enrichment Agent initialized")
    
    def enrich_sources(self, sources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich search results with metadata, sentiment, and topics.
        
        Args:
            sources: Raw sources from retriever
            
        Returns:
            Enriched sources with additional metadata
        """
        logger.info("Enricher: Starting source enrichment")
        
        enriched = {
            "web": self._enrich_list(sources.get("web", []), "web"),
            "papers": sources.get("papers", []),  # Papers usually don't need enrichment
            "news": self._enrich_list(sources.get("news", []), "news"),
            "query": sources.get("query", ""),
            "metadata": {
                "total_sources": len(sources.get("web", [])) + len(sources.get("news", [])),
                "enrichment_applied": True,
                "enrichment_timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"Enricher: Enriched {enriched['metadata']['total_sources']} sources")
        return enriched
    
    def _enrich_list(self, source_list: List[Dict[str, Any]], source_type: str) -> List[Dict[str, Any]]:
        """Enrich a list of sources."""
        enriched_list = []
        
        for source in source_list:
            enriched = source.copy()
            
            # Add domain authority score
            enriched["domain_score"] = self._calculate_domain_score(source.get("url", ""))
            
            # Add sentiment analysis
            enriched["sentiment"] = self._analyze_sentiment(source.get("snippet", ""))
            
            # Add category
            enriched["category"] = self._categorize_source(source, source_type)
            
            # Add metadata
            enriched["metadata"] = self._extract_metadata(source)
            
            enriched_list.append(enriched)
        
        return enriched_list
    
    def _calculate_domain_score(self, url: str) -> float:
        """
        Calculate domain authority score based on URL patterns.
        
        Returns:
            Score between 0.0 and 1.0
        """
        if not url:
            return 0.0
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # High authority domains
            high_authority = [".edu", ".gov", ".org", ".ac.uk", ".edu.au"]
            medium_authority = [".com", ".net", ".io", ".co"]
            
            # Check for high authority
            if any(domain.endswith(ext) for ext in high_authority):
                return 0.9
            
            # Check for medium authority
            if any(domain.endswith(ext) for ext in medium_authority):
                # Check for known reputable domains
                reputable_domains = [
                    "wikipedia.org", "github.com", "stackoverflow.com",
                    "arxiv.org", "nature.com", "science.org", "ieee.org",
                    "acm.org", "springer.com", "elsevier.com"
                ]
                if any(rep in domain for rep in reputable_domains):
                    return 0.8
                return 0.6
            
            # Default score
            return 0.5
            
        except Exception as e:
            logger.warning(f"Error calculating domain score: {e}")
            return 0.5
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Returns:
            Dictionary with sentiment label and score
        """
        if not text:
            return {"label": "neutral", "score": 0.0}
        
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = [
            "success", "achievement", "breakthrough", "innovation", "improve",
            "benefit", "advantage", "positive", "excellent", "great", "good",
            "effective", "efficient", "promising", "significant", "important"
        ]
        
        # Negative indicators
        negative_words = [
            "failure", "problem", "issue", "concern", "risk", "threat",
            "negative", "poor", "bad", "ineffective", "inefficient",
            "decline", "decrease", "worse", "challenge", "difficulty"
        ]
        
        # Count sentiment words
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment score (-1 to 1)
        total_words = len(text.split())
        if total_words == 0:
            return {"label": "neutral", "score": 0.0}
        
        sentiment_score = (positive_count - negative_count) / max(total_words, 1)
        
        # Normalize to -1 to 1 range
        sentiment_score = max(-1.0, min(1.0, sentiment_score * 10))
        
        # Determine label
        if sentiment_score > 0.1:
            label = "positive"
        elif sentiment_score < -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        return {
            "label": label,
            "score": round(sentiment_score, 2)
        }
    
    def _categorize_source(self, source: Dict[str, Any], source_type: str) -> str:
        """
        Categorize source by content and type.
        
        Returns:
            Category string
        """
        snippet = source.get("snippet", "").lower()
        title = source.get("title", "").lower()
        url = source.get("url", "").lower()
        
        # Research/Academic
        research_keywords = ["research", "study", "paper", "journal", "academic", 
                           "university", "arxiv", "pubmed", "doi"]
        if any(keyword in snippet or keyword in title or keyword in url 
               for keyword in research_keywords):
            return "research"
        
        # News
        news_keywords = ["news", "report", "article", "breaking", "update", 
                        "announcement", "press", "media"]
        if any(keyword in snippet or keyword in title or keyword in url 
               for keyword in news_keywords):
            return "news"
        
        # Technical/Documentation
        tech_keywords = ["documentation", "tutorial", "guide", "api", 
                        "github", "stackoverflow", "technical"]
        if any(keyword in snippet or keyword in title or keyword in url 
               for keyword in tech_keywords):
            return "technical"
        
        # Blog/Opinion
        blog_keywords = ["blog", "opinion", "viewpoint", "perspective", "commentary"]
        if any(keyword in snippet or keyword in title or keyword in url 
               for keyword in blog_keywords):
            return "blog"
        
        # Default based on source type
        if source_type == "news":
            return "news"
        elif source_type == "web":
            return "general"
        else:
            return "general"
    
    def _extract_metadata(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract additional metadata from source.
        
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        
        # Extract domain from URL
        url = source.get("url", "")
        if url:
            try:
                parsed = urlparse(url)
                metadata["domain"] = parsed.netloc
                metadata["path"] = parsed.path
            except Exception:
                pass
        
        # Extract date if available
        published_date = source.get("published_date", "")
        if published_date:
            metadata["published_date"] = published_date
        
        # Extract word count
        snippet = source.get("snippet", "")
        if snippet:
            metadata["word_count"] = len(snippet.split())
            metadata["char_count"] = len(snippet)
        
        # Extract language (simple heuristic - can be enhanced)
        if snippet:
            # Simple English detection
            common_english_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
            words = snippet.lower().split()
            english_word_count = sum(1 for word in words if word in common_english_words)
            if len(words) > 0:
                english_ratio = english_word_count / len(words)
                metadata["language"] = "en" if english_ratio > 0.1 else "unknown"
        
        return metadata
    
    def _enrich_with_llm(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM for advanced enrichment (optional enhancement).
        
        This can be used for more sophisticated sentiment analysis,
        topic extraction, or other advanced features.
        """
        if not self.llm:
            return {}
        
        try:
            snippet = source.get("snippet", "")[:500]  # Limit text length
            
            # Use LLM for advanced analysis (can be enhanced)
            # For now, return empty dict - can be implemented later
            return {}
            
        except Exception as e:
            logger.warning(f"LLM enrichment failed: {e}")
            return {}

