# core/financial_planner_agent.py
# Multi-agent financial planner using LangChain with Tavily fallback
from core.visualization_builder import VisualizationBuilder
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import json
from datetime import datetime

class FinancialPlannerAgent:
    """
    Multi-agent financial planning system with web search fallback.
    
    Agents:
    - Query Understanding Agent: Extracts intent and time context
    - Data Retrieval Agent: Fetches relevant financial data
    - Knowledge Agent: Searches knowledge base OR web (Tavily fallback)
    - Analysis Agent: Analyzes data and generates insights
    """
    
    def __init__(self, transaction_store, knowledge_store, openai_api_key: str, base_url: str, tavily_api_key: str = None):
        self.transaction_store = transaction_store
        self.knowledge_store = knowledge_store
        
        # Initialize LLM with optional custom base_url (for OpenRouter, etc.)
        llm_params = {
            "model": "gpt-4o-mini",
            "api_key": openai_api_key,
            "temperature": 0.3
        }
        
        if base_url:
            llm_params["base_url"] = base_url
        
        self.llm = ChatOpenAI(**llm_params)
        
        # Initialize Tavily search tool (optional)
        self.tavily_api_key = tavily_api_key
        self.tavily_tool = None
        
        if tavily_api_key:
            try:
                from langchain_community.tools.tavily_search import TavilySearchResults
                self.tavily_tool = TavilySearchResults(
                    api_key=tavily_api_key,
                    max_results=3
                )
                print("✅ Tavily search enabled as fallback")
            except ImportError:
                print("⚠️ Tavily not available. Install: pip install langchain-community tavily-python")
            except Exception as e:
                print(f"⚠️ Tavily initialization error: {e}")
    
    def chat(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Process user query through multi-agent system with web search fallback.
        """
        reasoning = []
        
        # Step 1: Query Understanding Agent
        reasoning.append({
            'agent': 'Query Understanding Agent',
            'action': 'Analyzing query to understand intent and time requirements'
        })
        
        query_analysis = self._analyze_query(query)
        
        reasoning.append({
            'agent': 'Query Understanding Agent',
            'action': f"Detected: {query_analysis.get('time_context', 'all data')}"
        })
        
        # Step 2: Data Retrieval Agent
        reasoning.append({
            'agent': 'Data Retrieval Agent',
            'action': f"Fetching financial data: {query_analysis.get('time_context', 'all data')}"
        })
        
        user_data = self._fetch_financial_data(user_id, query_analysis)
        
        # Step 3: Knowledge Agent - Search knowledge base first, then web fallback
        knowledge = []
        knowledge_source = None
        
        if query_analysis.get('needs_knowledge', False):
            reasoning.append({
                'agent': 'Knowledge Agent',
                'action': f"Searching knowledge base for: {', '.join(query_analysis.get('knowledge_topics', ['financial advice']))}"
            })
            
            knowledge = self._search_knowledge(
                query, 
                topics=query_analysis.get('knowledge_topics', [])
            )
            
            if knowledge:
                reasoning.append({
                    'agent': 'Knowledge Agent',
                    'action': f"✅ Found {len(knowledge)} relevant documents in knowledge base"
                })
                knowledge_source = 'knowledge_base'
            else:
                reasoning.append({
                    'agent': 'Knowledge Agent',
                    'action': "❌ No knowledge base results. Searching web with Tavily..."
                })
                
                web_results = self._search_web(query, query_analysis.get('knowledge_topics', []))
                
                if web_results:
                    knowledge = web_results
                    reasoning.append({
                        'agent': 'Knowledge Agent',
                        'action': f"🌐 Found {len(web_results)} relevant results from web search"
                    })
                    knowledge_source = 'web_search'
                else:
                    reasoning.append({
                        'agent': 'Knowledge Agent',
                        'action': "⚠️ No web search results. Using general financial principles."
                    })
                    knowledge_source = 'general'
        
        # Step 4: Build Visualizations (NEW!)
        visualizations = []
        if query_analysis.get('needs_visualization', False):
            reasoning.append({
                'agent': 'Visualization Agent',
                'action': 'Building interactive charts and graphs'
            })
            
            visualizations = self._build_visualizations(user_data, query_analysis)
            
            if visualizations:
                reasoning.append({
                    'agent': 'Visualization Agent',
                    'action': f"✅ Generated {len(visualizations)} chart(s)"
                })
        
        # Step 5: Analysis Agent
        reasoning.append({
            'agent': 'Analysis Agent',
            'action': 'Generating personalized financial insights'
        })
        
        response = self._generate_response(query, user_data, knowledge, query_analysis, knowledge_source)
        
        return {
            'response': response,
            'reasoning': reasoning,
            'query_analysis': query_analysis,
            'knowledge_used': len(knowledge) > 0,
            'knowledge_source': knowledge_source,
            'visualizations': visualizations  # NEW!
        }

    def _search_web(self, query: str, topics: List[str] = None) -> List[Dict]:
        """
        Search web using Tavily when knowledge base has no results.
        
        Args:
            query: User query
            topics: List of topic keywords
            
        Returns:
            List of search results formatted like knowledge base results
        """
        if not self.tavily_tool:
            print("⚠️ Tavily tool not initialized. Skipping web search.")
            return []
        
        try:
            # Build enhanced search query with topics
            search_query = query
            if topics:
                # Add topic context to improve search relevance
                topic_context = " ".join(topics)
                search_query = f"{query} {topic_context} financial advice guide"
            
            print(f"🔍 Tavily search query: {search_query}")
            
            # Execute search
            results = self.tavily_tool.invoke({"query": search_query})
            
            if not results:
                print("⚠️ Tavily returned no results")
                return []
            
            print(f"✅ Tavily found {len(results)} results")
            
            # Format results to match knowledge base structure
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'content': result.get('content', ''),
                    'metadata': {
                        'source': result.get('url', ''),
                        'title': result.get('title', 'Web Search Result'),
                        'category': topics[0] if topics else 'general',
                        'region': 'Global',
                        'source_type': 'web_search'
                    }
                })
            
            return formatted_results
        
        except Exception as e:
            print(f"❌ Tavily search error: {e}")
            import traceback
            traceback.print_exc()
            return []

    
    def _calculate_dates(self, query: str, analysis: Dict) -> Dict:
        """
        Use LLM to calculate specific dates from natural language.
        """
        date_prompt = f"""Current date: {datetime.now().strftime('%Y-%m-%d')}
        Query: "{query}"

        Calculate the exact start_date and end_date in YYYY-MM-DD format.

        Examples:
        "last 3 months" → start: 3 months ago, end: today
        "January 2024" → start: 2024-01-01, end: 2024-01-31
        "Q1 2024" → start: 2024-01-01, end: 2024-03-31

        Respond with ONLY JSON:
        {{
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        }}"""

        try:
            response = self.llm.invoke([HumanMessage(content=date_prompt)])
            response_text = response.content.strip()
            
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            dates = json.loads(response_text)
            
            sql_params = analysis['sql_params'].copy()
            sql_params['start_date'] = dates['start_date']
            sql_params['end_date'] = dates['end_date']
            
            return sql_params
        
        except Exception as e:
            print(f"Error calculating dates: {e}")
            return analysis['sql_params']
    
    def _fetch_financial_data(self, user_id: str, query_analysis: Dict) -> Dict:
        """
        Fetch financial data based on query analysis.
        """
        if not self.transaction_store:
            return {'error': 'No transaction data available'}
        
        try:
            db_user_id = self.transaction_store.get_user_id(user_id)
            
            if not db_user_id:
                return {'error': 'User not found in database'}
            
            sql_params = query_analysis['sql_params']
            query_type = sql_params['type']
            
            if query_type == 'latest_month':
                # Get latest month with data
                data = self.transaction_store.get_latest_month_transactions(db_user_id)
                
                return {
                    'type': 'single_period',
                    'period': data.get('period', 'Latest month'),
                    'income': float(data['summary'].get('total_income', 0)),
                    'expenses': float(data['summary'].get('total_expenses', 0)),
                    'savings': float(data['summary'].get('savings', 0)),
                    'savings_rate': float(data['summary'].get('savings_rate', 0)),
                    'categories': data['summary'].get('category_breakdown', []),
                    'transaction_count': data['summary'].get('transaction_count', 0),
                    'date_range': f"{data.get('start_date')} to {data.get('end_date')}"
                }
            
            elif query_type == 'monthly':
                # Get monthly breakdown
                months = sql_params.get('months', 6)
                monthly_data = self.transaction_store.get_monthly_breakdown(db_user_id, months)
                
                return {
                    'type': 'monthly_breakdown',
                    'months': monthly_data,
                    'period': f'Last {months} months',
                    'summary': self._summarize_breakdown(monthly_data)
                }
            
            elif query_type == 'quarterly':
                # Get quarterly breakdown
                quarters = sql_params.get('quarters', 4)
                quarterly_data = self.transaction_store.get_quarterly_breakdown(db_user_id, quarters)
                
                return {
                    'type': 'quarterly_breakdown',
                    'quarters': quarterly_data,
                    'period': f'Last {quarters} quarters',
                    'summary': self._summarize_breakdown(quarterly_data)
                }
            
            elif query_type == 'date_range':
                # Get specific date range
                start_date = sql_params.get('start_date')
                end_date = sql_params.get('end_date')
                
                if start_date and end_date:
                    data = self.transaction_store.get_date_range_summary(
                        db_user_id, start_date, end_date
                    )
                    
                    return {
                        'type': 'single_period',
                        'period': f"{start_date} to {end_date}",
                        'income': float(data['summary'].get('total_income', 0)),
                        'expenses': float(data['summary'].get('total_expenses', 0)),
                        'savings': float(data['summary'].get('savings', 0)),
                        'savings_rate': float(data['summary'].get('savings_rate', 0)),
                        'categories': data['summary'].get('category_breakdown', []),
                        'transaction_count': data['summary'].get('transaction_count', 0),
                        'date_range': f"{start_date} to {end_date}"
                    }
            
            # Fallback: all data
            summary = self.transaction_store.get_financial_summary(db_user_id)
            
            return {
                'type': 'single_period',
                'period': 'All time',
                'income': float(summary.get('total_income', 0)),
                'expenses': float(summary.get('total_expenses', 0)),
                'savings': float(summary.get('savings', 0)),
                'savings_rate': float(summary.get('savings_rate', 0)),
                'categories': summary.get('category_breakdown', []),
                'transaction_count': summary.get('transaction_count', 0)
            }
        
        except Exception as e:
            print(f"Error fetching financial data: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def _summarize_breakdown(self, breakdown_data: List[Dict]) -> Dict:
        """
        Create summary statistics from monthly/quarterly breakdown.
        """
        if not breakdown_data:
            return {}
        
        total_income = sum(d.get('income', 0) for d in breakdown_data)
        total_expenses = sum(d.get('expenses', 0) for d in breakdown_data)
        total_savings = sum(d.get('savings', 0) for d in breakdown_data)
        avg_savings_rate = sum(d.get('savings_rate', 0) for d in breakdown_data) / len(breakdown_data)
        
        # Find best and worst periods
        best_period = max(breakdown_data, key=lambda x: x.get('savings_rate', 0))
        worst_period = min(breakdown_data, key=lambda x: x.get('savings_rate', 0))
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_savings': total_savings,
            'avg_savings_rate': avg_savings_rate,
            'best_period': best_period,
            'worst_period': worst_period,
            'trend': 'improving' if breakdown_data[0]['savings_rate'] > breakdown_data[-1]['savings_rate'] else 'declining'
        }
    
    
    def _generate_response(self, query: str, user_data: Dict, knowledge: List[Dict], 
                          query_analysis: Dict, knowledge_source: str = None) -> str:
        """Generate response using LLM with fetched data and knowledge (with source indicator)."""
        
        if 'error' in user_data:
            return f"I couldn't fetch your financial data: {user_data['error']}. Please make sure you've uploaded bank statements."
        
        # Build context for LLM
        context_parts = []
        
        # Add time period
        context_parts.append(f"Analysis Period: {user_data.get('period', 'Unknown')}")
        context_parts.append(f"User Intent: {query_analysis.get('intent', 'General analysis')}")
        
        # Format data based on type
        if user_data.get('type') == 'monthly_breakdown':
            context_parts.append("\n📊 Monthly Breakdown:")
            for month_data in user_data.get('months', []):
                context_parts.append(
                    f"  {month_data.get('month', 'Unknown')}: "
                    f"Income ₹{month_data.get('income', 0):,.0f} | "
                    f"Expenses ₹{month_data.get('expenses', 0):,.0f} | "
                    f"Savings ₹{month_data.get('savings', 0):,.0f} "
                    f"({month_data.get('savings_rate', 0):.1f}%)"
                )
            
            # Add summary
            summary = user_data.get('summary', {})
            if summary:
                context_parts.append(f"\n📈 Summary:")
                context_parts.append(f"  Total Income: ₹{summary.get('total_income', 0):,.0f}")
                context_parts.append(f"  Total Expenses: ₹{summary.get('total_expenses', 0):,.0f}")
                context_parts.append(f"  Total Savings: ₹{summary.get('total_savings', 0):,.0f}")
                context_parts.append(f"  Avg Savings Rate: {summary.get('avg_savings_rate', 0):.1f}%")
                context_parts.append(f"  Trend: {summary.get('trend', 'stable').title()}")
        
        elif user_data.get('type') == 'quarterly_breakdown':
            context_parts.append("\n📊 Quarterly Breakdown:")
            for quarter_data in user_data.get('quarters', []):
                context_parts.append(
                    f"  {quarter_data.get('period', 'Unknown')}: "
                    f"Income ₹{quarter_data.get('income', 0):,.0f} | "
                    f"Expenses ₹{quarter_data.get('expenses', 0):,.0f} | "
                    f"Savings ₹{quarter_data.get('savings', 0):,.0f} "
                    f"({quarter_data.get('savings_rate', 0):.1f}%)"
                )
            
            # Add summary
            summary = user_data.get('summary', {})
            if summary:
                context_parts.append(f"\n📈 Summary:")
                context_parts.append(f"  Total Savings: ₹{summary.get('total_savings', 0):,.0f}")
                context_parts.append(f"  Avg Savings Rate: {summary.get('avg_savings_rate', 0):.1f}%")
                context_parts.append(f"  Best Quarter: {summary.get('best_period', {}).get('period', 'N/A')}")
                context_parts.append(f"  Trend: {summary.get('trend', 'stable').title()}")
        
        else:
            # Single period
            context_parts.append(f"\n💰 Financial Summary:")
            context_parts.append(f"  Income: ₹{user_data.get('income', 0):,.0f}")
            context_parts.append(f"  Expenses: ₹{user_data.get('expenses', 0):,.0f}")
            context_parts.append(f"  Savings: ₹{user_data.get('savings', 0):,.0f}")
            context_parts.append(f"  Savings Rate: {user_data.get('savings_rate', 0):.1f}%")
            context_parts.append(f"  Transactions: {user_data.get('transaction_count', 0)}")
            
            # Add top categories
            categories = user_data.get('categories', [])
            if categories:
                context_parts.append(f"\n🏷️  Top Spending Categories:")
                for cat in categories[:5]:
                    context_parts.append(f"  • {cat.get('category', 'Unknown')}: ₹{cat.get('amount', 0):,.0f}")
        
        # Add knowledge with source indicator
        if knowledge:
            context_parts.append("\n" + "="*50)
            
            if knowledge_source == 'web_search':
                context_parts.append("🌐 RELEVANT INFORMATION FROM WEB SEARCH (Tavily):")
                context_parts.append("(Real-time, current information from the web)")
            elif knowledge_source == 'knowledge_base':
                context_parts.append("📚 RELEVANT FINANCIAL KNOWLEDGE (Knowledge Base):")
                context_parts.append("(From curated knowledge base)")
            else:
                context_parts.append("📚 RELEVANT FINANCIAL KNOWLEDGE:")
            
            context_parts.append("="*50)
            
            for idx, doc in enumerate(knowledge, 1):
                context_parts.append(f"\n### Source {idx}:")
                
                if knowledge_source == 'web_search':
                    context_parts.append(f"URL: {doc['metadata'].get('source', 'Unknown')}")
                    context_parts.append(f"Title: {doc['metadata'].get('title', 'Untitled')}")
                else:
                    context_parts.append(f"Topic: {doc['metadata'].get('category', 'General')}")
                    context_parts.append(f"Region: {doc['metadata'].get('region', 'Global')}")
                
                context_parts.append(f"Content: {doc['content'][:800]}...")
                context_parts.append("-" * 50)
        
        context = "\n".join(context_parts)
        
        # Enhanced system prompt with source awareness
        system_prompt = f"""You are an expert financial advisor AI. Provide personalized, actionable financial advice.

**CRITICAL INSTRUCTIONS:**
1. **USE THE PROVIDED INFORMATION** - {'Web search results (current, real-time data)' if knowledge_source == 'web_search' else 'Knowledge base information'} provided above
2. **Cite sources** - Reference information naturally (e.g., "According to recent data...", "Based on current guidelines...")
3. **Combine data + knowledge** - Use the user's actual financial data PLUS the provided information
4. **Be specific** - Reference actual rules, limits, and recommendations from the sources
5. **Actionable advice** - Give concrete steps based on both their data and the information provided
6. **Source transparency** - {'Mention that information is from current web sources for credibility' if knowledge_source == 'web_search' else 'Use established financial principles from knowledge base'}

Your analysis should:
- Focus on the specific time period mentioned
- Use actual numbers from the user's data
- Apply provided information to their specific situation
- Give 2-3 specific, actionable recommendations
- Be conversational and supportive

{'**Note:** You are using REAL-TIME web search data to provide current, up-to-date information.' if knowledge_source == 'web_search' else ''}

DO NOT:
- {'Ignore the web search results' if knowledge_source == 'web_search' else 'Ignore the knowledge base'}
- Make up rules or regulations not in the sources
- Give generic advice without using their data
- Ignore the time context"""

        user_prompt = f"""
User Question: {query}

{context}

**Remember:** Use BOTH the user's financial data AND the provided information to give comprehensive, specific advice."""

        # Generate response
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Add source indicator footer
            footer = ""
            if knowledge_source == 'web_search':
                footer = "\n\n---\n*💡 This response includes real-time information from web search (Tavily)*"
            elif knowledge_source == 'knowledge_base':
                footer = "\n\n---\n*📚 This response uses information from the curated knowledge base*"
            
            return response.content + footer
        
        except Exception as e:
            return f"I apologize, but I encountered an error generating insights: {str(e)}. Please try rephrasing your question."

    # Add this to the _analyze_query method in financial_planner_agent.py

    def _analyze_query(self, query: str) -> Dict:
        """
        Use LLM to analyze query and extract structured information.
        """

        analysis_prompt = f"""You are a query analysis agent. Extract structured information from the user's financial query.

        Current date: {datetime.now().strftime('%Y-%m-%d')}

        User query: "{query}"

        Extract the following information and respond ONLY with valid JSON:

        {{
            "intent": "brief description of what user wants to know",
            "time_context": "specific time period",
            "analysis_type": "single_period | monthly_breakdown | quarterly_breakdown | comparison | spending_analysis",
            "needs_knowledge": true/false,
            "knowledge_topics": ["topic1", "topic2"],
            "needs_visualization": true/false,
            "chart_types": ["trend", "pie", "bar"],
            "sql_params": {{
                "type": "latest_month | monthly | quarterly | date_range | all",
                "start_date": "YYYY-MM-DD or null",
                "end_date": "YYYY-MM-DD or null",
                "months": number or null,
                "quarters": number or null
            }}
        }}

        **IMPORTANT:** 
        
        Set analysis_type="spending_analysis" if query involves:
        - "analyze spending", "spending patterns", "where is my money going"
        - "expense breakdown", "spending habits", "expense analysis"
        - Any request to understand or visualize spending behavior
        
        Set needs_visualization=true and include chart_types if query involves:
        - "analyze", "show me", "visualize", "chart", "graph", "trend"
        - Spending patterns or expense analysis
        - Comparisons over time
        
        Chart types:
        - "trend" for time-series analysis (monthly/quarterly trends)
        - "pie" for category breakdowns
        - "bar" for comparisons
        
        Set needs_knowledge=true if query involves:
        - Tax saving, tax optimization, tax deductions
        - Investment advice, investment options, mutual funds, stocks
        - Insurance recommendations
        - Loan decisions (prepay vs invest)
        - Retirement planning
        - Financial concepts or strategies
        - "How to" questions about money

        Set needs_knowledge=false ONLY for:
        - Simple spending analysis
        - Transaction summaries
        - Data queries without advice

        If needs_knowledge=true, identify relevant topics in knowledge_topics array:
        - "tax" for tax-related queries
        - "investment" for investment queries
        - "insurance" for insurance queries
        - "debt" or "loan" for loan queries
        - "planning" for general financial planning

        For spending analysis queries WITHOUT a specific time frame mentioned:
        - Use sql_params.type = "all" to get ALL data
        - Set months = 12 or quarters = 4 for trend charts

        Respond with ONLY the JSON, no explanation."""

        try:
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            
            # Parse JSON response
            response_text = response.content.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            analysis = json.loads(response_text)
            
            # Calculate dates if needed
            if analysis['sql_params']['type'] == 'date_range':
                if not analysis['sql_params']['start_date'] or not analysis['sql_params']['end_date']:
                    analysis['sql_params'] = self._calculate_dates(query, analysis)
            
            return analysis
        
        except Exception as e:
            print(f"Error analyzing query: {e}")
            # Fallback - assume needs knowledge for most queries
            return {
                'intent': 'Financial analysis',
                'time_context': 'latest month',
                'analysis_type': 'single_period',
                'needs_knowledge': True,
                'needs_visualization': False,
                'chart_types': [],
                'knowledge_topics': ['planning'],
                'sql_params': {
                    'type': 'latest_month',
                    'start_date': None,
                    'end_date': None,
                    'months': None,
                    'quarters': None
                }
            }
    
    def _search_knowledge(self, query: str, topics: List[str] = None) -> List[Dict]:
        """
        Search knowledge base for relevant information.
        
        Args:
            query: User query
            topics: List of topic keywords (tax, investment, insurance, etc.)
        """
        if not self.knowledge_store:
            return []
        
        try:
            # Search for each topic
            all_results = []
            
            if topics:
                for topic in topics:
                    results = self.knowledge_store.search_knowledge(
                        query, 
                        category=topic if topic in ['tax', 'investment', 'insurance', 'debt'] else None,
                        top_k=2
                    )
                    all_results.extend(results)
            else:
                # General search
                results = self.knowledge_store.search_knowledge(query, top_k=3)
                all_results.extend(results)
            
            # Remove duplicates
            seen = set()
            unique_results = []
            for r in all_results:
                content_hash = hash(r['content'][:100])  # Use first 100 chars as identifier
                if content_hash not in seen:
                    seen.add(content_hash)
                    unique_results.append(r)
            
            return unique_results[:5]  # Return top 5
        
        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []
        
    def _build_visualizations(self, user_data: Dict, query_analysis: Dict) -> List[Dict]:
        """
        Build visualization charts based on user data and query analysis.
        
        Args:
            user_data: Fetched financial data
            query_analysis: Analyzed query with visualization requirements
            
        Returns:
            List of chart configurations
        """
        charts = []
        
        if not query_analysis.get('needs_visualization', False):
            return charts
        
        chart_types = query_analysis.get('chart_types', [])
        viz_builder = VisualizationBuilder()
        
        # Build trend chart if requested
        if 'trend' in chart_types:
            if user_data.get('type') == 'monthly_breakdown':
                trend_chart = viz_builder.build_spending_trend_chart(user_data.get('months', []))
                if trend_chart:
                    charts.append(trend_chart)
                
                savings_chart = viz_builder.build_savings_rate_bar_chart(user_data.get('months', []))
                if savings_chart:
                    charts.append(savings_chart)
        
        # Build pie chart if requested
        if 'pie' in chart_types:
            categories = user_data.get('categories', [])
            if categories:
                pie_chart = viz_builder.build_category_pie_chart(categories)
                if pie_chart:
                    charts.append(pie_chart)
        
        # Build bar chart if requested
        if 'bar' in chart_types:
            categories = user_data.get('categories', [])
            if categories:
                bar_chart = viz_builder.build_top_expenses_bar_chart(categories)
                if bar_chart:
                    charts.append(bar_chart)
        
        return charts
    
    def get_investment_recommendations(
        self,
        goal_id: str,
        goal_name: str,
        target_amount: float,
        current_balance: float,
        monthly_contribution: float,
        time_horizon_months: int,
        risk_tolerance: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Get investment recommendations for a specific goal.
        
        Args:
            goal_id: Unique goal identifier
            goal_name: Goal name
            target_amount: Target amount for goal
            current_balance: Current saved amount
            monthly_contribution: Monthly SIP amount
            time_horizon_months: Time until goal due date
            risk_tolerance: conservative, balanced, or aggressive
            
        Returns:
            Investment strategy with recommendations
        """
        try:
            from core.investment_options_agent import (
                InvestmentOptionsAgent,
                InvestmentOptionsInput
            )
            
            # Initialize investment agent
            investment_agent = InvestmentOptionsAgent(
                openai_api_key=self.llm.openai_api_key,
                base_url=self.llm.openai_api_base if hasattr(self.llm, 'openai_api_base') else None
            )
            
            # Create input
            investment_input = InvestmentOptionsInput(
                goal_id=goal_id,
                goal_name=goal_name,
                target_amount=target_amount,
                current_balance=current_balance,
                monthly_contribution=monthly_contribution,
                time_horizon_months=time_horizon_months,
                risk_tolerance=risk_tolerance
            )
            
            # Get recommendations
            strategy = investment_agent.recommend(investment_input)
            
            return strategy.model_dump()
        
        except Exception as e:
            print(f"Error getting investment recommendations: {e}")
            return {
                'error': str(e),
                'fallback': 'Consider consulting a financial advisor for personalized investment advice'
            }