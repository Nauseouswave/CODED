"""
Import/Export UI components
"""

import streamlit as st
from datetime import datetime
from utils.import_export import (
    export_portfolio_to_csv, import_portfolio_from_csv, create_sample_csv, validate_csv_format,
    export_goals_to_csv, import_goals_from_csv, export_complete_data_to_csv, validate_goals_csv_format,
    import_complete_data_from_file
)
from utils.storage import save_to_storage
from utils.goals import save_goals, load_goals


def render_export_section(investments):
    """Render the export functionality"""
    st.subheader("📤 Export Portfolio")
    
    if not investments:
        st.info("No investments to export. Add some investments first!")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**{len(investments)} investments** ready for export")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_export_{timestamp}.csv"
        
        # Export to CSV
        csv_data = export_portfolio_to_csv(investments)
        
        if csv_data:
            st.download_button(
                label="💾 Download Portfolio CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                type="primary",
                help="Download your portfolio data as a CSV file"
            )
            
            st.success("✅ Export ready! Click the button above to download.")
        else:
            st.error("❌ Failed to prepare export data")
    
    with col2:
        # Preview of export data
        st.write("**Export Preview:**")
        if csv_data:
            # Show first few lines of CSV
            lines = csv_data.split('\n')[:4]  # Header + 3 rows
            preview = '\n'.join(lines)
            st.code(preview, language='csv')
            
            if len(investments) > 3:
                st.caption(f"... and {len(investments) - 3} more investments")


def render_import_section():
    """Render the import functionality"""
    st.subheader("📥 Import Portfolio")
    
    # Instructions
    with st.expander("📋 Import Instructions", expanded=False):
        st.write("""
        **How to import your portfolio:**
        
        1. **Prepare your CSV file** with these required columns:
           - `Investment Name`: Name of the investment
           - `Investment Type`: Stocks, Bonds, Real Estate, or Cryptocurrency
           - `Entry Price`: Price per share/unit when purchased
           - `Shares/Units`: Number of shares or units owned
           - `Total Amount`: Total investment amount
        
        2. **Optional columns:**
           - `Risk Level`: Low, Medium, or High
           - `Date Added`: When the investment was added
        
        3. **Upload the file** using the file uploader below
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file containing your portfolio data"
        )
        
        # Import options
        st.write("**Import Options:**")
        import_mode = st.radio(
            "What to do with existing investments?",
            ["Add to existing portfolio", "Replace entire portfolio"],
            help="Choose whether to add imported investments to your current portfolio or replace everything"
        )
        
        if uploaded_file is not None:
            # Validate file first
            is_valid, message = validate_csv_format(uploaded_file)
            
            if is_valid:
                st.success(f"✅ {message}")
                
                # Show import button
                if st.button("🚀 Import Portfolio", type="primary"):
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Import the data
                    imported_investments, import_message = import_portfolio_from_csv(uploaded_file)
                    
                    if imported_investments:
                        # Handle import mode
                        if import_mode == "Replace entire portfolio":
                            st.session_state.investments = imported_investments
                        else:  # Add to existing
                            if 'investments' not in st.session_state:
                                st.session_state.investments = []
                            st.session_state.investments.extend(imported_investments)
                        
                        # Save to storage
                        save_to_storage(st.session_state.investments)
                        
                        st.success(f"🎉 {import_message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Import failed: {import_message}")
            else:
                st.error(f"❌ {message}")
    
    with col2:
        # Sample template download
        st.write("**Need a template?**")
        st.write("Download a sample CSV file to see the correct format:")
        
        sample_csv = create_sample_csv()
        st.download_button(
            label="📋 Download Sample Template",
            data=sample_csv,
            file_name="portfolio_template.csv",
            mime="text/csv",
            help="Download a sample CSV file with the correct format"
        )
        
        # Show sample preview
        st.write("**Sample Format:**")
        st.code("""Investment Name,Investment Type,Entry Price,Shares/Units,Total Amount,Risk Level
Apple Inc. (AAPL),Stocks,150.00,10.0,1500.00,Medium
Bitcoin (BTC),Cryptocurrency,45000.00,0.1,4500.00,High""", language='csv')


def render_import_export_page():
    """Render the complete import/export page"""
    st.header("📊 Portfolio & Goals Data Management")
    st.write("Import and export your portfolio investments and goals to keep backups or share with other tools.")
    
    # Create tabs for different data types
    tab1, tab2, tab3 = st.tabs(["📤 Export", "📥 Import", "📋 Complete Backup"])
    
    with tab1:
        st.subheader("Export Data")
        export_type = st.selectbox(
            "What would you like to export?",
            ["Portfolio Investments Only", "Investment Goals Only", "Everything (Excel)"]
        )
        
        if export_type == "Portfolio Investments Only":
            render_export_section(st.session_state.get('investments', []))
        elif export_type == "Investment Goals Only":
            render_goals_export_section()
        else:
            render_complete_export_section()
    
    with tab2:
        st.subheader("Import Data")
        import_type = st.selectbox(
            "What would you like to import?",
            ["Portfolio Investments", "Investment Goals", "Complete Backup (Excel/CSV)"]
        )
        
        if import_type == "Portfolio Investments":
            render_import_section()
        elif import_type == "Investment Goals":
            render_goals_import_section()
        else:
            render_complete_import_section()
    
    with tab3:
        render_backup_section()
    
    st.divider()
    
    # Data summary
    render_data_summary()


def render_goals_export_section():
    """Render goals export functionality"""
    goals = load_goals()
    
    if not goals:
        st.info("No goals to export. Create some goals first!")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**{len(goals)} goals** ready for export")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"goals_export_{timestamp}.csv"
        
        # Export to CSV
        csv_data = export_goals_to_csv(goals)
        
        if csv_data:
            st.download_button(
                label="💾 Download Goals CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                type="primary",
                help="Download your investment goals as a CSV file"
            )
            
            st.success("✅ Goals export ready! Click the button above to download.")
        else:
            st.error("❌ Failed to prepare goals export data")
    
    with col2:
        # Preview of goals export data
        st.write("**Goals Export Preview:**")
        if csv_data:
            lines = csv_data.split('\n')[:4]  # Header + 3 rows
            preview = '\n'.join(lines)
            st.code(preview, language='csv')


def render_goals_import_section():
    """Render goals import functionality"""
    st.write("Upload a CSV file containing your investment goals.")
    
    uploaded_file = st.file_uploader(
        "Choose a goals CSV file",
        type=['csv'],
        help="Upload a CSV file with goals data",
        key="goals_csv_upload"
    )
    
    if uploaded_file is not None:
        # Validate file first
        is_valid, message = validate_goals_csv_format(uploaded_file)
        
        if is_valid:
            st.success(f"✅ {message}")
            
            # Show preview
            uploaded_file.seek(0)  # Reset file pointer
            try:
                import pandas as pd
                df = pd.read_csv(uploaded_file, nrows=3)
                st.write("**File Preview:**")
                st.dataframe(df)
            except:
                st.warning("Could not preview file")
            
            uploaded_file.seek(0)  # Reset again for import
            
            if st.button("📥 Import Goals", type="primary"):
                goals, result_message = import_goals_from_csv(uploaded_file)
                
                if goals:
                    # Save goals
                    save_goals(goals)
                    st.success(f"✅ {result_message}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {result_message}")
        else:
            st.error(f"❌ {message}")
            
    # Goals CSV template
    st.subheader("📋 Goals CSV Template")
    st.write("Not sure about the format? Download a template:")
    
    template_data = """Goal Name,Description,Target Amount,Target Date,Investment Filter,Is Active,Created Date
Emergency Fund,Build an emergency fund for unexpected expenses,10000,2025-12-31,{},True,2024-01-01T00:00:00
Retirement Savings,Long-term retirement savings goal,500000,2040-01-01,{},True,2024-01-01T00:00:00
House Down Payment,Save for house down payment,50000,2026-06-01,{},True,2024-01-01T00:00:00"""
    
    st.download_button(
        label="📄 Download Goals Template",
        data=template_data,
        file_name="goals_template.csv",
        mime="text/csv",
        help="Download a template CSV file for goals import"
    )


def render_complete_export_section():
    """Render complete data export (Excel with multiple sheets or CSV fallback)"""
    investments = st.session_state.get('investments', [])
    goals = load_goals()
    
    if not investments and not goals:
        st.info("No data to export. Add some investments or goals first!")
        return
    
    st.write("Export everything in a single file.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Export Contents:**")
        if investments:
            st.write(f"• {len(investments)} investments")
        if goals:
            st.write(f"• {len(goals)} goals")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export data
        export_data = export_complete_data_to_csv(investments, goals)
        
        if export_data:
            # Check if it's binary (Excel) or text (CSV)
            if isinstance(export_data, bytes):
                # Excel format
                filename = f"complete_portfolio_backup_{timestamp}.xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                label = "💾 Download Complete Backup (Excel)"
                success_msg = "✅ Excel backup ready!"
            else:
                # CSV fallback format
                filename = f"complete_portfolio_backup_{timestamp}.csv"
                mime_type = "text/csv"
                label = "💾 Download Complete Backup (CSV)"
                success_msg = "✅ CSV backup ready!"
            
            st.download_button(
                label=label,
                data=export_data,
                file_name=filename,
                mime=mime_type,
                type="primary",
                help="Download all your data in a single file"
            )
            
            st.success(success_msg)
        else:
            st.error("❌ Failed to prepare complete backup")
    
    with col2:
        # Check what format will be used
        try:
            import xlsxwriter
            st.info("📘 **Excel Format**\n\nThe Excel file will contain separate sheets:\n• **Investments**: All your portfolio data\n• **Goals**: All your investment goals\n\nThis format preserves all data and can be opened in Excel, Google Sheets, or other spreadsheet applications.")
        except ImportError:
            st.info("📄 **CSV Format**\n\nSince Excel support is not available, data will be exported as a structured CSV file with:\n• **Investments section**: All your portfolio data\n• **Goals section**: All your investment goals\n\nFor full Excel support, install xlsxwriter: `pip install xlsxwriter`")


def render_backup_section():
    """Render backup and restore functionality"""
    st.subheader("🔄 Complete Backup & Restore")
    st.write("Create a complete backup of all your data or restore from a previous backup.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📤 Create Backup**")
        investments = st.session_state.get('investments', [])
        goals = load_goals()
        
        if investments or goals:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            export_data = export_complete_data_to_csv(investments, goals)
            
            if export_data:
                # Determine file format
                if isinstance(export_data, bytes):
                    filename = f"fintech_app_backup_{timestamp}.xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    label = "💾 Create Complete Backup (Excel)"
                else:
                    filename = f"fintech_app_backup_{timestamp}.csv"
                    mime_type = "text/csv"
                    label = "💾 Create Complete Backup (CSV)"
                
                st.download_button(
                    label=label,
                    data=export_data,
                    file_name=filename,
                    mime=mime_type,
                    type="primary"
                )
            else:
                st.error("Failed to create backup")
        else:
            st.info("No data to backup")
    
    with col2:
        st.write("**📥 Restore from Backup**")
        st.info("🚧 Restore functionality coming soon!\n\nFor now, you can manually import investments and goals using the Import tab.")


def render_data_summary():
    """Render current data summary"""
    investments = st.session_state.get('investments', [])
    goals = load_goals()
    
    if investments or goals:
        st.subheader("📈 Current Data Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Investments", len(investments))
        
        with col2:
            if investments:
                total_value = sum(inv['amount'] for inv in investments)
                st.metric("Total Value", f"${total_value:,.2f}")
            else:
                st.metric("Total Value", "$0")
        
        with col3:
            st.metric("Goals", len(goals))
        
        with col4:
            if goals:
                active_goals = len([g for g in goals if g.get('is_active', True)])
                st.metric("Active Goals", active_goals)
            else:
                st.metric("Active Goals", "0")
        
        # Additional stats
        if investments:
            investment_types = len(set(inv['type'] for inv in investments))
            st.caption(f"📊 Portfolio spread across {investment_types} investment types")
        
        if goals:
            total_target = sum(g['target_amount'] for g in goals if g.get('is_active', True))
            st.caption(f"🎯 Total goal targets: ${total_target:,.0f}")
    else:
        st.info("No data available. Start by adding some investments or creating goals!")


def render_complete_import_section():
    """Render complete backup import functionality"""
    st.write("Import a complete backup file containing both investments and goals.")
    st.info("📁 **Supported formats:**\n• Excel files (.xlsx) with separate sheets\n• Structured CSV files from app exports\n• Regular CSV files (investments only)")
    
    uploaded_file = st.file_uploader(
        "Choose a backup file",
        type=['xlsx', 'xls', 'csv'],
        help="Upload an Excel or CSV backup file",
        key="complete_backup_upload"
    )
    
    if uploaded_file is not None:
        st.write("**File Information:**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📄 **File:** {uploaded_file.name}")
            st.write(f"📊 **Size:** {uploaded_file.size / 1024:.1f} KB")
        with col2:
            file_type = "Excel" if uploaded_file.name.lower().endswith(('.xlsx', '.xls')) else "CSV"
            st.write(f"📋 **Type:** {file_type}")
        
        # Preview section
        with st.expander("👀 File Preview", expanded=False):
            try:
                if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
                    # Excel preview
                    import pandas as pd
                    excel_data = pd.read_excel(uploaded_file, sheet_name=None, nrows=3)
                    for sheet_name, df in excel_data.items():
                        st.write(f"**Sheet: {sheet_name}**")
                        st.dataframe(df)
                        st.write("")
                else:
                    # CSV preview
                    uploaded_file.seek(0)
                    content = uploaded_file.read().decode('utf-8')
                    lines = content.split('\n')[:10]  # First 10 lines
                    preview = '\n'.join(lines)
                    st.code(preview, language='csv')
                
                uploaded_file.seek(0)  # Reset file pointer
            except Exception as e:
                st.warning(f"Could not preview file: {str(e)}")
        
        st.divider()
        
        # Import options
        col1, col2 = st.columns(2)
        
        with col1:
            merge_data = st.checkbox(
                "Merge with existing data",
                value=True,
                help="If unchecked, existing data will be replaced"
            )
        
        with col2:
            import_investments = st.checkbox("Import Investments", value=True)
            import_goals = st.checkbox("Import Goals", value=True)
        
        if st.button("📥 Import Complete Backup", type="primary"):
            if not import_investments and not import_goals:
                st.error("Please select at least one data type to import!")
                return
            
            # Import the data
            investments, goals, message = import_complete_data_from_file(uploaded_file)
            
            if investments is None and goals is None:
                st.error(f"❌ Import failed: {message}")
                return
            
            # Handle the imported data
            success_messages = []
            
            if investments and import_investments:
                if merge_data:
                    # Merge with existing investments
                    existing_investments = st.session_state.get('investments', [])
                    existing_names = [inv['name'] for inv in existing_investments]
                    new_investments = [inv for inv in investments if inv['name'] not in existing_names]
                    st.session_state.investments = existing_investments + new_investments
                    save_to_storage(st.session_state.investments)
                    success_messages.append(f"✅ Added {len(new_investments)} new investments ({len(investments) - len(new_investments)} duplicates skipped)")
                else:
                    # Replace existing investments
                    st.session_state.investments = investments
                    save_to_storage(investments)
                    success_messages.append(f"✅ Imported {len(investments)} investments (replaced existing)")
            
            if goals and import_goals:
                if merge_data:
                    # Merge with existing goals
                    existing_goals = load_goals()
                    existing_names = [goal['name'] for goal in existing_goals]
                    new_goals = [goal for goal in goals if goal['name'] not in existing_names]
                    all_goals = existing_goals + new_goals
                    save_goals(all_goals)
                    success_messages.append(f"✅ Added {len(new_goals)} new goals ({len(goals) - len(new_goals)} duplicates skipped)")
                else:
                    # Replace existing goals
                    save_goals(goals)
                    success_messages.append(f"✅ Imported {len(goals)} goals (replaced existing)")
            
            if success_messages:
                for msg in success_messages:
                    st.success(msg)
                st.balloons()
                st.rerun()
            else:
                st.warning("No new data was imported.")