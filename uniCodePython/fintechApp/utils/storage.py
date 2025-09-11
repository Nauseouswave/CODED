"""
Storage utilities for portfolio data persistence
"""

import streamlit as st
import json
import base64


def save_to_storage(investments):
    """Save investments to browser localStorage"""
    investments_json = json.dumps(investments)
    # Encode to base64 to handle special characters
    encoded_data = base64.b64encode(investments_json.encode()).decode()
    st.query_params["data"] = encoded_data


def load_from_storage():
    """Load investments from browser localStorage"""
    try:
        encoded_data = st.query_params.get("data", "")
        if encoded_data:
            decoded_data = base64.b64decode(encoded_data).decode()
            return json.loads(decoded_data)
    except:
        pass
    return []


def load_investments():
    """Load investments from session state or storage"""
    # First try session state
    if 'investments' in st.session_state:
        return st.session_state.investments
    
    # Fall back to storage
    investments = load_from_storage()
    if investments:
        st.session_state.investments = investments
    
    return investments
