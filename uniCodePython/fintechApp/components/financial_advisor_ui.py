"""
Financial Advisor UI Component
Streamlit interface for AI-powered financial advisory features
"""

import streamlit as st
from typing import List, Dict, Any
import json
from datetime import datetime

try:
    from ..utils.financial_advisor import FinancialAdvisorAgent
    from ..utils.storage import load_investments
    from ..utils.goals import load_goals
except ImportError:
    # Fallback imports for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.financial_advisor import FinancialAdvisorAgent
    from utils.storage import load_investments
    from utils.goals import load_goals

def render_financial_advisor():
    """Render the financial advisor interface"""
    
    st.header("🤖 AI Financial Advisor")
    st.write("Get personalized financial advice based on your portfolio and goals.")
    
    # Initialize the financial advisor
    advisor = FinancialAdvisorAgent()
    
    if not advisor.enabled:
        st.error("🔑 OpenAI API key required for AI advisor features")
        st.info("""
        To enable the AI Financial Advisor:
        1. Get an OpenAI API key from https://platform.openai.com
        2. Set the environment variable: `OPENAI_API_KEY=your_key_here`
        3. Restart the application
        """)
        return
    
    # Load current data
    investments = load_investments()
    goals = load_goals()
    
    # Quick insights panel
    with st.container():
        st.subheader("📊 Quick Insights")
        
        if investments or goals:
            insights = advisor.get_quick_insights(investments, goals)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                portfolio_value = insights.get("portfolio_value", "Not calculated")
                st.metric("Portfolio Value", portfolio_value)
            
            with col2:
                st.metric("Holdings", insights.get("portfolio_summary", "0"))
            
            with col3:
                st.metric("Active Goals", insights.get("goals_summary", "0"))
            
            # Show recommendations
            if insights.get("recommendations"):
                st.write("**Quick Recommendations:**")
                for rec in insights["recommendations"]:
                    st.write(f"• {rec}")
        else:
            st.info("💡 Add some investments and goals to get personalized insights!")
    
    st.divider()
    
    # Chat interface
    st.subheader("💬 Ask Your Financial Advisor")
    
    # Initialize chat history
    if "advisor_messages" not in st.session_state:
        st.session_state.advisor_messages = []
    
    # Example questions
    with st.expander("💡 Example Questions"):
        examples = [
            "How diversified is my portfolio?",
            "Am I on track to meet my financial goals?",
            "Should I invest more in technology stocks?",
            "What's my biggest financial risk right now?",
            "How can I improve my investment strategy?",
            "Analyze my portfolio performance",
            "What sectors should I consider for diversification?",
            "How much should I save monthly to reach my goals?"
        ]
        
        for example in examples:
            if st.button(f"Ask: {example}", key=f"example_{hash(example)}"):
                st.session_state.advisor_messages.append({"role": "user", "content": example})
                st.rerun()
    
    # Display chat history
    for message in st.session_state.advisor_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Check if last message was a user message that needs processing
    if (st.session_state.advisor_messages and 
        st.session_state.advisor_messages[-1]["role"] == "user"):
        
        last_user_message = st.session_state.advisor_messages[-1]["content"]
        
        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your request..."):
                # Process the query with current portfolio and goals data
                response = advisor.process_query(last_user_message, investments, goals)
                st.write(response)
        
        # Add assistant response to chat history
        st.session_state.advisor_messages.append({"role": "assistant", "content": response})
        st.rerun()  # Refresh to show the new message
    
    # Chat input
    if prompt := st.chat_input("Ask your financial advisor anything..."):
        # Add user message to chat history
        st.session_state.advisor_messages.append({"role": "user", "content": prompt})
        st.rerun()  # This will trigger the processing above
    
    st.divider()
    
    # Data context panel
    with st.expander("📋 Current Data Context", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Portfolio Holdings:**")
            if investments:
                for inv in investments:
                    name = inv.get('name', 'Unknown')
                    shares = inv.get('shares', 0)
                    investment_type = inv.get('type', 'Unknown')
                    amount = inv.get('amount', 0)
                    st.write(f"• {name} ({investment_type})")
                    st.write(f"  └ {shares:,.4f} shares - ${amount:,.2f} invested")
            else:
                st.write("No investments added yet")
        
        with col2:
            st.write("**Financial Goals:**")
            if goals:
                for goal in goals:
                    # Import the goal progress calculation function
                    try:
                        from ..utils.goals import calculate_goal_progress
                    except ImportError:
                        from utils.goals import calculate_goal_progress
                    
                    # Calculate actual progress using the proper function
                    progress_data = calculate_goal_progress(goal, investments)
                    progress_percentage = progress_data.get('progress_percentage', 0)
                    
                    st.write(f"• {goal.get('name', 'Unnamed')} - {progress_percentage:.1f}% complete")
            else:
                st.write("No goals set yet")
    
    # Advanced features
    st.subheader("🔧 Advanced Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 Detailed Portfolio Analysis"):
            if investments:
                with st.spinner("Analyzing portfolio..."):
                    analysis_prompt = "Please provide a comprehensive analysis of my current portfolio including diversification, risk assessment, sector allocation, and specific recommendations for improvement."
                    response = advisor.process_query(analysis_prompt, investments, goals)
                    st.session_state.advisor_messages.append({"role": "user", "content": "Portfolio Analysis Request"})
                    st.session_state.advisor_messages.append({"role": "assistant", "content": response})
                    st.success("Analysis complete! Check the chat above.")
                    st.rerun()
            else:
                st.warning("Add some investments first to analyze your portfolio.")
    
    with col2:
        if st.button("🎯 Goals Progress Review"):
            if goals:
                with st.spinner("Reviewing goals..."):
                    goals_prompt = "Please review my progress towards all financial goals and provide specific recommendations on how to accelerate my progress and optimize my strategy."
                    response = advisor.process_query(goals_prompt, investments, goals)
                    st.session_state.advisor_messages.append({"role": "user", "content": "Goals Progress Review"})
                    st.session_state.advisor_messages.append({"role": "assistant", "content": response})
                    st.success("Review complete! Check the chat above.")
                    st.rerun()
            else:
                st.warning("Set some financial goals first to review progress.")
    
    # Clear chat history
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.advisor_messages = []
        st.success("Chat history cleared!")
        st.rerun()

def render_advisor_sidebar_widget():
    """Render a compact advisor widget for the sidebar"""
    st.sidebar.header("🤖 AI Advisor")
    
    advisor = FinancialAdvisorAgent()
    
    if advisor.enabled:
        investments = load_investments()
        goals = load_goals()
        
        if investments or goals:
            insights = advisor.get_quick_insights(investments, goals)
            
            # Show AI insights instead of duplicate portfolio value
            if insights.get("portfolio_summary"):
                st.sidebar.metric("Holdings", insights["portfolio_summary"])
            
            # Show top recommendation
            if insights.get("recommendations"):
                st.sidebar.info(f"💡 {insights['recommendations'][0]}")
            
            if st.sidebar.button("💬 Open AI Advisor"):
                st.session_state.current_page = "🤖 AI Financial Advisor"
                st.rerun()
        else:
            st.sidebar.info("Add investments & goals for AI insights")
    else:
        st.sidebar.warning("🔑 Configure OpenAI API key for AI advisor")

if __name__ == "__main__":
    # For testing the component directly
    st.set_page_config(page_title="Financial Advisor Test", layout="wide")
    render_financial_advisor()
