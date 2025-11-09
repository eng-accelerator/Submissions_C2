# -*- coding: utf-8 -*-
"""Multi-Agent AI Researcher Module"""

import time
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate


class ResearchState(TypedDict):
    """State passed between agents"""
    query: str
    temperature: float
    context_documents: List[str]
    critical_analysis: str
    insights: List[str]
    report: str
    validation_passed: bool
    validation_feedback: str
    iteration_count: int
    max_iterations: int
    processing_time: Dict[str, float]


class SimpleMultiAgentResearcher:
    """Simplified research system - no vector embeddings needed"""

    def __init__(self, openrouter_api_key: str, temperature: float = 0.7,
                 model: str = "anthropic/claude-sonnet-4-20250514"):
        self.api_key = openrouter_api_key
        self.temperature = temperature
        self.model = model
        self.documents = []

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=self.temperature,
            default_headers={
                "HTTP-Referer": "https://github.com/multi-agent-researcher",
                "X-Title": "Multi-Agent AI Researcher"
            }
        )

        # Build workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

    def _build_workflow(self) -> StateGraph:
        """Build agent workflow"""
        workflow = StateGraph(ResearchState)

        workflow.add_node("contextual_retriever", self.contextual_retriever_agent)
        workflow.add_node("critical_analysis", self.critical_analysis_agent)
        workflow.add_node("insight_generation", self.insight_generation_agent)
        workflow.add_node("report_builder", self.report_builder_agent)
        workflow.add_node("validation", self.validation_agent)

        workflow.set_entry_point("contextual_retriever")
        workflow.add_edge("contextual_retriever", "critical_analysis")
        workflow.add_edge("critical_analysis", "insight_generation")
        workflow.add_edge("insight_generation", "report_builder")
        workflow.add_edge("report_builder", "validation")

        workflow.add_conditional_edges(
            "validation",
            self._should_continue,
            {"continue": "critical_analysis", "end": END}
        )

        return workflow

    def _should_continue(self, state: ResearchState) -> str:
        if state["validation_passed"]:
            return "end"
        elif state["iteration_count"] >= state["max_iterations"]:
            return "end"
        return "continue"

    def load_documents(self, documents: List[str]):
        """Load documents (simple text storage)"""
        self.documents = documents
        return len(documents)

    def contextual_retriever_agent(self, state: ResearchState) -> ResearchState:
        """Agent 1: Simple context retrieval"""
        start = time.time()

        # Simple keyword matching instead of embeddings
        query_lower = state["query"].lower()
        query_words = set(query_lower.split())

        if self.documents:
            # Score documents by keyword overlap
            scored_docs = []
            for doc in self.documents:
                doc_words = set(doc.lower().split())
                overlap = len(query_words & doc_words)
                scored_docs.append((overlap, doc))

            # Sort by score and take top docs
            scored_docs.sort(reverse=True, key=lambda x: x[0])
            state["context_documents"] = [doc for score, doc in scored_docs[:3]]
        else:
            state["context_documents"] = ["No documents provided. Using general knowledge."]

        if "processing_time" not in state:
            state["processing_time"] = {}
        state["processing_time"]["retrieval"] = time.time() - start

        return state

    def critical_analysis_agent(self, state: ResearchState) -> ResearchState:
        """Agent 2: Critical analysis"""
        start = time.time()

        self.llm.temperature = state["temperature"]

        context_str = "\n\n".join([
            f"Document {i+1}:\n{doc[:500]}"
            for i, doc in enumerate(state["context_documents"])
        ])

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a critical analysis expert. Evaluate information quality, identify biases, gaps, and assess relevance to the research query."),
            HumanMessage(content=f"Research Query: {state['query']}\n\nAvailable Context:\n{context_str}\n\nProvide critical analysis.")
        ])

        response = self.llm.invoke(prompt.format_messages())
        state["critical_analysis"] = response.content
        state["processing_time"]["analysis"] = time.time() - start

        return state

    def insight_generation_agent(self, state: ResearchState) -> ResearchState:
        """Agent 3: Generate insights"""
        start = time.time()

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="Generate 5-7 actionable insights as a numbered list. Be concise and specific."),
            HumanMessage(content=f"Query: {state['query']}\n\nAnalysis: {state['critical_analysis']}\n\nGenerate key insights.")
        ])

        response = self.llm.invoke(prompt.format_messages())

        insights = [
            line.strip()
            for line in response.content.split('\n')
            if line.strip() and any(c.isdigit() for c in line[:3])
        ]

        if not insights:
            insights = [response.content]

        state["insights"] = insights
        state["processing_time"]["insights"] = time.time() - start

        return state

    def report_builder_agent(self, state: ResearchState) -> ResearchState:
        """Agent 4: Build comprehensive report"""
        start = time.time()

        insights_str = "\n".join(state["insights"])

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="Create a structured research report with: Executive Summary, Key Findings, Detailed Analysis, Insights & Implications, Recommendations, and Conclusion. Make it comprehensive and professional."),
            HumanMessage(content=f"Research Query: {state['query']}\n\nCritical Analysis:\n{state['critical_analysis']}\n\nKey Insights:\n{insights_str}\n\nCreate the final research report.")
        ])

        response = self.llm.invoke(prompt.format_messages())
        state["report"] = response.content
        state["processing_time"]["report"] = time.time() - start

        return state

    def validation_agent(self, state: ResearchState) -> ResearchState:
        """Agent 5: Validate report quality"""
        start = time.time()

        self.llm.temperature = 0.3

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="Validate this report on completeness, coherence, evidence, clarity, and actionability. Start your response with either PASS or FAIL, then explain why."),
            HumanMessage(content=f"Query: {state['query']}\n\nReport:\n{state['report']}\n\nValidate.")
        ])

        response = self.llm.invoke(prompt.format_messages())
        validation_text = response.content

        passed = "PASS" in validation_text.upper().split('\n')[0]

        state["validation_passed"] = passed
        state["validation_feedback"] = validation_text
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        state["processing_time"]["validation"] = time.time() - start

        return state

    def research(self, query: str, temperature: float = None, max_iterations: int = 2) -> Dict[str, Any]:
        """Execute research workflow"""
        if temperature is None:
            temperature = self.temperature

        initial_state = ResearchState(
            query=query,
            temperature=temperature,
            context_documents=[],
            critical_analysis="",
            insights=[],
            report="",
            validation_passed=False,
            validation_feedback="",
            iteration_count=0,
            max_iterations=max_iterations,
            processing_time={}
        )

        final_state = self.app.invoke(initial_state)
        total_time = sum(final_state["processing_time"].values())

        return {
            "query": final_state["query"],
            "report": final_state["report"],
            "insights": final_state["insights"],
            "analysis": final_state["critical_analysis"],
            "validation_passed": final_state["validation_passed"],
            "validation_feedback": final_state["validation_feedback"],
            "iterations": final_state["iteration_count"],
            "processing_time": final_state["processing_time"],
            "total_time": total_time
        }

