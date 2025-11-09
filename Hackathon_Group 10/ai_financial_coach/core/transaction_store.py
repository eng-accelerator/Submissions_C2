# core/transaction_store.py
# Database wrapper for transaction storage (SQLite/PostgreSQL)

from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import sqlite3
import json
import psycopg2
from psycopg2.extras import RealDictCursor

class TransactionStore:
    """
    Database wrapper for transaction storage.
    Supports both SQLite (for demo) and PostgreSQL (for production).
    """
    
    def __init__(self, connection_string: str):
        """
        Args:
            connection_string: 
                - SQLite: "sqlite:///./database.db"
                - PostgreSQL: "postgresql://user:pass@localhost:5432/dbname"
        """
        self.connection_string = connection_string
        
        if connection_string.startswith("sqlite"):
            # SQLite mode
            self.db_path = connection_string.replace("sqlite:///", "")
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.db_type = "sqlite"
        else:
            # PostgreSQL mode (requires psycopg2)
            try:
                
                self.conn = psycopg2.connect(connection_string)
                self.cursor_factory = RealDictCursor
                self.db_type = "postgres"
            except ImportError:
                raise ImportError("Please install psycopg2: pip install psycopg2-binary")
        
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            country TEXT DEFAULT 'India',
            currency TEXT DEFAULT 'INR',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Transactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            transaction_date DATE NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            balance REAL,
            description TEXT,
            category TEXT,
            mode TEXT,
            reference_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        
        # Create indexes
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_date 
        ON transactions(user_id, transaction_date DESC)
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_type 
        ON transactions(user_id, transaction_type)
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_category 
        ON transactions(user_id, category)
        """)
        
        self.conn.commit()
    
    def add_user(self, username: str, email: str = None, 
                 country: str = "India", currency: str = "INR") -> str:
        """Create user and return user_id."""
        import uuid
        user_id = str(uuid.uuid4())
        
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO users (user_id, username, email, country, currency)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, email, country, currency))
            
            self.conn.commit()
            return user_id
        
        except sqlite3.IntegrityError:
            # User already exists, return existing user_id
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_user_id(self, username: str) -> Optional[str]:
        """Get user_id from username."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def bulk_insert_transactions(self, user_id: str, transactions: List[Dict]):
        """
        Bulk insert transactions.
        
        Args:
            user_id: User UUID
            transactions: List of transaction dicts from parser
        """
        if not transactions:
            return
        
        import uuid
        cursor = self.conn.cursor()
        
        for txn in transactions:
            transaction_id = str(uuid.uuid4())
            
            cursor.execute("""
            INSERT INTO transactions 
            (transaction_id, user_id, transaction_date, amount, transaction_type,
             balance, description, category, mode, reference_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                user_id,
                txn.get('date'),
                float(txn.get('amount', 0)),
                txn.get('type', 'debit'),
                float(txn.get('balance')) if txn.get('balance') else None,
                txn.get('description', ''),
                txn.get('category', 'others'),
                txn.get('mode', ''),
                txn.get('reference', '')
            ))
        
        self.conn.commit()
    
    def get_financial_summary(self, user_id: str, 
                             start_date: str = None, 
                             end_date: str = None) -> Dict:
        """
        Get financial summary for user.
        Returns aggregated metrics.
        """
        cursor = self.conn.cursor()
        
        date_filter = ""
        params = [user_id]
        
        if start_date and end_date:
            date_filter = "AND transaction_date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        # Total income and expenses
        cursor.execute(f"""
        SELECT 
            SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as total_expenses,
            COUNT(*) as transaction_count,
            MIN(transaction_date) as start_date,
            MAX(transaction_date) as end_date
        FROM transactions
        WHERE user_id = ? {date_filter}
        """, params)
        
        row = cursor.fetchone()
        
        if self.db_type == "sqlite":
            summary = {
                'total_income': row[0] or 0,
                'total_expenses': row[1] or 0,
                'transaction_count': row[2] or 0,
                'start_date': row[3],
                'end_date': row[4]
            }
        else:
            summary = dict(row)
        
        # Calculate derived metrics
        income = float(summary['total_income'] or 0)
        expenses = float(summary['total_expenses'] or 0)
        
        summary['savings'] = income - expenses
        summary['savings_rate'] = (summary['savings'] / income * 100) if income > 0 else 0
        
        # Category breakdown
        cursor.execute(f"""
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE user_id = ? AND transaction_type = 'debit' {date_filter}
        GROUP BY category
        ORDER BY total DESC
        """, params)
        
        summary['category_breakdown'] = [
            {'category': row[0], 'amount': float(row[1])}
            for row in cursor.fetchall()
        ]
        
        # Mode breakdown
        cursor.execute(f"""
        SELECT mode, COUNT(*) as count
        FROM transactions
        WHERE user_id = ? {date_filter}
        GROUP BY mode
        ORDER BY count DESC
        """, params)
        
        summary['mode_breakdown'] = [
            {'mode': row[0], 'count': row[1]}
            for row in cursor.fetchall()
        ]
        
        # Latest balance
        cursor.execute("""
        SELECT balance, transaction_date
        FROM transactions
        WHERE user_id = ? AND balance IS NOT NULL
        ORDER BY transaction_date DESC
        LIMIT 1
        """, [user_id])
        
        balance_row = cursor.fetchone()
        if balance_row:
            summary['latest_balance'] = float(balance_row[0])
            summary['balance_date'] = balance_row[1]
        
        return summary
    
    def get_monthly_trend(self, user_id: str, months: int = 12) -> pd.DataFrame:
        """Get monthly income/expense trend."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT 
            strftime('%Y-%m', transaction_date) as month,
            SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as expenses
        FROM transactions
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', transaction_date)
        ORDER BY month DESC
        LIMIT ?
        """, (user_id, months))
        
        data = cursor.fetchall()
        
        return pd.DataFrame(data, columns=['month', 'income', 'expenses'])
    
    def search_transactions(self, user_id: str, 
                           query: str = None,
                           category: str = None,
                           min_amount: float = None,
                           max_amount: float = None,
                           start_date: str = None,
                           end_date: str = None,
                           limit: int = 100) -> List[Dict]:
        """Search transactions with filters."""
        cursor = self.conn.cursor()
        
        conditions = ["user_id = ?"]
        params = [user_id]
        
        if query:
            conditions.append("description LIKE ?")
            params.append(f"%{query}%")
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if min_amount:
            conditions.append("amount >= ?")
            params.append(min_amount)
        
        if max_amount:
            conditions.append("amount <= ?")
            params.append(max_amount)
        
        if start_date:
            conditions.append("transaction_date >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("transaction_date <= ?")
            params.append(end_date)
        
        where_clause = " AND ".join(conditions)
        
        cursor.execute(f"""
        SELECT *
        FROM transactions
        WHERE {where_clause}
        ORDER BY transaction_date DESC
        LIMIT ?
        """, params + [limit])
        
        columns = [desc[0] for desc in cursor.description]
        
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
    def get_category_totals(self, user_id: str, 
                           start_date: str = None,
                           end_date: str = None) -> List[Dict]:
        """Get spending by category."""
        cursor = self.conn.cursor()
        
        date_filter = ""
        params = [user_id]
        
        if start_date and end_date:
            date_filter = "AND transaction_date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        cursor.execute(f"""
        SELECT 
            category,
            SUM(amount) as total_amount,
            COUNT(*) as transaction_count,
            AVG(amount) as avg_amount
        FROM transactions
        WHERE user_id = ? 
            AND transaction_type = 'debit'
            {date_filter}
        GROUP BY category
        ORDER BY total_amount DESC
        """, params)
        
        columns = [desc[0] for desc in cursor.description]
        
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
    def close(self):
        """Close database connection."""
        self.conn.close()

    
    def get_latest_month_transactions(self, user_id: str) -> Dict:
        """
        Get transactions and summary for the most recent month with data.
        
        Returns:
            Dict with transactions and summary for latest month
        """
        cursor = self.conn.cursor()
        
        # Find the most recent month with transactions
        cursor.execute("""
        SELECT 
            MAX(strftime('%Y-%m', transaction_date)) as latest_month
        FROM transactions
        WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        latest_month = result[0] if result else None
        
        if not latest_month:
            return {
                'transactions': [], 
                'summary': {
                    'total_income': 0,
                    'total_expenses': 0,
                    'savings': 0,
                    'savings_rate': 0,
                    'transaction_count': 0,
                    'category_breakdown': []
                }, 
                'period': 'No data',
                'start_date': None,
                'end_date': None
            }
        
        # Get start and end dates for that month
        year, month = latest_month.split('-')
        start_date = f"{year}-{month}-01"
        
        # Calculate end date (last day of month)
        import calendar
        last_day = calendar.monthrange(int(year), int(month))[1]
        end_date = f"{year}-{month}-{last_day:02d}"
        
        # Get transactions for that month
        transactions = self.search_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Get summary for that month
        summary = self.get_financial_summary(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Format period name
        month_name = calendar.month_name[int(month)]
        
        return {
            'transactions': transactions,
            'summary': summary,
            'period': f"{month_name} {year}",
            'start_date': start_date,
            'end_date': end_date
        }
    
    def get_date_range_summary(self, user_id: str, start_date: str, end_date: str) -> Dict:
        """
        Get summary for specific date range.
        
        Args:
            user_id: User UUID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dict with summary and transactions
        """
        transactions = self.search_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=5000
        )
        
        summary = self.get_financial_summary(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            'transactions': transactions,
            'summary': summary,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def get_monthly_breakdown(self, user_id: str, months: int = 6) -> List[Dict]:
        """
        Get month-by-month breakdown for last N months.
        
        Args:
            user_id: User UUID
            months: Number of months to retrieve
            
        Returns:
            List of monthly summaries
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT 
            strftime('%Y-%m', transaction_date) as month,
            SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as expenses,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', transaction_date)
        ORDER BY month DESC
        LIMIT ?
        """, (user_id, months))
        
        results = []
        for row in cursor.fetchall():
            month_str = row[0]
            income = float(row[1] or 0)
            expenses = float(row[2] or 0)
            savings = income - expenses
            
            results.append({
                'month': month_str,
                'income': income,
                'expenses': expenses,
                'savings': savings,
                'savings_rate': (savings / income * 100) if income > 0 else 0,
                'transaction_count': row[3]
            })
        
        return results
    
    def get_quarterly_breakdown(self, user_id: str, quarters: int = 4) -> List[Dict]:
        """
        Get quarter-by-quarter breakdown.
        
        Args:
            user_id: User UUID
            quarters: Number of quarters to retrieve
            
        Returns:
            List of quarterly summaries
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT 
            strftime('%Y', transaction_date) as year,
            CASE 
                WHEN CAST(strftime('%m', transaction_date) AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1'
                WHEN CAST(strftime('%m', transaction_date) AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2'
                WHEN CAST(strftime('%m', transaction_date) AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3'
                ELSE 'Q4'
            END as quarter,
            SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as expenses,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE user_id = ?
        GROUP BY year, quarter
        ORDER BY year DESC, quarter DESC
        LIMIT ?
        """, (user_id, quarters))
        
        results = []
        for row in cursor.fetchall():
            year = row[0]
            quarter = row[1]
            income = float(row[2] or 0)
            expenses = float(row[3] or 0)
            savings = income - expenses
            
            results.append({
                'period': f"{quarter} {year}",
                'year': year,
                'quarter': quarter,
                'income': income,
                'expenses': expenses,
                'savings': savings,
                'savings_rate': (savings / income * 100) if income > 0 else 0,
                'transaction_count': row[4]
            })
        
        return results
