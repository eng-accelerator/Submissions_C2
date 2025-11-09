# core/visualization_builder.py
# Generate chart data for frontend visualization

from typing import Dict, List, Any
import json

class VisualizationBuilder:
    """
    Build visualization data structures for Plotly/Chart.js
    """
    
    @staticmethod
    def build_spending_trend_chart(monthly_data: List[Dict]) -> Dict:
        """
        Build monthly spending trend chart data.
        
        Args:
            monthly_data: List of monthly summaries with income, expenses, savings
            
        Returns:
            Chart configuration for Plotly
        """
        if not monthly_data:
            return None
        
        # Sort by month
        sorted_data = sorted(monthly_data, key=lambda x: x.get('month', ''))
        
        months = [d.get('month', 'Unknown') for d in sorted_data]
        income = [d.get('income', 0) for d in sorted_data]
        expenses = [d.get('expenses', 0) for d in sorted_data]
        savings = [d.get('savings', 0) for d in sorted_data]
        
        return {
            'type': 'line',
            'title': 'Income vs Expenses Trend',
            'data': {
                'labels': months,
                'datasets': [
                    {
                        'label': 'Income',
                        'data': income,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    },
                    {
                        'label': 'Expenses',
                        'data': expenses,
                        'borderColor': 'rgb(255, 99, 132)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    },
                    {
                        'label': 'Savings',
                        'data': savings,
                        'borderColor': 'rgb(54, 162, 235)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    }
                ]
            }
        }
    
    @staticmethod
    def build_category_pie_chart(categories: List[Dict]) -> Dict:
        """
        Build category breakdown pie chart.
        
        Args:
            categories: List of category totals with category name and amount
            
        Returns:
            Chart configuration for Plotly
        """
        if not categories:
            return None
        
        # Sort by amount descending
        sorted_categories = sorted(categories, key=lambda x: x.get('amount', 0), reverse=True)
        
        # Take top 10 categories
        top_categories = sorted_categories[:10]
        
        labels = [c.get('category', 'Unknown').replace('_', ' ').title() for c in top_categories]
        values = [c.get('amount', 0) for c in top_categories]
        
        return {
            'type': 'pie',
            'title': 'Spending by Category',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': values,
                    'backgroundColor': [
                        'rgb(255, 99, 132)',
                        'rgb(54, 162, 235)',
                        'rgb(255, 206, 86)',
                        'rgb(75, 192, 192)',
                        'rgb(153, 102, 255)',
                        'rgb(255, 159, 64)',
                        'rgb(199, 199, 199)',
                        'rgb(83, 102, 255)',
                        'rgb(255, 99, 255)',
                        'rgb(99, 255, 132)'
                    ]
                }]
            }
        }
    
    @staticmethod
    def build_savings_rate_bar_chart(breakdown_data: List[Dict]) -> Dict:
        """
        Build savings rate comparison bar chart.
        
        Args:
            breakdown_data: Monthly or quarterly breakdown with savings rates
            
        Returns:
            Chart configuration
        """
        if not breakdown_data:
            return None
        
        # Sort by period
        sorted_data = sorted(breakdown_data, key=lambda x: x.get('month', x.get('period', '')))
        
        labels = [d.get('month', d.get('period', 'Unknown')) for d in sorted_data]
        savings_rates = [d.get('savings_rate', 0) for d in sorted_data]
        
        return {
            'type': 'bar',
            'title': 'Savings Rate Over Time',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Savings Rate (%)',
                    'data': savings_rates,
                    'backgroundColor': 'rgba(75, 192, 192, 0.6)',
                    'borderColor': 'rgb(75, 192, 192)',
                    'borderWidth': 1
                }]
            }
        }
    
    @staticmethod
    def build_top_expenses_bar_chart(categories: List[Dict], limit: int = 10) -> Dict:
        """
        Build top expenses bar chart.
        
        Args:
            categories: List of category totals
            limit: Number of top categories to show
            
        Returns:
            Chart configuration
        """
        if not categories:
            return None
        
        # Sort by amount descending
        sorted_categories = sorted(categories, key=lambda x: x.get('amount', 0), reverse=True)[:limit]
        
        labels = [c.get('category', 'Unknown').replace('_', ' ').title() for c in sorted_categories]
        values = [c.get('amount', 0) for c in sorted_categories]
        
        return {
            'type': 'bar',
            'title': f'Top {limit} Spending Categories',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Amount Spent (₹)',
                    'data': values,
                    'backgroundColor': 'rgba(255, 99, 132, 0.6)',
                    'borderColor': 'rgb(255, 99, 132)',
                    'borderWidth': 1
                }]
            },
            'options': {
                'indexAxis': 'y',  # Horizontal bars
            }
        }