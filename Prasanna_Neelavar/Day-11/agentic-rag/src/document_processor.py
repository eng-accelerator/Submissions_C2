import pandas as pd
import os
from typing import List
import streamlit as st
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pypdf import PdfReader
from io import BytesIO

@st.cache_resource
def get_embedding_model():
    """Loads the HuggingFace embedding model (cached)."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_text_from_uploaded_files(uploaded_files: List[BytesIO]) -> List[Document]:
    """Reads uploaded files and extracts text, returning a list of Langchain Documents."""
    documents = []
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        if file_name.endswith(".pdf"):
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            documents.append(Document(page_content=text, metadata={"source": file_name}))
        elif file_name.endswith(".txt"):
            text = uploaded_file.getvalue().decode("utf-8")
            documents.append(Document(page_content=text, metadata={"source": file_name}))
        elif file_name.endswith(".csv"):
            # Read CSV into a pandas DataFrame
            df = pd.read_csv(uploaded_file)
            # Convert each row to a Document
            for index, row in df.iterrows():
                # Convert row to a string representation, e.g., JSON or a custom format
                row_content = row.to_json()
                documents.append(Document(page_content=row_content, metadata={"source": file_name, "row_index": index}))
    return documents

def get_text_chunks(documents: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
    """Takes a list of Documents and splits them into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_documents(documents)

def create_vector_store(chunks: List[Document], embeddings_model: HuggingFaceEmbeddings) -> FAISS:
    """Creates and returns a FAISS index from document chunks and an embedding model."""
    return FAISS.from_documents(documents=chunks, embedding=embeddings_model)
