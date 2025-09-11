"""
Import/Export UI components
"""

import streamlit as st
from datetime import datetime
from utils.import_export import export_portfolio_to_csv, import_portfolio_from_csv, create_sample_csv, validate_csv_format
from utils.storage import save_to_storage


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
    st.header("📊 Portfolio Data Management")
    st.write("Import and export your portfolio data to keep backups or share with other tools.")
    
    # Create tabs for import and export
    tab1, tab2 = st.tabs(["📤 Export", "📥 Import"])
    
    with tab1:
        render_export_section(st.session_state.get('investments', []))
    
    with tab2:
        render_import_section()
    
    st.divider()
    
    # Data summary
    if 'investments' in st.session_state and st.session_state.investments:
        st.subheader("📈 Current Portfolio Summary")
        total_investments = len(st.session_state.investments)
        total_value = sum(inv['amount'] for inv in st.session_state.investments)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Investments", total_investments)
        with col2:
            st.metric("Total Value", f"${total_value:,.2f}")
        with col3:
            investment_types = len(set(inv['type'] for inv in st.session_state.investments))
            st.metric("Investment Types", investment_types)
