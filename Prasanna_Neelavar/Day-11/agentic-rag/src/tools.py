from typing import Any, Dict, List, Optional
from langchain.tools import BaseTool
from langchain_community.vectorstores import FAISS
from langchain_tavily import TavilySearch
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_core.callbacks import CallbackManagerForToolRun

class DocumentRAGTool(BaseTool):
    name: str = "document_rag_tool"
    description: str = "Useful for answering questions directly from the uploaded documents. Prioritize this tool for specific document-related queries."
    vectorstore: FAISS

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool synchronously."""
        if self.vectorstore:
            docs = self.vectorstore.similarity_search(query)
            return "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant information found in the documents."
        return "No documents have been uploaded yet."

def get_all_tools(faiss_index: FAISS) -> List[BaseTool]:
    """Initializes and returns all tools for the agent."""
    tavily_tool = TavilySearch(max_results=5)
    arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=3, doc_content_chars_max=4000))
    wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=4000))
    doc_rag_tool = DocumentRAGTool(vectorstore=faiss_index)

    return [doc_rag_tool, tavily_tool, arxiv_tool, wikipedia_tool]
