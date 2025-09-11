"""
Goals tracking utilities for portfolio management
"""

import streamlit as st
from datetime import datetime, date
from typing import List, Dict, Optional
import json


def create_goal(name: str, target_amount: float, target_date: str, 
               investment_filter: Dict = None, description: str = "") -> Dict:
    """Create a new investment goal"""
    return {
        'id': f"goal_{int(datetime.now().timestamp())}",
        'name': name,
        'target_amount': target_amount,
        'target_date': target_date,
        'investment_filter': investment_filter or {},
        'description': description,
        'created_date': datetime.now().isoformat(),
        'is_active': True
    }


def calculate_goal_progress(goal: Dict, investments: List[Dict]) -> Dict:
    """Calculate progress towards a specific goal"""
    # Ensure investments is a list (handle None case)
    if investments is None:
        investments = []
    
    # Filter investments based on goal criteria
    filtered_investments = filter_investments_for_goal(investments, goal['investment_filter'])
    
    # Calculate current amount
    current_amount = sum(inv['amount'] for inv in filtered_investments)
    
    # Calculate progress percentage
    progress_percentage = min((current_amount / goal['target_amount']) * 100, 100)
    
    # Calculate remaining amount
    remaining_amount = max(goal['target_amount'] - current_amount, 0)
    
    # Calculate days remaining
    days_remaining = calculate_days_remaining(goal['target_date'])
    
    # Calculate savings needed
    daily_savings_needed = remaining_amount / max(days_remaining, 1) if days_remaining > 0 else 0
    monthly_savings_needed = daily_savings_needed * 30
    
    # Check if on track (simple heuristic)
    is_on_track = progress_percentage >= 50 if days_remaining > 365 else progress_percentage >= 80
    
    return {
        'current_amount': current_amount,
        'progress_percentage': progress_percentage,
        'remaining_amount': remaining_amount,
        'days_remaining': days_remaining,
        'daily_savings_needed': daily_savings_needed,
        'monthly_savings_needed': monthly_savings_needed,
        'is_on_track': is_on_track,
        'filtered_investments': filtered_investments
    }


def filter_investments_for_goal(investments: List[Dict], investment_filter: Dict) -> List[Dict]:
    """Filter investments based on goal criteria"""
    # Handle None or empty investments
    if not investments:
        return []
    
    if not investment_filter:
        return investments
    
    filtered = []
    
    for inv in investments:
        include = True
        
        # Filter by investment type
        if 'investment_types' in investment_filter:
            if inv['type'] not in investment_filter['investment_types']:
                include = False
        
        # Filter by specific investments
        if 'specific_investments' in investment_filter:
            if inv['name'] not in investment_filter['specific_investments']:
                include = False
        
        # Filter by risk level
        if 'risk_levels' in investment_filter:
            if inv['risk_level'] not in investment_filter['risk_levels']:
                include = False
        
        if include:
            filtered.append(inv)
    
    return filtered


def calculate_days_remaining(target_date_str: str) -> int:
    """Calculate days remaining until target date"""
    try:
        if isinstance(target_date_str, str):
            target_date = datetime.fromisoformat(target_date_str).date()
        else:
            target_date = target_date_str
        
        today = date.today()
        delta = target_date - today
        return max(delta.days, 0)
    except:
        return 0


def save_goals(goals: List[Dict]):
    """Save goals to session state and localStorage"""
    st.session_state.investment_goals = goals
    # Could extend this to save to file or database


def load_goals() -> List[Dict]:
    """Load goals from session state"""
    return st.session_state.get('investment_goals', [])


def get_goal_status_color(progress_percentage: float, days_remaining: int) -> str:
    """Get color for goal status based on progress and time remaining"""
    if progress_percentage >= 100:
        return "🟢"  # Complete
    elif progress_percentage >= 75:
        return "🟡"  # On track
    elif days_remaining < 30:
        return "🔴"  # Urgent
    elif progress_percentage >= 50:
        return "🟠"  # Moderate progress
    else:
        return "🔴"  # Behind


def get_goal_recommendations(goal: Dict, progress: Dict) -> List[str]:
    """Get recommendations for achieving the goal"""
    recommendations = []
    
    if progress['progress_percentage'] < 25 and progress['days_remaining'] < 365:
        recommendations.append("⚠️ Consider increasing your investment amount to reach this goal")
    
    if progress['monthly_savings_needed'] > 0:
        recommendations.append(f"💡 Save ${progress['monthly_savings_needed']:.2f} per month to stay on track")
    
    if progress['progress_percentage'] >= 100:
        recommendations.append("🎉 Congratulations! You've reached your goal!")
    elif progress['progress_percentage'] >= 75:
        recommendations.append("✨ Great progress! You're on track to reach your goal")
    
    if progress['days_remaining'] < 30 and progress['progress_percentage'] < 90:
        recommendations.append("🚨 Goal deadline is approaching - consider increasing investments")
    
    return recommendations


def get_popular_goal_templates() -> List[Dict]:
    """Get popular goal templates for quick setup"""
    return [
        {
            'name': 'Emergency Fund',
            'target_amount': 25000,
            'description': 'Build a 6-month emergency fund',
            'investment_filter': {'investment_types': ['Bonds'], 'risk_levels': ['Low']},
            'default_timeline_months': 24
        },
        {
            'name': 'House Down Payment',
            'target_amount': 100000,
            'description': 'Save for a house down payment',
            'investment_filter': {'investment_types': ['Stocks', 'Bonds'], 'risk_levels': ['Low', 'Medium']},
            'default_timeline_months': 60
        },
        {
            'name': 'Retirement Fund',
            'target_amount': 500000,
            'description': 'Build retirement savings',
            'investment_filter': {},  # All investments
            'default_timeline_months': 240
        },
        {
            'name': 'Bitcoin Holdings',
            'target_amount': 100000,
            'description': 'Accumulate Bitcoin for long-term growth',
            'investment_filter': {'specific_investments': ['Bitcoin (BTC)']},
            'default_timeline_months': 36
        },
        {
            'name': 'Index Fund Portfolio',
            'target_amount': 50000,
            'description': 'Build a diversified index fund portfolio',
            'investment_filter': {'specific_investments': ['S&P 500 ETF (SPY)', 'QQQ Nasdaq ETF (QQQ)', 'SPDR S&P 500 ETF Trust (SPUS)']},
            'default_timeline_months': 60
        },
        {
            'name': 'Education Fund',
            'target_amount': 75000,
            'description': 'Save for education expenses',
            'investment_filter': {'investment_types': ['Stocks', 'Bonds'], 'risk_levels': ['Low', 'Medium']},
            'default_timeline_months': 120
        }
    ]
