"""
Billing Page - Subscription Management
Professional interface for billing and subscriptions
"""

import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.chat_interface import (
    load_chat_styles,
    render_conversation_header,
    render_info_message
)

def main():
    st.set_page_config(
        page_title="💳 Billing - AI Boardroom",
        page_icon="💳",
        layout="wide"
    )
    
    load_chat_styles()
    
    render_conversation_header(
        "Billing & Subscriptions",
        "Manage your AI Boardroom subscription"
    )
    
    render_info_message("Billing feature coming in Week 4 of development")
    
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">💳 Planned Features</h3>
        </div>
        <div style="margin: 1.5rem 0;">
            <ul>
                <li>Subscription tier management</li>
                <li>Stripe integration</li>
                <li>Usage-based billing</li>
                <li>Invoice history</li>
                <li>Payment method management</li>
                <li>Upgrade/downgrade options</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()