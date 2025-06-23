"""
Settings Page - User Preferences and Configuration
Professional interface for application settings
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
        page_title="⚙️ Settings - AI Boardroom",
        page_icon="⚙️",
        layout="wide"
    )
    
    load_chat_styles()
    
    render_conversation_header(
        "Settings",
        "Customize your AI Boardroom experience"
    )
    
    render_info_message("Settings feature coming in Week 4 of development")
    
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">⚙️ Planned Features</h3>
        </div>
        <div style="margin: 1.5rem 0;">
            <ul>
                <li>User profile management</li>
                <li>Theme selection (dark/light)</li>
                <li>Default model preferences</li>
                <li>Export format settings</li>
                <li>Notification preferences</li>
                <li>API key management</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()