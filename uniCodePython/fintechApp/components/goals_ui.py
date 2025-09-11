"""
Goals tracking UI components
"""

import streamlit as st
from datetime import datetime, date, timedelta
from utils.goals import (
    create_goal, calculate_goal_progress, save_goals, load_goals,
    get_goal_status_color, get_goal_recommendations, get_popular_goal_templates
)
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO


def render_goals_dashboard():
    """Render the main goals dashboard"""
    st.header("🎯 Investment Goals")
    st.write("Set and track your investment goals to stay motivated and on track!")
    
    # Load existing goals
    goals = load_goals()
    investments = st.session_state.get('investments', [])
    
    # Quick stats
    if goals:
        col1, col2, col3, col4 = st.columns(4)
        
        total_goals = len(goals)
        active_goals = len([g for g in goals if g['is_active']])
        completed_goals = 0
        total_target = 0
        
        for goal in goals:
            if goal['is_active']:
                progress = calculate_goal_progress(goal, investments)
                total_target += goal['target_amount']
                if progress['progress_percentage'] >= 100:
                    completed_goals += 1
        
        with col1:
            st.metric("Total Goals", total_goals)
        with col2:
            st.metric("Active Goals", active_goals)
        with col3:
            st.metric("Completed", completed_goals)
        with col4:
            st.metric("Target Value", f"${total_target:,.0f}")
    
    st.divider()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["📊 My Goals", "➕ Add New Goal"])
    
    with tab1:
        render_goals_list(goals, investments)
    
    with tab2:
        render_add_goal_form()


def render_goals_list(goals, investments):
    """Render the list of existing goals with progress"""
    if not goals:
        st.info("🎯 No goals set yet! Create your first goal in the 'Add New Goal' tab.")
        return
    
    st.subheader("Your Investment Goals")
    
    for i, goal in enumerate(goals):
        if not goal['is_active']:
            continue
            
        progress = calculate_goal_progress(goal, investments)
        status_color = get_goal_status_color(progress['progress_percentage'], progress['days_remaining'])
        
        # Goal container
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"{status_color} {goal['name']}")
                if goal['description']:
                    st.write(goal['description'])
                
                # Progress bar
                progress_color = "green" if progress['progress_percentage'] >= 75 else "orange" if progress['progress_percentage'] >= 50 else "red"
                st.progress(progress['progress_percentage'] / 100)
                
                # Progress details
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Current Amount", f"${progress['current_amount']:,.2f}")
                with col_b:
                    st.metric("Target Amount", f"${goal['target_amount']:,.2f}")
                with col_c:
                    st.metric("Progress", f"{progress['progress_percentage']:.1f}%")
                
                # Time and savings info
                col_d, col_e, col_f = st.columns(3)
                with col_d:
                    if progress['days_remaining'] > 0:
                        st.metric("Days Remaining", progress['days_remaining'])
                    else:
                        st.metric("Days Remaining", "Overdue", delta_color="inverse")
                with col_e:
                    st.metric("Remaining", f"${progress['remaining_amount']:,.2f}")
                with col_f:
                    if progress['monthly_savings_needed'] > 0:
                        st.metric("Monthly Savings Needed", f"${progress['monthly_savings_needed']:.2f}")
                    else:
                        st.metric("Monthly Savings Needed", "Goal Reached! 🎉")
                
                # Recommendations
                recommendations = get_goal_recommendations(goal, progress)
                if recommendations:
                    with st.expander("💡 Recommendations"):
                        for rec in recommendations:
                            st.write(rec)
                
                # Show filtered investments
                if progress['filtered_investments']:
                    with st.expander(f"📈 Relevant Investments ({len(progress['filtered_investments'])})"):
                        for inv in progress['filtered_investments']:
                            st.write(f"• {inv['name']}: ${inv['amount']:,.2f}")
            
            with col2:
                st.write("**Target Date**")
                target_date = datetime.fromisoformat(goal['target_date']).strftime("%B %d, %Y")
                st.write(target_date)
                
                st.write("")  # Spacing
                if st.button(f"✏️ Edit", key=f"edit_goal_{i}"):
                    st.session_state[f'editing_goal_{i}'] = True
                    st.rerun()
                
                if st.button(f"🗑️ Delete", key=f"delete_goal_{i}"):
                    goals.remove(goal)
                    save_goals(goals)
                    st.success(f"Deleted goal: {goal['name']}")
                    st.rerun()
        
        # Edit form (if editing)
        if st.session_state.get(f'editing_goal_{i}', False):
            render_edit_goal_form(goal, i)
        
        st.divider()


def render_add_goal_form():
    """Render the form to add a new goal"""
    st.subheader("Create New Investment Goal")
    
    # Goal templates
    with st.expander("🚀 Quick Start Templates", expanded=True):
        st.write("Choose from popular goal templates:")
        
        templates = get_popular_goal_templates()
        
        cols = st.columns(3)
        for i, template in enumerate(templates):
            with cols[i % 3]:
                if st.button(f"📋 {template['name']}", key=f"template_{i}"):
                    st.session_state.template_selected = template
                    st.rerun()
    
    st.divider()
    
    # Check if template was selected
    template = st.session_state.get('template_selected', None)
    
    # Goal form
    with st.form("add_goal_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            goal_name = st.text_input(
                "Goal Name*", 
                value=template['name'] if template else "",
                placeholder="e.g., Emergency Fund"
            )
            
            target_amount = st.number_input(
                "Target Amount ($)*", 
                min_value=100.0, 
                value=float(template['target_amount']) if template else 10000.0,
                step=100.0
            )
            
            description = st.text_area(
                "Description (Optional)", 
                value=template['description'] if template else "",
                placeholder="What is this goal for?"
            )
        
        with col2:
            # Target date
            default_date = date.today() + timedelta(days=template['default_timeline_months'] * 30 if template else 365)
            target_date = st.date_input(
                "Target Date*", 
                min_value=date.today(),
                value=default_date
            )
            
            # Investment filter options
            st.write("**Filter Investments (Optional)**")
            filter_type = st.selectbox(
                "Filter by:",
                ["All Investments", "Investment Type", "Specific Investments", "Risk Level"]
            )
            
            investment_filter = {}
            
            if filter_type == "Investment Type":
                selected_types = st.multiselect(
                    "Select Investment Types:",
                    ["Stocks", "Bonds", "Real Estate", "Cryptocurrency"],
                    default=template.get('investment_filter', {}).get('investment_types', []) if template else []
                )
                if selected_types:
                    investment_filter['investment_types'] = selected_types
            
            elif filter_type == "Specific Investments":
                investments = st.session_state.get('investments', [])
                if investments:
                    investment_names = [inv['name'] for inv in investments]
                    selected_investments = st.multiselect(
                        "Select Specific Investments:",
                        investment_names,
                        default=template.get('investment_filter', {}).get('specific_investments', []) if template else []
                    )
                    if selected_investments:
                        investment_filter['specific_investments'] = selected_investments
                else:
                    st.info("Add some investments first to use this filter")
            
            elif filter_type == "Risk Level":
                selected_risks = st.multiselect(
                    "Select Risk Levels:",
                    ["Low", "Medium", "High"],
                    default=template.get('investment_filter', {}).get('risk_levels', []) if template else []
                )
                if selected_risks:
                    investment_filter['risk_levels'] = selected_risks
        
        submitted = st.form_submit_button("🎯 Create Goal", type="primary")
        
        if submitted:
            if goal_name and target_amount > 0:
                new_goal = create_goal(
                    name=goal_name,
                    target_amount=target_amount,
                    target_date=target_date.isoformat(),
                    investment_filter=investment_filter,
                    description=description
                )
                
                goals = load_goals()
                goals.append(new_goal)
                save_goals(goals)
                
                # Clear template selection
                if 'template_selected' in st.session_state:
                    del st.session_state.template_selected
                
                st.success(f"🎉 Goal '{goal_name}' created successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("Please fill in all required fields")


def render_edit_goal_form(goal, goal_index):
    """Render form to edit an existing goal"""
    st.subheader(f"✏️ Edit Goal: {goal['name']}")
    
    with st.form(f"edit_goal_form_{goal_index}"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Goal Name", value=goal['name'])
            new_target = st.number_input("Target Amount ($)", value=goal['target_amount'], min_value=100.0)
            new_description = st.text_area("Description", value=goal.get('description', ''))
        
        with col2:
            current_date = datetime.fromisoformat(goal['target_date']).date()
            new_date = st.date_input("Target Date", value=current_date, min_value=date.today())
        
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            if st.form_submit_button("💾 Save Changes", type="primary"):
                goal['name'] = new_name
                goal['target_amount'] = new_target
                goal['target_date'] = new_date.isoformat()
                goal['description'] = new_description
                
                goals = load_goals()
                save_goals(goals)
                
                st.session_state[f'editing_goal_{goal_index}'] = False
                st.success("Goal updated successfully!")
                st.rerun()
        
        with col_cancel:
            if st.form_submit_button("❌ Cancel"):
                st.session_state[f'editing_goal_{goal_index}'] = False
                st.rerun()


def render_goals_sidebar_widget():
    """Render a compact goals widget for the sidebar"""
    goals = load_goals()
    investments = st.session_state.get('investments', [])
    
    if not goals:
        return
    
    st.subheader("🎯 Goals Progress")
    
    active_goals = [g for g in goals if g['is_active']][:3]  # Show top 3
    
    for goal in active_goals:
        progress = calculate_goal_progress(goal, investments)
        status_color = get_goal_status_color(progress['progress_percentage'], progress['days_remaining'])
        
        st.write(f"{status_color} **{goal['name']}**")
        st.progress(progress['progress_percentage'] / 100)
        st.caption(f"{progress['progress_percentage']:.1f}% complete")
    
    if len([g for g in goals if g['is_active']]) > 3:
        st.caption(f"+ {len([g for g in goals if g['is_active']]) - 3} more goals")
