"""
Import/Export utilities for portfolio data and investment goals
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import io
import csv
import json


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


def export_goals_to_csv(goals):
    """Export investment goals to CSV format"""
    if not goals:
        return None
    
    # Create a DataFrame from goals
    export_data = []
    for goal in goals:
        export_data.append({
            'Goal Name': goal['name'],
            'Description': goal.get('description', ''),
            'Target Amount': goal['target_amount'],
            'Target Date': goal['target_date'],
            'Investment Filter': json.dumps(goal.get('investment_filter', {})),
            'Is Active': goal['is_active'],
            'Created Date': goal['created_date']
        })
    
    df = pd.DataFrame(export_data)
    
    # Convert to CSV string
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()
    
    return csv_string


def import_goals_from_csv(csv_file):
    """Import investment goals from CSV file"""
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Validate required columns for goals
        required_columns = ['Goal Name', 'Target Amount', 'Target Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"Missing required columns for goals: {', '.join(missing_columns)}"
        
        # Convert DataFrame to goals list
        goals = []
        for _, row in df.iterrows():
            try:
                # Parse investment filter JSON if present
                investment_filter = {}
                if 'Investment Filter' in df.columns and pd.notna(row['Investment Filter']):
                    try:
                        investment_filter = json.loads(row['Investment Filter'])
                    except json.JSONDecodeError:
                        investment_filter = {}
                
                goal = {
                    'name': str(row['Goal Name']),
                    'description': str(row.get('Description', '')),
                    'target_amount': float(row['Target Amount']),
                    'target_date': str(row['Target Date']),
                    'investment_filter': investment_filter,
                    'is_active': bool(row.get('Is Active', True)),
                    'created_date': str(row.get('Created Date', datetime.now().isoformat()))
                }
                
                goals.append(goal)
                
            except (ValueError, TypeError) as e:
                return None, f"Error processing goal data in row {len(goals) + 1}: {str(e)}"
        
        return goals, f"Successfully imported {len(goals)} goals"
    
    except Exception as e:
        return None, f"Error importing goals from CSV: {str(e)}"


def export_complete_data_to_csv(investments, goals):
    """Export both investments and goals to a single Excel file, or create a ZIP with separate CSVs as fallback"""
    if not investments and not goals:
        return None
    
    try:
        # Try Excel export first
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Export investments to 'Investments' sheet
            if investments:
                investments_df = pd.DataFrame([{
                    'Investment Name': inv['name'],
                    'Investment Type': inv['type'],
                    'Entry Price': inv['entry_price'],
                    'Shares/Units': inv['shares'],
                    'Total Amount': inv['amount'],
                    'Risk Level': inv['risk_level'],
                    'Date Added': inv.get('date_added', '')
                } for inv in investments])
                investments_df.to_excel(writer, sheet_name='Investments', index=False)
            
            # Export goals to 'Goals' sheet
            if goals:
                goals_df = pd.DataFrame([{
                    'Goal Name': goal['name'],
                    'Description': goal.get('description', ''),
                    'Target Amount': goal['target_amount'],
                    'Target Date': goal['target_date'],
                    'Investment Filter': json.dumps(goal.get('investment_filter', {})),
                    'Is Active': goal['is_active'],
                    'Created Date': goal['created_date']
                } for goal in goals])
                goals_df.to_excel(writer, sheet_name='Goals', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    except (ImportError, Exception) as e:
        # Fallback: create a combined CSV with a separator
        try:
            combined_csv = io.StringIO()
            
            # Add investments section
            if investments:
                combined_csv.write("=== INVESTMENTS ===\n")
                investments_csv = export_portfolio_to_csv(investments)
                combined_csv.write(investments_csv)
                combined_csv.write("\n\n")
            
            # Add goals section
            if goals:
                combined_csv.write("=== GOALS ===\n")
                goals_csv = export_goals_to_csv(goals)
                combined_csv.write(goals_csv)
            
            return combined_csv.getvalue()
        
        except Exception as fallback_error:
            return None


def create_fallback_csv_export(investments, goals):
    """Create a fallback CSV export when Excel is not available"""
    combined_data = io.StringIO()
    
    # Header
    combined_data.write("FINTECH APP DATA EXPORT\n")
    combined_data.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    combined_data.write("="*50 + "\n\n")
    
    # Investments section
    if investments:
        combined_data.write("PORTFOLIO INVESTMENTS\n")
        combined_data.write("="*25 + "\n")
        investments_csv = export_portfolio_to_csv(investments)
        combined_data.write(investments_csv)
        combined_data.write("\n\n")
    
    # Goals section
    if goals:
        combined_data.write("INVESTMENT GOALS\n")
        combined_data.write("="*16 + "\n")
        goals_csv = export_goals_to_csv(goals)
        combined_data.write(goals_csv)
    
    return combined_data.getvalue()


def import_complete_data_from_file(uploaded_file):
    """Import complete data from Excel or CSV file"""
    try:
        file_name = uploaded_file.name.lower()
        
        if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            # Handle Excel file
            return import_from_excel_file(uploaded_file)
        elif file_name.endswith('.csv'):
            # Handle CSV file (could be structured or regular)
            return import_from_structured_csv(uploaded_file)
        else:
            return None, None, "Unsupported file format. Please use Excel (.xlsx) or CSV (.csv) files."
    
    except Exception as e:
        return None, None, f"Error importing file: {str(e)}"


def import_from_excel_file(uploaded_file):
    """Import data from Excel file with multiple sheets"""
    try:
        # Read all sheets
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        
        investments = None
        goals = None
        messages = []
        
        # Check for Investments sheet
        if 'Investments' in excel_data:
            inv_df = excel_data['Investments']
            investments, inv_msg = convert_dataframe_to_investments(inv_df)
            if investments:
                messages.append(f"✅ Imported {len(investments)} investments")
            else:
                messages.append(f"❌ Investment import failed: {inv_msg}")
        
        # Check for Goals sheet
        if 'Goals' in excel_data:
            goals_df = excel_data['Goals']
            goals, goals_msg = convert_dataframe_to_goals(goals_df)
            if goals:
                messages.append(f"✅ Imported {len(goals)} goals")
            else:
                messages.append(f"❌ Goals import failed: {goals_msg}")
        
        if not investments and not goals:
            return None, None, "No valid data sheets found. Expected 'Investments' and/or 'Goals' sheets."
        
        return investments, goals, " | ".join(messages)
    
    except Exception as e:
        return None, None, f"Error reading Excel file: {str(e)}"


def import_from_structured_csv(uploaded_file):
    """Import data from structured CSV file (with sections)"""
    try:
        content = uploaded_file.read().decode('utf-8')
        uploaded_file.seek(0)  # Reset for potential reuse
        
        # Check if it's a structured CSV (contains sections)
        if "=== INVESTMENTS ===" in content or "=== GOALS ===" in content:
            return parse_structured_csv(content)
        else:
            # Try as regular investments CSV
            investments, msg = import_portfolio_from_csv(uploaded_file)
            return investments, None, msg
    
    except Exception as e:
        return None, None, f"Error reading CSV file: {str(e)}"


def parse_structured_csv(content):
    """Parse structured CSV content with sections"""
    try:
        lines = content.split('\n')
        investments = None
        goals = None
        messages = []
        
        # Find sections
        investments_start = None
        goals_start = None
        
        for i, line in enumerate(lines):
            if "=== INVESTMENTS ===" in line:
                investments_start = i + 1
            elif "=== GOALS ===" in line:
                goals_start = i + 1
        
        # Extract investments section
        if investments_start is not None:
            investments_lines = []
            for i in range(investments_start, len(lines)):
                if "=== GOALS ===" in lines[i] or lines[i].strip() == "":
                    break
                investments_lines.append(lines[i])
            
            if investments_lines:
                investments_csv = '\n'.join(investments_lines)
                investments_buffer = io.StringIO(investments_csv)
                investments, inv_msg = import_portfolio_from_csv(investments_buffer)
                if investments:
                    messages.append(f"✅ Imported {len(investments)} investments")
                else:
                    messages.append(f"❌ Investment import failed: {inv_msg}")
        
        # Extract goals section
        if goals_start is not None:
            goals_lines = []
            for i in range(goals_start, len(lines)):
                if lines[i].strip() != "":
                    goals_lines.append(lines[i])
            
            if goals_lines:
                goals_csv = '\n'.join(goals_lines)
                goals_buffer = io.StringIO(goals_csv)
                goals, goals_msg = import_goals_from_csv(goals_buffer)
                if goals:
                    messages.append(f"✅ Imported {len(goals)} goals")
                else:
                    messages.append(f"❌ Goals import failed: {goals_msg}")
        
        if not investments and not goals:
            return None, None, "No valid data sections found in structured CSV."
        
        return investments, goals, " | ".join(messages)
    
    except Exception as e:
        return None, None, f"Error parsing structured CSV: {str(e)}"


def convert_dataframe_to_investments(df):
    """Convert DataFrame to investments list"""
    try:
        # Validate required columns
        required_columns = ['Investment Name', 'Investment Type', 'Entry Price', 'Shares/Units', 'Total Amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"
        
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
                return None, f"Error processing investment data in row {len(investments) + 1}: {str(e)}"
        
        return investments, f"Successfully processed {len(investments)} investments"
    
    except Exception as e:
        return None, f"Error converting investments: {str(e)}"


def convert_dataframe_to_goals(df):
    """Convert DataFrame to goals list"""
    try:
        # Validate required columns
        required_columns = ['Goal Name', 'Target Amount', 'Target Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"
        
        goals = []
        for _, row in df.iterrows():
            try:
                # Parse investment filter JSON if present
                investment_filter = {}
                if 'Investment Filter' in df.columns and pd.notna(row['Investment Filter']):
                    try:
                        investment_filter = json.loads(row['Investment Filter'])
                    except json.JSONDecodeError:
                        investment_filter = {}
                
                goal = {
                    'name': str(row['Goal Name']),
                    'description': str(row.get('Description', '')),
                    'target_amount': float(row['Target Amount']),
                    'target_date': str(row['Target Date']),
                    'investment_filter': investment_filter,
                    'is_active': bool(row.get('Is Active', True)),
                    'created_date': str(row.get('Created Date', datetime.now().isoformat()))
                }
                goals.append(goal)
            except (ValueError, TypeError) as e:
                return None, f"Error processing goal data in row {len(goals) + 1}: {str(e)}"
        
        return goals, f"Successfully processed {len(goals)} goals"
    
    except Exception as e:
        return None, f"Error converting goals: {str(e)}"


def validate_goals_csv_format(csv_file):
    """Validate goals CSV file format before import"""
    try:
        df = pd.read_csv(csv_file)
        
        # Check if file is empty
        if df.empty:
            return False, "Goals CSV file is empty"
        
        # Check required columns for goals
        required_columns = ['Goal Name', 'Target Amount', 'Target Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns for goals: {', '.join(missing_columns)}"
        
        # Check data types for goals
        try:
            pd.to_numeric(df['Target Amount'], errors='raise')
        except (ValueError, TypeError):
            return False, "Column 'Target Amount' contains non-numeric values"
        
        # Validate dates
        try:
            pd.to_datetime(df['Target Date'], errors='raise')
        except (ValueError, TypeError):
            return False, "Column 'Target Date' contains invalid date values"
        
        return True, "Goals CSV format is valid"
    
    except Exception as e:
        return False, f"Error validating goals CSV: {str(e)}"
