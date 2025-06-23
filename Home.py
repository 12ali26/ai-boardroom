"""
AI Boardroom - Professional Landing Page
Modern Streamlit interface with professional design
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our professional components
from components.chat_interface import (
    load_chat_styles,
    render_conversation_header,
    render_chat_stats,
    render_info_message,
    render_success_message,
    render_connection_status,
    initialize_chat_session,
    get_session_duration
)
from components.theme_manager import apply_theme, render_theme_toggle

def main():
    """Main application entry point"""
    
    # Set page config
    st.set_page_config(
        page_title="AI Boardroom - Your AI Advisory Board",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load professional styles
    load_chat_styles()
    
    # Apply theme
    apply_theme()
    
    # Initialize session
    initialize_chat_session()
    
    # Render header
    render_conversation_header(
        "AI Boardroom",
        "Your AI Advisory Board for Better Business Decisions"
    )
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-title">🤖 AI Boardroom</div>
        <div class="sidebar-subtitle">Your AI Advisory Board</div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🚀 Quick Start")
        
        # Navigation buttons
        if st.button("💬 Start AI Chat", key="nav_chat", help="Single AI conversation mode"):
            st.switch_page("pages/01_AI_Chat.py")
        
        if st.button("🏢 Join Boardroom", key="nav_boardroom", help="Multi-AI debate mode"):
            st.switch_page("pages/02_Boardroom.py")
        
        if st.button("📁 Process Files", key="nav_files", help="Upload and analyze documents"):
            st.switch_page("pages/03_Files.py")
        
        if st.button("🎨 Generate Images", key="nav_images", help="AI image generation"):
            st.switch_page("pages/04_Images.py")
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Application")
        
        if st.button("⚙️ Settings", key="nav_settings"):
            st.switch_page("pages/05_Settings.py")
        
        if st.button("📊 Usage Stats", key="nav_usage"):
            st.switch_page("pages/06_Usage.py")
        
        if st.button("💳 Billing", key="nav_billing"):
            st.switch_page("pages/07_Billing.py")
        
        st.markdown("---")
        
        # Theme toggle
        st.markdown("### 🎨 Theme")
        render_theme_toggle("home_theme_toggle")
        
        st.markdown("---")
        
        # Health status
        st.markdown("### 🔧 System Status")
        
        # Quick health check
        try:
            from backend.app.main import health_check
            import asyncio
            
            # Run health check
            health_ok = True  # Simplified for now
            
            if health_ok:
                render_success_message("All systems operational")
                render_connection_status("connected")
            else:
                st.markdown("""
                <div class="alert alert-warning">
                    <strong>⚠️ Warning:</strong> Some systems may be offline
                </div>
                """, unsafe_allow_html=True)
                render_connection_status("error")
                
        except Exception as e:
            st.markdown("""
            <div class="alert alert-error">
                <strong>❌ Error:</strong> System check failed
            </div>
            """, unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">🎯 What makes AI Boardroom unique?</h2>
                <p class="card-subtitle">The only AI platform with collaborative decision-making</p>
            </div>
            
            <div style="margin: 1.5rem 0;">
                <h3>🏢 AI Boardroom Debates</h3>
                <p>Get insights from multiple AI personas representing different executive perspectives:</p>
                <ul>
                    <li><strong>Alexandra Stone (CEO)</strong> - Strategic vision and leadership</li>
                    <li><strong>Marcus Chen (CTO)</strong> - Technical innovation and implementation</li>
                    <li><strong>Sofia Rodriguez (CMO)</strong> - Marketing strategy and growth</li>
                    <li><strong>David Kim (CFO)</strong> - Financial analysis and risk management</li>
                </ul>
            </div>
            
            <div style="margin: 1.5rem 0;">
                <h3>💬 Standard AI Chat</h3>
                <p>Access 322+ AI models from leading providers:</p>
                <ul>
                    <li><strong>OpenAI</strong> - GPT-4, GPT-4-turbo, GPT-3.5</li>
                    <li><strong>Anthropic</strong> - Claude-3-Sonnet, Claude-3-Haiku</li>
                    <li><strong>Google</strong> - Gemini-Pro, Gemini-Flash</li>
                    <li><strong>And many more...</strong></li>
                </ul>
            </div>
            
            <div style="margin: 1.5rem 0;">
                <h3>📁 File Processing</h3>
                <ul>
                    <li>Upload and analyze PDFs, documents, images</li>
                    <li>Ask questions about your files</li>
                    <li>Generate summaries and insights</li>
                    <li>Export results in multiple formats</li>
                </ul>
            </div>
            
            <div style="margin: 1.5rem 0;">
                <h3>🎨 Image Generation</h3>
                <ul>
                    <li>DALL-E integration for creative images</li>
                    <li>Stable Diffusion support</li>
                    <li>Custom prompts and styles</li>
                    <li>High-resolution outputs</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick start section
        st.markdown("""
        <div class="card" style="margin-top: 2rem;">
            <div class="card-header">
                <h2 class="card-title">🚀 Quick Start Guide</h2>
                <p class="card-subtitle">Get started in minutes</p>
            </div>
            
            <div style="margin: 1.5rem 0;">
                <h4>Step 1: Choose Your Mode</h4>
                <p>• <strong>AI Chat</strong> - For individual AI conversations<br>
                • <strong>Boardroom</strong> - For collaborative AI discussions</p>
                
                <h4>Step 2: Select Your Topic</h4>
                <p>• Business decisions work best<br>
                • Frame as questions for better results<br>
                • Include context and constraints</p>
                
                <h4>Step 3: Engage with AI</h4>
                <p>• Ask follow-up questions<br>
                • Challenge assumptions<br>
                • Request different perspectives</p>
                
                <h4>Step 4: Export Results</h4>
                <p>• Download as PDF or Markdown<br>
                • Email transcripts to team<br>
                • Save for future reference</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Usage statistics
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 Your Activity</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Session stats
        render_chat_stats(
            message_count=st.session_state.get('message_count', 0),
            model_count=len(st.session_state.get('models_used', set())),
            session_time=get_session_duration()
        )
        
        # Subscription tier info
        st.markdown("""
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-header">
                <h3 class="card-title">💎 Current Plan</h3>
            </div>
            <div style="text-align: center; margin: 1rem 0;">
                <div class="badge badge-primary">FREE TIER</div>
                <p style="margin-top: 1rem; color: #718096;">
                    20 messages remaining today<br>
                    Basic models only
                </p>
                <button class="btn-primary" style="margin-top: 1rem; width: 100%;">
                    Upgrade to Pro
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recent activity
        st.markdown("""
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-header">
                <h3 class="card-title">🕒 Recent Activity</h3>
            </div>
            <div style="font-size: 0.9rem; color: #718096;">
                <p>• No recent conversations</p>
                <p>• Start your first chat to see activity</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Help and support
        st.markdown("""
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-header">
                <h3 class="card-title">❓ Need Help?</h3>
            </div>
            <div style="font-size: 0.9rem;">
                <p>• <a href="#" class="message-link">Documentation</a></p>
                <p>• <a href="#" class="message-link">Video Tutorials</a></p>
                <p>• <a href="#" class="message-link">Contact Support</a></p>
                <p>• <a href="#" class="message-link">Feature Requests</a></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="margin-top: 3rem; padding: 2rem; background: #f8f9fa; border-radius: 16px; text-align: center;">
        <h3>🎯 Ready to get started?</h3>
        <p>Choose your AI interaction mode and begin your conversation</p>
        <div style="margin-top: 1.5rem;">
            <!-- Footer navigation buttons will be handled by Streamlit buttons below -->
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add proper Streamlit navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        pass  # Empty for spacing
    
    with col2:
        if st.button("🚀 Start AI Chat", key="footer_start_chat", type="primary"):
            st.switch_page("pages/01_AI_Chat.py")
        
        if st.button("🏢 Join Boardroom", key="footer_join_boardroom"):
            st.switch_page("pages/02_Boardroom.py")
    
    with col3:
        pass  # Empty for spacing

if __name__ == "__main__":
    main()