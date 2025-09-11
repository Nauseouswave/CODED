"""
Import/Export utilities for portfolio data
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import io
import csv


def export_portfolio_to_csv(investments):
    """Export portfolio data to CSV format"""
    if not investments:
        return None
    
    # Create a DataFrame from investments
    export_data = []
    for inv in investments:
        export_data.append({
            'Investment Name': inv['name'],
            'Investment Type': inv['type'],
            'Entry Price': inv['entry_price'],
            'Shares/Units': inv['shares'],
            'Total Amount': inv['amount'],
            'Risk Level': inv['risk_level'],
            'Date Added': inv.get('date_added', '')
        })
    
    df = pd.DataFrame(export_data)
    
    # Convert to CSV string
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()
    
    return csv_string


def import_portfolio_from_csv(csv_file):
    """Import portfolio data from CSV file"""
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        required_columns = ['Investment Name', 'Investment Type', 'Entry Price', 'Shares/Units', 'Total Amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"
        
        # Convert DataFrame back to investment format
        investments = []
        for _, row in df.iterrows():
            try:
                investment = {
                    'name': str(row['Investment Name']),
                    'type': str(row['Investment Type']),
                    'entry_price': float(row['Entry Price']),
                    'shares': float(row['Shares/Units']),
                    'amount': float(row['Total Amount']),
                    'risk_level': str(row.get('Risk Level', 'Medium')),
                    'date_added': str(row.get('Date Added', datetime.now().isoformat()))
                }
                investments.append(investment)
            except (ValueError, TypeError) as e:
                return None, f"Error processing row {len(investments) + 1}: Invalid data format"
        
        return investments, f"Successfully imported {len(investments)} investments"
    
    except Exception as e:
        return None, f"Error reading CSV file: {str(e)}"


def create_sample_csv():
    """Create a sample CSV template for download"""
    sample_data = [
        {
            'Investment Name': 'Apple Inc. (AAPL)',
            'Investment Type': 'Stocks',
            'Entry Price': 150.00,
            'Shares/Units': 10.0,
            'Total Amount': 1500.00,
            'Risk Level': 'Medium',
            'Date Added': datetime.now().isoformat()
        },
        {
            'Investment Name': 'Bitcoin (BTC)',
            'Investment Type': 'Cryptocurrency',
            'Entry Price': 45000.00,
            'Shares/Units': 0.1,
            'Total Amount': 4500.00,
            'Risk Level': 'High',
            'Date Added': datetime.now().isoformat()
        }
    ]
    
    df = pd.DataFrame(sample_data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()


def validate_csv_format(csv_file):
    """Validate CSV file format before import"""
    try:
        df = pd.read_csv(csv_file)
        
        # Check if file is empty
        if df.empty:
            return False, "CSV file is empty"
        
        # Check required columns
        required_columns = ['Investment Name', 'Investment Type', 'Entry Price', 'Shares/Units', 'Total Amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        # Check data types
        numeric_columns = ['Entry Price', 'Shares/Units', 'Total Amount']
        for col in numeric_columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                except (ValueError, TypeError):
                    return False, f"Column '{col}' contains non-numeric values"
        
        return True, "CSV format is valid"
    
    except Exception as e:
        return False, f"Error validating CSV: {str(e)}"
