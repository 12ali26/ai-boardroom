"""
Usage Statistics Page - Analytics and Insights
Professional interface for usage analytics
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
        page_title="📊 Usage Statistics - AI Boardroom",
        page_icon="📊",
        layout="wide"
    )
    
    load_chat_styles()
    
    render_conversation_header(
        "Usage Statistics",
        "Track your AI interactions and analytics"
    )
    
    render_info_message("Usage analytics feature coming in Week 4 of development")
    
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">📊 Planned Features</h3>
        </div>
        <div style="margin: 1.5rem 0;">
            <ul>
                <li>Message usage tracking</li>
                <li>Model usage statistics</li>
                <li>Conversation history</li>
                <li>Export usage reports</li>
                <li>Performance metrics</li>
                <li>Cost tracking</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()