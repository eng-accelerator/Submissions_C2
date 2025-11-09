"""
Vector Database Manager for AI Financial Coach
Handles document processing, vectorization, and retrieval using FAISS
"""

import os
import json
import pickle
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings

# Document loaders
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
import pandas as pd
import io
import re

# Import smart parser
from transaction_parser import BankStatementParser, parse_csv_file, parse_excel_file


class VectorDBManager:
    """
    Manages vector database operations for financial documents.
    Each user has their own isolated collection.
    """
    
    def __init__(self, user_id: str, openrouter_api_key: str, db_path: str = "./vector_db"):
        """
        Initialize Vector DB Manager for a specific user
        
        Args:
            user_id: Unique identifier for the user
            openrouter_api_key: OpenRouter API key for embeddings
            db_path: Base path for storing vector databases
        """
        self.user_id = user_id
        self.db_path = os.path.join(db_path, user_id)
        self.openrouter_api_key = openrouter_api_key
        
        # Create user-specific directory
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize embeddings using OpenRouter
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # Efficient embedding model
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Smaller chunks for financial data
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Load or initialize vector store
        self.vector_store = self._load_or_create_vector_store()
        
        # Metadata store
        self.metadata_file = os.path.join(self.db_path, "metadata.json")
        self.metadata = self._load_metadata()
    
    def _load_or_create_vector_store(self):
        """Load existing vector store or create a new one"""
        vector_store_path = os.path.join(self.db_path, "faiss_index")
        
        if os.path.exists(vector_store_path):
            try:
                return FAISS.load_local(
                    vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Error loading vector store: {e}")
                return None
        return None
    
    def _save_vector_store(self):
        """Save vector store to disk"""
        if self.vector_store:
            vector_store_path = os.path.join(self.db_path, "faiss_index")
            self.vector_store.save_local(vector_store_path)
    
    def _load_metadata(self) -> Dict:
        """Load metadata from disk"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"documents": {}, "total_chunks": 0}
    
    def _save_metadata(self):
        """Save metadata to disk"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _extract_transaction_data(self, text: str) -> List[Dict]:
        """
        Extract transaction details from text using pattern matching
        
        Args:
            text: Raw text from document
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        # Common patterns for transactions
        # Pattern 1: Date Amount Description
        pattern1 = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?:₹|Rs\.?|INR)?\s*(-?\d+(?:,\d+)*(?:\.\d{2})?)\s+(.+?)(?=\d{1,2}[/-]|\n|$)'
        
        # Pattern 2: Description followed by amount
        pattern2 = r'(.+?)\s+(?:₹|Rs\.?|INR)?\s*(-?\d+(?:,\d+)*(?:\.\d{2})?)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        
        matches1 = re.finditer(pattern1, text, re.MULTILINE)
        for match in matches1:
            date, amount, description = match.groups()
            transactions.append({
                'date': date.strip(),
                'amount': amount.strip().replace(',', ''),
                'description': description.strip(),
                'type': 'debit' if '-' in amount else 'credit'
            })
        
        matches2 = re.finditer(pattern2, text, re.MULTILINE)
        for match in matches2:
            description, amount, date = match.groups()
            transactions.append({
                'date': date.strip(),
                'amount': amount.strip().replace(',', ''),
                'description': description.strip(),
                'type': 'debit' if '-' in amount else 'credit'
            })
        
        return transactions
    
    def _categorize_transaction(self, description: str) -> str:
        """
        Categorize transaction based on description
        Uses intelligent keyword matching and merchant name extraction
        
        Args:
            description: Transaction description
            
        Returns:
            Category name
        """
        description_lower = description.lower()
        
        # Enhanced categories with more keywords
        categories = {
            'cash_withdrawal': ['atm', 'cash withdrawal', 'atm withdrawal', 'cash', 'withdrawal', 'atm wdl'],
            'food_dining': [
                'restaurant', 'cafe', 'swiggy', 'zomato', 'food', 'dining', 'pizza', 'burger', 
                'hotel', 'dhaba', 'barbeque', 'kitchen', 'bakery', 'sweet', 'dominos', 'mcdonald',
                'kfc', 'subway', 'starbucks', 'ccd', 'coffee', 'tea', 'breakfast', 'lunch', 'dinner'
            ],
            'transport': [
                'uber', 'ola', 'petrol', 'fuel', 'metro', 'taxi', 'parking', 'rapido', 'auto',
                'bus', 'train', 'flight', 'cab', 'vehicle', 'transport', 'travel', 'toll'
            ],
            'shopping': [
                'amazon', 'flipkart', 'shop', 'store', 'mall', 'purchase', 'myntra', 'ajio',
                'clothing', 'fashion', 'dress', 'shoes', 'electronics', 'appliance', 'mobile',
                'grocery', 'supermarket', 'big bazaar', 'dmart', 'reliance', 'retail'
            ],
            'utilities': [
                'electricity', 'water', 'gas', 'internet', 'mobile', 'phone', 'bill', 'recharge',
                'broadband', 'wifi', 'telecom', 'airtel', 'jio', 'vodafone', 'bsnl', 'postpaid'
            ],
            'entertainment': [
                'movie', 'netflix', 'spotify', 'prime', 'gaming', 'entertainment', 'youtube',
                'cinema', 'theater', 'hotstar', 'disney', 'subscription', 'music', 'video'
            ],
            'healthcare': [
                'hospital', 'pharmacy', 'medicine', 'doctor', 'clinic', 'health', 'medical',
                'lab', 'test', 'diagnostic', 'chemist', 'apollo', 'medplus', 'insurance'
            ],
            'emi_debt': [
                'emi', 'loan', 'credit card', 'debt', 'payment', 'installment', 'repayment',
                'credit', 'emi payment', 'loan repayment'
            ],
            'housing': [
                'rent', 'maintenance', 'society', 'housing', 'house rent', 'flat', 'apartment'
            ],
            'investment': [
                'mutual fund', 'sip', 'stock', 'investment', 'savings', 'fd', 'rd',
                'deposit', 'recurring', 'systematic', 'equity', 'debt fund', 'ppf', 'nps'
            ],
            'transfer': [
                'transfer', 'upi', 'neft', 'imps', 'rtgs', 'paytm', 'phonepe', 'gpay', 
                'googlepay', 'fund transfer', 'self transfer', 'wallet'
            ],
            'salary': [
                'salary', 'wage', 'income', 'payment received', 'credit interest',
                'sal credit', 'payroll', 'stipend'
            ],
            'education': [
                'school', 'college', 'university', 'education', 'tuition', 'course', 
                'training', 'book', 'exam', 'fee', 'admission'
            ],
            'insurance': [
                'insurance', 'policy', 'premium', 'lic', 'life insurance', 'health insurance',
                'vehicle insurance', 'general insurance'
            ],
        }
        
        # Priority matching - check specific keywords first
        for category, keywords in categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'others'
    
    def _create_enhanced_chunks(self, transactions: List[Dict], filename: str) -> List[Document]:
        """
        Create enhanced document chunks with transaction details
        
        Args:
            transactions: List of extracted transactions
            filename: Source filename
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        for trans in transactions:
            # Get transaction details
            mode = trans.get('mode', 'unknown')
            party_name = trans.get('party_name', '')
            reference = trans.get('reference', '')
            value_date = trans.get('value_date', '')
            
            # Categorize based on description
            category = self._categorize_transaction(trans['description'])
            
            # Build detailed content
            content_parts = [
                "Transaction Details:",
                f"Date: {trans['date']}"
            ]
            
            if value_date and value_date != trans['date']:
                content_parts.append(f"Value Date: {value_date}")
            
            content_parts.extend([
                f"Amount: {trans['amount']}",
                f"Type: {trans['type']}",
                f"Mode: {mode}",
                f"Category: {category}"
            ])
            
            if reference:
                content_parts.append(f"Reference: {reference}")
            
            if party_name:
                content_parts.append(f"Party: {party_name}")
            
            content_parts.append(f"Description: {trans['description']}")
            
            # Add balance if available
            if trans.get('balance'):
                content_parts.append(f"Balance: {trans['balance']}")
            
            content = "\n".join(content_parts).strip()
            
            metadata = {
                'source': filename,
                'date': trans['date'],
                'amount': trans['amount'],
                'type': trans['type'],
                'mode': mode,
                'category': category,
                'description': trans['description']
            }
            
            if value_date:
                metadata['value_date'] = value_date
            if party_name:
                metadata['party_name'] = party_name
            if reference:
                metadata['reference'] = reference
            
            documents.append(Document(page_content=content, metadata=metadata))
        
        return documents
    
    def process_pdf(self, file, filename: str) -> List[Document]:
        """
        Process PDF file and extract transactions
        
        Args:
            file: File object
            filename: Name of the file
            
        Returns:
            List of Document objects
        """
        # Save temporarily
        temp_path = os.path.join(self.db_path, f"temp_{filename}")
        with open(temp_path, 'wb') as f:
            f.write(file.getvalue())
        
        # Load PDF
        loader = PyPDFLoader(temp_path)
        pages = loader.load()
        
        # Extract all text
        full_text = "\n".join([page.page_content for page in pages])
        
        # Extract transactions
        transactions = self._extract_transaction_data(full_text)
        
        # Create enhanced chunks
        documents = self._create_enhanced_chunks(transactions, filename)
        
        # Clean up
        os.remove(temp_path)
        
        return documents
    
    def process_excel(self, file, filename: str) -> List[Document]:
        """
        Process Excel file with transaction data using smart parser
        
        Args:
            file: File object
            filename: Name of the file
            
        Returns:
            List of Document objects
        """
        # Use smart parser
        transactions = parse_excel_file(file, filename)
        
        # Create enhanced chunks
        return self._create_enhanced_chunks(transactions, filename)
    
    def process_csv(self, file, filename: str) -> List[Document]:
        """
        Process CSV file with transaction data using smart parser
        
        Args:
            file: File object
            filename: Name of the file
            
        Returns:
            List of Document objects
        """
        # Use smart parser
        transactions = parse_csv_file(file, filename)
        
        # Create enhanced chunks
        return self._create_enhanced_chunks(transactions, filename)
    
    def process_and_store_document(self, file, filename: str) -> Dict[str, Any]:
        """
        Process document and store in vector database
        
        Args:
            file: Uploaded file object
            filename: Name of the file
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Determine file type and process accordingly
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext == 'pdf':
                documents = self.process_pdf(file, filename)
            elif file_ext in ['xlsx', 'xls']:
                documents = self.process_excel(file, filename)
            elif file_ext == 'csv':
                documents = self.process_csv(file, filename)
            else:
                return {'success': False, 'message': f'Unsupported file type: {file_ext}'}
            
            if not documents:
                return {'success': False, 'message': 'No transactions found in document'}
            
            # Add to vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            else:
                self.vector_store.add_documents(documents)
            
            # Save vector store
            self._save_vector_store()
            
            # Update metadata
            self.metadata['documents'][filename] = {
                'added_at': datetime.now().isoformat(),
                'chunks': len(documents),
                'transactions': len(documents)
            }
            self.metadata['total_chunks'] += len(documents)
            self._save_metadata()
            
            return {
                'success': True,
                'message': f'Successfully processed {len(documents)} transactions',
                'chunks_created': len(documents)
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error processing document: {str(e)}'}
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search vector database for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of search results with content and metadata
        """
        if self.vector_store is None:
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(score)
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents in the database"""
        return len(self.metadata.get('documents', {}))
    
    def get_all_transactions_by_category(self) -> Dict[str, List[Dict]]:
        """
        Retrieve all transactions grouped by category
        
        Returns:
            Dictionary with categories as keys and transaction lists as values
        """
        if self.vector_store is None:
            return {}
        
        # This would require storing all documents separately
        # For now, return empty dict
        return {}
    
    def delete_document(self, filename: str) -> bool:
        """
        Delete a document from the vector store
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            Success status
        """
        try:
            if filename in self.metadata['documents']:
                # Remove from metadata
                chunks = self.metadata['documents'][filename]['chunks']
                self.metadata['total_chunks'] -= chunks
                del self.metadata['documents'][filename]
                self._save_metadata()
                
                # Note: FAISS doesn't support easy deletion
                # Would need to rebuild index without this document
                # For now, just update metadata
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
