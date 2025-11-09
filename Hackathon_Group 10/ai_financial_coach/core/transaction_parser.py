"""
Intelligent CSV/Excel Parser for Bank Statements
Uses rule-based column detection - NO LLMs needed
"""

import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import numpy as np


class BankStatementParser:
    """
    Intelligent parser that auto-detects bank statement columns
    Works with any CSV/Excel format without hardcoding
    """
    
    def __init__(self):
        # Column detection patterns
        self.date_keywords = [
            'date', 'dt', 'transaction date', 'trans date', 'posting date',
            'value date', 'txn date', 'timestamp', 'txndate', 'valuedate',
            'tran date', 'posting dt', 'value dt'
        ]
        
        self.amount_keywords = [
            'amount', 'amt', 'value', 'transaction amount', 'txn amount',
            'debit', 'credit', 'withdrawal', 'deposit', 'balance',
            'dr', 'cr', 'drcr'
        ]
        
        self.description_keywords = [
            'description', 'desc', 'narration', 'particulars', 'details',
            'remarks', 'transaction details', 'txn details', 'reference',
            'narr', 'transaction description', 'merchant', 'transaction particulars',
            'narration/particulars'
        ]
        
        self.balance_keywords = [
            'balance', 'closing balance', 'available balance', 'bal',
            'running balance', 'current balance', 'account balance'
        ]
        
        self.mode_keywords = [
            'mode', 'type', 'transaction type', 'txn type', 'payment mode',
            'channel', 'transaction mode', 'payment method', 'method'
        ]
        
        self.name_keywords = [
            'name', 'party name', 'counterparty', 'beneficiary', 'payee',
            'merchant', 'vendor'
        ]
        
        self.reference_keywords = [
            'reference', 'ref', 'cheque', 'chq', 'cheque number', 'ref no',
            'reference number', 'transaction id', 'txn id', 'utr', 'rrn',
            'cheque no', 'instrument number', 'chq no'
        ]
        
        # Date format patterns
        self.date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d',
            '%m/%d/%Y', '%m-%d-%Y', '%d.%m.%Y', '%d %b %Y',
            '%d-%b-%Y', '%d %B %Y', '%d-%B-%Y', '%Y%m%d'
        ]
    
    def detect_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detect date column by keyword and data type"""
        # Normalize column names to lowercase for comparison
        col_map = {col: str(col).lower().strip() for col in df.columns}
        
        for col, col_lower in col_map.items():
            # Check keyword match
            if any(keyword in col_lower for keyword in self.date_keywords):
                # Verify it contains date-like values
                if self._is_date_column(df[col]):
                    return col
        
        # Fallback: check all columns for date-like data
        for col in df.columns:
            if self._is_date_column(df[col]):
                return col
        
        return None
    
    def detect_amount_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Detect amount columns (debit, credit, or combined)
        Returns: {'debit': col_name, 'credit': col_name} or {'amount': col_name}
        """
        result = {}
        
        # Normalize column names
        col_map = {col: str(col).lower().strip() for col in df.columns}
        
        # PRIORITY 1: Look for DrCr or combined Dr/Cr column first
        for col, col_lower in col_map.items():
            if col_lower in ['drcr', 'dr cr', 'dr/cr', 'drcr']:
                # This is a combined column with Db/Cr indicators
                if self._is_drcr_indicator_column(df[col]):
                    result['drcr_indicator'] = col
                    print(f"  Found DrCr indicator column: {col}")
                    break
        
        # PRIORITY 2: Look for explicit debit/credit columns
        for col, col_lower in col_map.items():
            # Check for debit column - including Dr variations
            if (col_lower in ['dr', 'debit', 'withdrawal', 'withdrawals', 'dr.'] or 
                'debit' in col_lower or 'withdrawal' in col_lower):
                if self._is_numeric_column(df[col]):
                    result['debit'] = col
            
            # Check for credit column - including Cr variations
            elif (col_lower in ['cr', 'credit', 'deposit', 'deposits', 'cr.'] or
                  'credit' in col_lower or 'deposit' in col_lower):
                if self._is_numeric_column(df[col]):
                    result['credit'] = col
        
        # PRIORITY 3: Look for amount column (only if no DrCr indicator found)
        if 'drcr_indicator' not in result and not result:
            for col, col_lower in col_map.items():
                if any(keyword in col_lower for keyword in ['amount', 'amt', 'value', 'transaction']):
                    if self._is_numeric_column(df[col]) and 'balance' not in col_lower:
                        result['amount'] = col
                        break
        
        # Fallback: find numeric columns (excluding balance)
        if not result:
            for col in df.columns:
                col_lower = str(col).lower().strip()
                if 'balance' not in col_lower and self._is_numeric_column(df[col]):
                    result['amount'] = col
                    break
        
        return result
    
    def detect_description_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detect description/narration column"""
        col_map = {col: str(col).lower().strip() for col in df.columns}
        
        # First pass: look for explicit description keywords
        for col, col_lower in col_map.items():
            if any(keyword in col_lower for keyword in self.description_keywords):
                # Make sure it's not a date column
                if not any(date_kw in col_lower for date_kw in ['date', 'dt']):
                    return col
        
        # Fallback: find longest text column that's not date/balance/amount
        text_cols = []
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            # Skip if it's a date, balance, or amount column
            if any(skip in col_lower for skip in ['date', 'dt', 'balance', 'amount', 'dr', 'cr']):
                continue
            
            if df[col].dtype == 'object':
                avg_len = df[col].astype(str).str.len().mean()
                if avg_len > 3:  # Ignore very short columns
                    text_cols.append((col, avg_len))
        
        if text_cols:
            text_cols.sort(key=lambda x: x[1], reverse=True)
            return text_cols[0][0]
        
        return None
    
    def detect_balance_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detect balance column"""
        col_map = {col: str(col).lower().strip() for col in df.columns}
        
        for col, col_lower in col_map.items():
            if any(keyword in col_lower for keyword in self.balance_keywords):
                if self._is_numeric_column(df[col]):
                    return col
        
        return None
    
    def detect_mode_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detect transaction mode/type column"""
        col_map = {col: str(col).lower().strip() for col in df.columns}
        
        for col, col_lower in col_map.items():
            if any(keyword in col_lower for keyword in self.mode_keywords):
                return col
        
        return None
    
    def detect_name_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detect party/merchant name column"""
        col_map = {col: str(col).lower().strip() for col in df.columns}
        
        for col, col_lower in col_map.items():
            if any(keyword in col_lower for keyword in self.name_keywords):
                return col
        
        return None
    
    def detect_reference_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detect reference/cheque number column"""
        col_map = {col: str(col).lower().strip() for col in df.columns}
        
        for col, col_lower in col_map.items():
            if any(keyword in col_lower for keyword in self.reference_keywords):
                return col
        
        return None
    
    def detect_value_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detect value date column (separate from transaction date)"""
        col_map = {col: str(col).lower().strip() for col in df.columns}
        
        for col, col_lower in col_map.items():
            if 'value date' in col_lower or 'value dt' in col_lower:
                if self._is_date_column(df[col]):
                    return col
        
        return None
    
    def extract_summary_info(self, df: pd.DataFrame, balance_col: Optional[str]) -> Dict:
        """
        Extract opening and closing balance from statement
        
        Args:
            df: DataFrame with transactions
            balance_col: Name of balance column
            
        Returns:
            Dictionary with opening_balance and closing_balance
        """
        summary = {
            'opening_balance': None,
            'closing_balance': None
        }
        
        if balance_col and balance_col in df.columns:
            try:
                # Get first and last non-null balance values
                balances = df[balance_col].dropna()
                
                if len(balances) > 0:
                    # First balance might be opening + transaction
                    # Last balance is closing
                    first_balance = self._parse_amount(str(balances.iloc[0]))
                    last_balance = self._parse_amount(str(balances.iloc[-1]))
                    
                    summary['opening_balance'] = first_balance
                    summary['closing_balance'] = last_balance
            except:
                pass
        
        return summary
    
    def _normalize_transaction_mode(self, mode: str) -> str:
        """
        Normalize transaction mode to standard categories
        
        Args:
            mode: Raw mode value from CSV
            
        Returns:
            Normalized mode category
        """
        if not mode or pd.isna(mode):
            return 'unknown'
        
        mode_lower = str(mode).lower().strip()
        
        # Define mode mappings
        mode_map = {
            'atm': ['atm', 'cash withdrawal', 'atm withdrawal', 'atm-'],
            'upi': ['upi', 'unified payment', 'bhim', 'paytm', 'phonepe', 'gpay', 'googlepay', 'upi/'],
            'neft': ['neft', 'national electronic'],
            'imps': ['imps', 'immediate payment'],
            'rtgs': ['rtgs', 'real time gross'],
            'cheque': ['cheque', 'check', 'chq', 'cheq', 'cheque deposit', 'cheque payment'],
            'debit_card': ['debit card', 'dc', 'pos', 'card purchase', 'card payment', 'pos purchase'],
            'credit_card': ['credit card', 'cc'],
            'net_banking': ['net banking', 'online', 'internet banking', 'netbanking'],
            'mobile_banking': ['mobile banking', 'mobile', 'mobile app'],
            'cash': ['cash', 'cash deposit', 'cash deposit at branch'],
            'emi': ['emi', 'equated monthly installment'],
            'auto_debit': ['auto debit', 'standing instruction', 'autopay', 'mandate', 'si'],
            'transfer': ['transfer', 'fund transfer', 'self transfer', 'own account transfer'],
            'bill_payment': ['bill payment', 'bill pay', 'utility payment'],
            'interest': ['interest', 'interest paid', 'interest credit', 'interest earned'],
            'charges': ['service charge', 'bank charge', 'fee', 'penalty', 'charges'],
            'salary': ['salary', 'sal credit', 'salary credit'],
            'dividend': ['dividend', 'dividend credit'],
            'refund': ['refund', 'refund credit', 'reversal'],
        }
        
        for category, keywords in mode_map.items():
            if any(keyword in mode_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _infer_mode_from_description(self, description: str) -> str:
        """
        Infer transaction mode from description text when mode column is not available
        
        Args:
            description: Transaction description
            
        Returns:
            Inferred transaction mode
        """
        if not description or pd.isna(description):
            return 'unknown'
        
        desc_lower = str(description).lower().strip()
        
        # Check for mode indicators in description
        mode_patterns = {
            'atm': ['atm', 'atm-', 'cash withdrawal', 'atm withdrawal', 'atm wdl'],
            'upi': ['upi/', 'upi-', 'paytm', 'phonepe', 'gpay', 'googlepay', 'bhim', 'upi '],
            'neft': ['neft', 'neft-', 'neft/'],
            'imps': ['imps', 'imps-', 'imps/'],
            'rtgs': ['rtgs', 'rtgs-', 'rtgs/'],
            'cheque': ['cheque', 'chq', 'chq-', 'cheq', 'clg', 'clearing'],
            'debit_card': ['pos', 'card purchase', 'card-', 'debit card', 'dc-'],
            'net_banking': ['netbanking', 'net banking', 'online transfer', 'internet banking'],
            'emi': ['emi', 'emi-', 'emi/'],
            'auto_debit': ['auto debit', 'standing instruction', 'autopay', 'si-', 'mandate'],
            'bill_payment': ['bill payment', 'bill pay', 'utility'],
            'interest': ['interest', 'int.pd', 'int paid', 'int credit', 'interest earned'],
            'charges': ['service charge', 'bank charge', 'fee', 'penalty', 'charges', 'sms charge'],
            'salary': ['salary', 'sal credit', 'sal cr'],
            'dividend': ['dividend', 'div credit'],
            'refund': ['refund', 'refund credit', 'reversal', 'chargeback'],
        }
        
        for mode, patterns in mode_patterns.items():
            if any(pattern in desc_lower for pattern in patterns):
                return mode
        
        return 'other'
    
    def _is_date_column(self, series: pd.Series) -> bool:
        """Check if series contains date-like values"""
        sample = series.dropna().head(10)
        
        if len(sample) == 0:
            return False
        
        date_count = 0
        for value in sample:
            if self._parse_date(str(value)) is not None:
                date_count += 1
        
        return date_count >= len(sample) * 0.7  # 70% threshold
    
    def _is_numeric_column(self, series: pd.Series) -> bool:
        """Check if series contains numeric values"""
        if pd.api.types.is_numeric_dtype(series):
            return True
        
        # Try parsing as numeric
        sample = series.dropna().head(10)
        if len(sample) == 0:
            return False
        
        numeric_count = 0
        for value in sample:
            if self._parse_amount(str(value)) is not None:
                numeric_count += 1
        
        return numeric_count >= len(sample) * 0.7
    
    def _is_drcr_indicator_column(self, series: pd.Series) -> bool:
        """Check if column contains Db/Cr indicators"""
        sample = series.dropna().head(20)
        if len(sample) == 0:
            return False
        
        indicator_count = 0
        for value in sample:
            val_str = str(value).strip().lower()
            if val_str in ['db', 'cr', 'dr', 'deb', 'cre']:
                indicator_count += 1
        
        return indicator_count >= len(sample) * 0.5  # 50% threshold
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Try to parse date string using multiple formats"""
        date_str = str(date_str).strip()
        
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # Try pandas parser as fallback
        try:
            return pd.to_datetime(date_str)
        except:
            return None
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to float"""
        if pd.isna(amount_str):
            return None
        
        amount_str = str(amount_str).strip()
        
        # Remove currency symbols and commas
        amount_str = re.sub(r'[₹$£€,\s]', '', amount_str)
        
        # Remove parentheses (sometimes used for negative)
        if '(' in amount_str and ')' in amount_str:
            amount_str = amount_str.replace('(', '-').replace(')', '')
        
        try:
            return float(amount_str)
        except:
            return None
    
    def parse_statement(self, df: pd.DataFrame, debug: bool = False) -> List[Dict]:
        """
        Parse bank statement DataFrame into transactions.
        
        Args:
            df: DataFrame containing bank statement
            debug: If True, print debug information
            
        Returns:
            List of transaction dictionaries
        """
        if debug:
            print("\n" + "="*50)
            print("DEBUG: Starting parse_statement")
            print("="*50)
            print(f"DataFrame shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"\nFirst 3 rows:")
            print(df.head(3))
        
        # Detect columns
        date_col = self.detect_date_column(df)
        amount_cols = self.detect_amount_columns(df)
        description_col = self.detect_description_column(df)
        balance_col = self.detect_balance_column(df)
        mode_col = self.detect_mode_column(df)
        reference_col = self.detect_reference_column(df)
        
        if debug:
            print(f"\nDetected columns:")
            print(f"  Date: {date_col}")
            print(f"  Amount: {amount_cols}")
            print(f"  Description: {description_col}")
            print(f"  Balance: {balance_col}")
            print(f"  Mode: {mode_col}")
            print(f"  Reference: {reference_col}")
        
        if not date_col:
            print("ERROR: Could not detect date column")
            return []
        
        if not amount_cols:
            print("ERROR: Could not detect amount columns")
            return []
        
        transactions = []
        
        # Parse each row
        for idx, row in df.iterrows():
            if debug and idx < 3:
                print(f"\n--- Processing row {idx} ---")
                print(row.to_dict())
            
            try:
                # Parse date
                date_val = row[date_col]
                
                if debug and idx < 3:
                    print(f"  Date value: {date_val}")
                
                parsed_date = self._parse_date(str(date_val))
                
                if not parsed_date:
                    if debug and idx < 3:
                        print(f"  ❌ Could not parse date: {date_val}")
                    continue
                
                if debug and idx < 3:
                    print(f"  ✅ Parsed date: {parsed_date}")
                
                # Parse amount and determine type
                amount = None
                trans_type = None
                
                # Handle different amount column formats
                if 'drcr_indicator' in amount_cols:
                    # DrCr indicator column
                    drcr_col = amount_cols['drcr_indicator']
                    indicator = str(row[drcr_col]).strip().upper()
                    
                    if debug and idx < 3:
                        print(f"  DrCr indicator: {indicator}")
                    
                    # Find amount column
                    amount_col = None
                    for col in df.columns:
                        col_lower = str(col).lower().strip()
                        if col_lower in ['amount', 'amt', 'value'] or 'amount' in col_lower:
                            if col != drcr_col and self._is_numeric_column(df[col]):
                                amount_col = col
                                break
                    
                    if not amount_col:
                        # Try any numeric column
                        for col in df.columns:
                            if col != drcr_col and col != balance_col and self._is_numeric_column(df[col]):
                                amount_col = col
                                break
                    
                    if amount_col:
                        amount = self._parse_amount(row[amount_col])
                        
                        if debug and idx < 3:
                            print(f"  Amount column: {amount_col}")
                            print(f"  Amount value: {row[amount_col]} → {amount}")
                        
                        # Determine type from indicator
                        if indicator in ['DB', 'DR', 'DEB', 'DEBIT', 'D']:
                            trans_type = 'debit'
                        elif indicator in ['CR', 'CRE', 'CREDIT', 'C']:
                            trans_type = 'credit'
                        else:
                            if debug and idx < 3:
                                print(f"  ❌ Unknown indicator: {indicator}")
                            continue
                    else:
                        if debug and idx < 3:
                            print(f"  ❌ Could not find amount column")
                        continue
                
                elif 'debit' in amount_cols and 'credit' in amount_cols:
                    # Separate debit/credit columns
                    debit_val = row[amount_cols['debit']]
                    credit_val = row[amount_cols['credit']]
                    
                    if debug and idx < 3:
                        print(f"  Debit: {debit_val}, Credit: {credit_val}")
                    
                    debit = self._parse_amount(str(debit_val)) if pd.notna(debit_val) else None
                    credit = self._parse_amount(str(credit_val)) if pd.notna(credit_val) else None
                    
                    if debit and debit > 0:
                        amount = debit
                        trans_type = 'debit'
                    elif credit and credit > 0:
                        amount = credit
                        trans_type = 'credit'
                    else:
                        if debug and idx < 3:
                            print(f"  ❌ Both debit and credit are empty/zero")
                        continue
                
                else:
                    # Combined amount column
                    amount = self._parse_amount(row[amount_cols['amount']])
                    
                    if debug and idx < 3:
                        print(f"  Amount: {amount}")
                    
                    if amount is None or amount == 0:
                        if debug and idx < 3:
                            print(f"  ❌ Amount is None or zero")
                        continue
                    
                    # Determine type based on sign
                    if amount < 0:
                        trans_type = 'debit'
                        amount = abs(amount)
                    else:
                        trans_type = 'credit'
                
                if not amount or not trans_type:
                    if debug and idx < 3:
                        print(f"  ❌ Missing amount or type")
                    continue
                
                # Build transaction dict
                transaction = {
                    'date': parsed_date,
                    'amount': str(amount),
                    'type': trans_type,
                    'description': str(row[description_col]) if description_col and pd.notna(row[description_col]) else '',
                    'balance': str(self._parse_amount(row[balance_col])) if balance_col and pd.notna(row[balance_col]) else None,
                    'mode': self._normalize_transaction_mode(str(row[mode_col])) if mode_col and pd.notna(row[mode_col]) else '',
                    'reference': str(row[reference_col]) if reference_col and pd.notna(row[reference_col]) else '',
                }
                
                transactions.append(transaction)
                
                if debug and idx < 3:
                    print(f"  ✅ Transaction added: {transaction}")
            
            except Exception as e:
                if debug:
                    print(f"  ❌ Error processing row {idx}: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
                continue
        
        if debug:
            print(f"\n{'='*50}")
            print(f"Total transactions parsed: {len(transactions)}")
            print(f"{'='*50}\n")
        
        return transactions

    def validate_transactions(self, transactions: List[Dict]) -> Tuple[bool, str]:
        """Validate parsed transactions"""
        if not transactions:
            return False, "No transactions found in file"
        
        if len(transactions) < 3:
            return False, f"Too few transactions found ({len(transactions)}). File may not be a valid bank statement."
        
        # Check date range
        dates = [datetime.strptime(t['date'], '%d/%m/%Y') for t in transactions]
        date_range = (max(dates) - min(dates)).days
        
        if date_range > 730:  # More than 2 years
            return False, "Date range suspiciously large. Please check file format."
        
        return True, f"Successfully parsed {len(transactions)} transactions"


    def parse_csv_file(file, filename: str) -> List[Dict]:
        """Parse CSV file using intelligent parser"""
        try:
            df = pd.read_csv(file)
            parser = BankStatementParser()
            transactions = parser.parse_statement(df)
            
            is_valid, message = parser.validate_transactions(transactions)
            if not is_valid:
                raise ValueError(message)
            
            return transactions
        except Exception as e:
            raise Exception(f"Error parsing CSV: {str(e)}")


    def parse_excel_file(file, filename: str) -> List[Dict]:
        """Parse Excel file using intelligent parser"""
        try:
            # Try to read first sheet
            df = pd.read_excel(file, sheet_name=0)
            
            # Skip empty rows at the beginning
            for i in range(len(df)):
                if df.iloc[i].notna().sum() > 2:  # Found row with data
                    df = pd.read_excel(file, sheet_name=0, skiprows=i)
                    break
            
            parser = BankStatementParser()
            transactions = parser.parse_statement(df)
            
            is_valid, message = parser.validate_transactions(transactions)
            if not is_valid:
                raise ValueError(message)
            
            return transactions
        except Exception as e:
            raise Exception(f"Error parsing Excel: {str(e)}")
        

    def parse_to_dict(self, file) -> List[Dict]:
            """
            Parse uploaded file and return list of transaction dictionaries.
            This is the main entry point called by app.py.
            
            Args:
                file: Streamlit uploaded file object (CSV, Excel, or PDF)
                
            Returns:
                List of transaction dictionaries ready for database insertion
                
            Example return format:
            [
                {
                    'date': '01/01/2024',
                    'amount': '10000.0',
                    'type': 'debit',
                    'description': 'ATM Withdrawal',
                    'balance': '90000.0',
                    'mode': 'atm',
                    'reference': 'TXN123456',
                    'category': 'cash_withdrawal'
                },
                ...
            ]
            """
            import pandas as pd
            import os
            
            # Get file extension
            filename = file.name if hasattr(file, 'name') else 'unknown'
            file_ext = os.path.splitext(filename)[1].lower()
            
            print(f"\n📄 Processing file: {filename}")
            print(f"   Extension: {file_ext}")
            
            # Read file into DataFrame based on type
            try:
                if file_ext == '.csv':
                    df = pd.read_csv(file)
                    print(f"   ✅ Read CSV file: {len(df)} rows")
                
                elif file_ext in ['.xlsx', '.xls']:
                    df = pd.read_excel(file)
                    print(f"   ✅ Read Excel file: {len(df)} rows")
                
                elif file_ext == '.pdf':
                    # PDF parsing (not implemented yet)
                    raise NotImplementedError(
                        "PDF parsing is not yet implemented. "
                        "Please convert your PDF to CSV or Excel format first."
                    )
                
                else:
                    raise ValueError(
                        f"Unsupported file type: {file_ext}. "
                        f"Supported formats: .csv, .xlsx, .xls"
                    )
            
            except Exception as e:
                print(f"   ❌ Error reading file: {str(e)}")
                raise ValueError(f"Error reading file {filename}: {str(e)}")
            
            # Show DataFrame info
            print(f"   Columns: {df.columns.tolist()}")
            print(f"   Shape: {df.shape}")
            
            # Parse the DataFrame using existing parse_statement method
            print(f"   🔄 Parsing transactions...")
            transactions = self.parse_statement(df, debug=True)
            
            if not transactions:
                print(f"   ❌ No transactions found!")
                raise ValueError(
                    f"No transactions found in {filename}. "
                    f"Please check that the file has the correct format with date, amount, and transaction columns."
                )
            
            print(f"   ✅ Parsed {len(transactions)} transactions")
            
            # Add categorization to each transaction
            print(f"   🏷️  Adding categories...")
            for idx, txn in enumerate(transactions):
                description = txn.get('description', '')
                txn['category'] = self._categorize_transaction(description)
                
                # Debug first few
                if idx < 3:
                    print(f"      Transaction {idx+1}: {txn.get('description', 'No desc')[:40]} → {txn['category']}")
            
            print(f"   ✅ Categorization complete\n")
            
            return transactions
        
    def _categorize_transaction(self, description: str) -> str:
            """
            Categorize transaction based on description keywords.
            Uses pattern matching to assign appropriate category.
            
            Args:
                description: Transaction description text
                
            Returns:
                Category name (lowercase with underscores)
                
            Categories:
            - salary: Salary credits
            - cash_withdrawal: ATM/cash withdrawals
            - food_dining: Restaurants, food delivery
            - transport: Uber, fuel, parking
            - shopping: Amazon, Flipkart, retail
            - utilities: Electricity, internet, mobile bills
            - entertainment: Netflix, movies, gaming
            - healthcare: Hospital, pharmacy, doctor
            - insurance: Insurance premiums
            - investment: Mutual funds, SIP, stocks
            - emi_loan: EMI, loan payments
            - transfer: UPI, NEFT, fund transfers
            - education: School fees, courses
            - rent: House rent payments
            - others: Everything else
            """
            if not description:
                return 'others'
            
            # Convert to lowercase for case-insensitive matching
            description_lower = description.lower()
            
            # Category patterns - organized by priority
            # Higher priority categories are checked first
            category_patterns = {
                # Income
                'salary': [
                    'salary', 'sal credit', 'payroll', 'salary credit', 'sal credited',
                    'monthly salary', 'payment of salary', 'sal transfer'
                ],
                
                # Cash
                'cash_withdrawal': [
                    'atm', 'cash withdrawal', 'cash wdl', 'atm withdrawal', 'withdrawal',
                    'cash', 'atm-wdl', 'atm cash', 'atm wd', 'cash wd', 'pos cash'
                ],
                
                # Food & Dining
                'food_dining': [
                    'swiggy', 'zomato', 'restaurant', 'cafe', 'food', 'dining',
                    'pizza', 'burger', 'hotel', 'dhaba', 'barbeque', 'kitchen',
                    'bakery', 'dominos', 'mcdonald', 'kfc', 'subway', 'starbucks',
                    'ccd', 'coffee', 'tea', 'dunkin', 'pizza hut', 'taco bell',
                    'panda express', 'chipotle', 'panera', 'food delivery',
                    'uber eats', 'doordash', 'grubhub', 'postmates'
                ],
                
                # Transport
                'transport': [
                    'uber', 'ola', 'petrol', 'fuel', 'metro', 'taxi', 'parking',
                    'rapido', 'auto', 'bus', 'train', 'flight', 'cab', 'toll',
                    'lyft', 'hp petrol', 'bharat petrol', 'shell', 'bpcl', 'iocl',
                    'indian oil', 'gas station', 'railway', 'irctc', 'airlines',
                    'indigo', 'spicejet', 'air india', 'vistara', 'go air'
                ],
                
                # Shopping
                'shopping': [
                    'amazon', 'flipkart', 'shop', 'store', 'mall', 'purchase',
                    'myntra', 'ajio', 'clothing', 'fashion', 'grocery',
                    'supermarket', 'dmart', 'reliance', 'big bazaar', 'more',
                    'walmart', 'target', 'ebay', 'etsy', 'shopify', 'retail',
                    'nykaa', 'firstcry', 'snapdeal', 'meesho', 'jiomart'
                ],
                
                # Utilities
                'utilities': [
                    'electricity', 'water', 'gas', 'internet', 'mobile', 'phone',
                    'bill', 'recharge', 'broadband', 'wifi', 'telecom',
                    'airtel', 'jio', 'vodafone', 'bsnl', 'vi', 'idea',
                    'tata sky', 'dish tv', 'cable', 'lpg', 'cooking gas',
                    'electricity bill', 'water bill', 'phone bill'
                ],
                
                # Entertainment
                'entertainment': [
                    'movie', 'netflix', 'spotify', 'prime', 'gaming', 'entertainment',
                    'youtube', 'cinema', 'theater', 'hotstar', 'disney', 'sony liv',
                    'zee5', 'voot', 'mx player', 'aha', 'hoichoi', 'apple music',
                    'amazon prime', 'hulu', 'hbo', 'playstation', 'xbox', 'steam',
                    'pvr', 'inox', 'cinepolis', 'carnival'
                ],
                
                # Healthcare
                'healthcare': [
                    'hospital', 'pharmacy', 'medicine', 'doctor', 'clinic', 'health',
                    'medical', 'lab', 'test', 'diagnostic', 'apollo', 'fortis',
                    'max', 'manipal', 'medanta', 'care', 'narayana', 'aiims',
                    'pharma', 'chemist', 'drugs', 'prescription', 'medplus',
                    'apollo pharmacy', '1mg', 'netmeds', 'pharmeasy'
                ],
                
                # Insurance
                'insurance': [
                    'insurance', 'premium', 'policy', 'lic', 'hdfc life',
                    'icici prudential', 'sbi life', 'max life', 'bajaj allianz',
                    'health insurance', 'life insurance', 'car insurance',
                    'term insurance', 'endowment', 'ulip'
                ],
                
                # Investment
                'investment': [
                    'mutual fund', 'sip', 'stock', 'investment', 'zerodha', 'groww',
                    'upstox', 'systematic', 'equity', 'debt', 'fund', 'nav',
                    'angel broking', 'icicidirect', 'hdfc securities', 'kotak securities',
                    'sharekhan', 'axis direct', 'fidelity', 'vanguard', 'robinhood'
                ],
                
                # EMI & Loans
                'emi_loan': [
                    'emi', 'loan', 'installment', 'home loan', 'car loan',
                    'personal loan', 'credit card', 'repayment', 'mortgage',
                    'auto loan', 'education loan', 'business loan', 'loan emi',
                    'housing loan', 'vehicle loan', 'two wheeler loan'
                ],
                
                # Transfers
                'transfer': [
                    'upi', 'neft', 'imps', 'rtgs', 'transfer', 'fund transfer',
                    'paytm', 'phonepe', 'google pay', 'gpay', 'bhim', 'wallet',
                    'money transfer', 'payment', 'to:', 'from:', '@', 'bank transfer',
                    'venmo', 'cashapp', 'zelle', 'paypal'
                ],
                
                # Education
                'education': [
                    'school', 'college', 'university', 'course', 'tuition',
                    'education', 'fee', 'book', 'exam', 'admission',
                    'coaching', 'classes', 'learning', 'udemy', 'coursera',
                    'byju', 'unacademy', 'vedantu', 'khan academy',
                    'school fee', 'college fee', 'exam fee'
                ],
                
                # Rent
                'rent': [
                    'rent', 'house rent', 'apartment', 'lease', 'flat rent',
                    'monthly rent', 'room rent', 'accommodation', 'housing rent',
                    'residential rent'
                ],
            }
            
            # Check each category in order
            for category, keywords in category_patterns.items():
                for keyword in keywords:
                    if keyword in description_lower:
                        return category
            
            # Default category if no match found
            return 'others'
