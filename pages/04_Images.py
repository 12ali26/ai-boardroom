"""
Image Generation Page - AI Image Creation
Professional interface for image generation capabilities
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
        page_title="🎨 Image Generation - AI Boardroom",
        page_icon="🎨",
        layout="wide"
    )
    
    load_chat_styles()
    
    render_conversation_header(
        "Image Generation",
        "Create images with AI models"
    )
    
    render_info_message("Image generation feature coming in Week 3 of development")
    
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">🎨 Planned Features</h3>
        </div>
        <div style="margin: 1.5rem 0;">
            <ul>
                <li>DALL-E integration</li>
                <li>Stable Diffusion support</li>
                <li>Custom prompts and styles</li>
                <li>Image editing capabilities</li>
                <li>Batch generation</li>
                <li>High-resolution exports</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()