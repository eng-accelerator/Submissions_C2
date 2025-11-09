# core/knowledge_store.py
# Financial Knowledge Base - SHARED Vector DB for unstructured documents

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import tempfile   
import os     

class FinancialKnowledgeStore:
    """
    Manage SHARED financial knowledge base in Vector DB.
    
    All users access the same knowledge base.
    Prevents duplicate crawling of topics.
    """
    
    def __init__(self, user_id: str, api_key: str, db_path: str = "./knowledge_db", base_url: str = None):
        # Use SHARED path for all users
        self.db_path = Path(db_path) / "shared"
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Embeddings with optional base_url for OpenRouter
        embedding_params = {
            "model": "text-embedding-3-small",
            "api_key": api_key
        }
        
        if base_url:
            embedding_params["base_url"] = base_url
        
        self.embeddings = OpenAIEmbeddings(**embedding_params)
        
        # Text splitter for documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Load or create vector store
        self.vector_store = self._load_or_create_store()
        
        # Metadata
        self.metadata_file = self.db_path / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_pdf_from_upload(self, pdf_file):
        """
        Load PDF from Streamlit UploadedFile object.
        
        Args:
            pdf_file: Streamlit UploadedFile object
            
        Returns:
            List of Document objects
        """
        import tempfile
        import os
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name
        
        try:
            # Load with PyPDFLoader
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()
            return pages
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def is_topic_crawled(self, category: str, region: str) -> bool:
        """
        Check if a topic has already been crawled for a region.
        
        Args:
            category: Category name (tax_laws, investment_strategies, etc.)
            region: Region name (India, USA, etc.)
            
        Returns:
            True if already crawled within last 30 days
        """
        if category not in self.metadata:
            return False
        
        # Check if any document in this category matches the region
        for doc_name, doc_info in self.metadata[category].items():
            if doc_info.get('region', '').lower() == region.lower():
                # Check if it's recent (within last 30 days)
                try:
                    added_at = datetime.fromisoformat(doc_info.get('added_at', '2000-01-01'))
                    if datetime.now() - added_at < timedelta(days=30):
                        return True
                except:
                    pass
        
        return False
    
    def get_crawled_topics(self, region: str = None) -> Dict[str, List[Dict]]:
        """
        Get list of topics already crawled.
        
        Args:
            region: Filter by region (optional)
            
        Returns:
            Dict with categories and their crawled topics
        """
        crawled = {
            'tax_laws': [],
            'investment_strategies': [],
            'insurance_info': [],
            'loan_information': [],
            'financial_planning': []
        }
        
        # Check metadata for each category
        for category in crawled.keys():
            if category in self.metadata:
                for doc_name, doc_info in self.metadata[category].items():
                    # Extract region and topic info
                    if region:
                        if doc_info.get('region', '').lower() == region.lower():
                            crawled[category].append({
                                'name': doc_name,
                                'region': doc_info.get('region'),
                                'added_at': doc_info.get('added_at'),
                                'chunks': doc_info.get('chunks', 0)
                            })
                    else:
                        crawled[category].append({
                            'name': doc_name,
                            'region': doc_info.get('region'),
                            'added_at': doc_info.get('added_at'),
                            'chunks': doc_info.get('chunks', 0)
                        })
        
        return crawled
    
    def add_tax_document(self, pdf_file, filename: str, region: str = "India"):
        """Add tax law document to knowledge base."""
        pages = self._load_pdf_from_upload(pdf_file)  # ← ADD THIS LINE
        # Add metadata
        for page in pages:
            page.metadata.update({
                'source': filename,
                'document_type': 'tax_law',
                'region': region,
                'category': 'taxation'
            })
        
        # Split and add to vector store
        chunks = self.text_splitter.split_documents(pages)
        self.vector_store.add_documents(chunks)
        
        self._update_metadata('tax_documents', filename, len(chunks), region)
        self.vector_store.save_local(str(self.db_path / "faiss_index"))
    
    def add_investment_guide(self, pdf_file, filename: str, region: str = "Global"):
        """Add investment strategy document."""
        pages = self._load_pdf_from_upload(pdf_file)
        
        for page in pages:
            page.metadata.update({
                'source': filename,
                'document_type': 'investment_guide',
                'category': 'investment',
                'region': region
            })
        
        chunks = self.text_splitter.split_documents(pages)
        self.vector_store.add_documents(chunks)
        
        self._update_metadata('investment_guides', filename, len(chunks), region)
        self.vector_store.save_local(str(self.db_path / "faiss_index"))
    
    def add_insurance_policy(self, pdf_file, filename: str, policy_type: str, region: str = "India"):
        """Add insurance policy document."""
        pages = self._load_pdf_from_upload(pdf_file)

        for page in pages:
            page.metadata.update({
                'source': filename,
                'document_type': 'insurance_policy',
                'policy_type': policy_type,
                'category': 'insurance',
                'region': region
            })
        
        chunks = self.text_splitter.split_documents(pages)
        self.vector_store.add_documents(chunks)
        
        self._update_metadata('insurance_policies', filename, len(chunks), region)
        self.vector_store.save_local(str(self.db_path / "faiss_index"))
    
    def add_loan_agreement(self, pdf_file, filename: str, loan_type: str, region: str = "India"):
        """Add loan agreement document."""
        pages = self._load_pdf_from_upload(pdf_file)
        
        for page in pages:
            page.metadata.update({
                'source': filename,
                'document_type': 'loan_agreement',
                'loan_type': loan_type,
                'category': 'debt',
                'region': region
            })
        
        chunks = self.text_splitter.split_documents(pages)
        self.vector_store.add_documents(chunks)
        
        self._update_metadata('loan_agreements', filename, len(chunks), region)
        self.vector_store.save_local(str(self.db_path / "faiss_index"))
    
    def add_financial_article(self, text: str, title: str, source: str, 
                             category: str, region: str = "Global"):
        """Add financial article/blog (from crawler) with region tracking."""
        doc = Document(
            page_content=text,
            metadata={
                'source': source,
                'title': title,
                'document_type': 'article',
                'category': category,
                'region': region
            }
        )
        
        chunks = self.text_splitter.split_documents([doc])
        self.vector_store.add_documents(chunks)
        
        # Use region in the document key to track regional content
        doc_key = f"{region}_{title[:50]}"
        
        self._update_metadata('articles', doc_key, len(chunks), region)
        self.vector_store.save_local(str(self.db_path / "faiss_index"))
    
    def search_knowledge(self, query: str, category: str = None, region: str = None, top_k: int = 5):
        """
        Search knowledge base.
        
        Args:
            query: Search query
            category: Filter by category (optional)
            region: Filter by region (optional)
            top_k: Number of results
        """
        # Build filter
        filter_dict = {}
        if category:
            filter_dict['category'] = category
        if region:
            filter_dict['region'] = region
        
        if filter_dict:
            results = self.vector_store.similarity_search(
                query,
                k=top_k,
                filter=filter_dict
            )
        else:
            results = self.vector_store.similarity_search(query, k=top_k)
        
        return [
            {
                'content': doc.page_content,
                'metadata': doc.metadata
            }
            for doc in results
        ]
    
    def get_statistics(self):
        """Get knowledge base statistics with region breakdown."""
        stats = {
            'total_documents': 0,
            'categories': {
                'tax_documents': 0,
                'investment_guides': 0,
                'insurance_policies': 0,
                'loan_agreements': 0,
                'articles': 0
            },
            'by_region': {}
        }
        
        for category, docs in self.metadata.items():
            if category in stats['categories']:
                stats['categories'][category] = len(docs)
            stats['total_documents'] += len(docs)
            
            # Count by region
            for doc_info in docs.values():
                region = doc_info.get('region', 'Unknown')
                if region not in stats['by_region']:
                    stats['by_region'][region] = 0
                stats['by_region'][region] += 1
        
        return stats
    
    def _load_or_create_store(self):
        """Load existing or create new vector store."""
        index_path = self.db_path / "faiss_index"
        
        if index_path.exists():
            try:
                return FAISS.load_local(
                    str(index_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except:
                # If loading fails, create new
                pass
        
        # Create empty store
        dummy_doc = Document(page_content="initialization", metadata={})
        return FAISS.from_documents([dummy_doc], self.embeddings)
    
    def _load_metadata(self):
        """Load metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {
            'tax_documents': {},
            'investment_guides': {},
            'insurance_policies': {},
            'loan_agreements': {},
            'articles': {}
        }
    
    def _update_metadata(self, category: str, filename: str, chunk_count: int, region: str = "Global"):
        """Update metadata after adding document."""
        if category not in self.metadata:
            self.metadata[category] = {}
        
        self.metadata[category][filename] = {
            'added_at': datetime.now().isoformat(),
            'chunks': chunk_count,
            'region': region
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)