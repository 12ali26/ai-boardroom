"""
AI Chat Page - Single AI Conversations
Professional interface for individual AI model interactions
"""

import streamlit as st
import sys
import os
from datetime import datetime
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components and backend
from components.chat_interface import (
    load_chat_styles,
    render_conversation_header,
    render_chat_container,
    render_chat_input,
    render_model_selector,
    render_chat_stats,
    render_export_options,
    render_loading_message,
    render_error_message,
    render_success_message,
    initialize_chat_session,
    add_message_to_session,
    get_session_duration
)

def get_available_models():
    """Get list of available AI models"""
    return [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "claude-3-sonnet",
        "claude-3-haiku",
        "gemini-pro",
        "gemini-flash"
    ]

async def get_ai_response(message: str, model: str):
    """Get AI response (placeholder for now)"""
    try:
        # Import backend components
        from backend.app.openrouter import OpenRouterClient
        from backend.app.validators import InputValidator
        
        # Validate input
        is_valid, cleaned_message, warnings = InputValidator.validate_topic(message)
        if not is_valid:
            return f"⚠️ Input validation failed: {warnings[0] if warnings else 'Invalid input'}"
        
        # Create OpenRouter client and get response
        client = OpenRouterClient()
        
        # Simplified response for now - replace with actual API call
        response = f"This is a response from {model} to: '{cleaned_message}'"
        
        return response
        
    except Exception as e:
        return f"❌ Error getting AI response: {str(e)}"

def main():
    """Main chat page"""
    
    # Set page config
    st.set_page_config(
        page_title="AI Chat - AI Boardroom",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load styles
    load_chat_styles()
    
    # Initialize session
    initialize_chat_session()
    
    # Render header
    render_conversation_header(
        "AI Chat",
        "Have a conversation with any AI model",
        mode="chat"
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-title">💬 AI Chat</div>
        <div class="sidebar-subtitle">Single AI Conversations</div>
        """, unsafe_allow_html=True)
        
        # Model selection
        st.markdown("### 🤖 Select AI Model")
        available_models = get_available_models()
        selected_model = render_model_selector(
            models=available_models,
            default_model=st.session_state.get('selected_model', 'gpt-4'),
            key="chat_model_selector"
        )
        st.session_state.selected_model = selected_model
        
        # Display model info
        model_info = {
            "gpt-4": "Most capable OpenAI model",
            "gpt-4-turbo": "Faster GPT-4 variant",
            "gpt-3.5-turbo": "Fast and efficient",
            "claude-3-sonnet": "Anthropic's balanced model",
            "claude-3-haiku": "Anthropic's fastest model",
            "gemini-pro": "Google's most capable model",
            "gemini-flash": "Google's fastest model"
        }
        
        st.markdown(f"""
        <div class="alert alert-info">
            <strong>{selected_model}</strong><br>
            {model_info.get(selected_model, "AI model")}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Chat controls
        st.markdown("### ⚙️ Chat Controls")
        
        if st.button("🔄 New Conversation", key="new_chat"):
            st.session_state.messages = []
            st.session_state.message_count = 0
            st.rerun()
        
        if st.button("🧹 Clear History", key="clear_chat"):
            st.session_state.messages = []
            st.session_state.message_count = 0
            st.session_state.models_used = set()
            render_success_message("Chat history cleared")
            st.rerun()
        
        st.markdown("---")
        
        # Export options
        export_format = render_export_options()
        if export_format:
            render_success_message(f"Conversation exported as {export_format}")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        if st.button("🏠 Home", key="nav_home"):
            st.switch_page("Home.py")
        
        if st.button("🏢 Boardroom", key="nav_boardroom"):
            st.switch_page("pages/02_🏢_Boardroom.py")
        
        if st.button("📁 Files", key="nav_files"):
            st.switch_page("pages/03_📁_Files.py")
        
        if st.button("🎨 Images", key="nav_images"):
            st.switch_page("pages/04_🎨_Images.py")
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat container
        if len(st.session_state.messages) == 0:
            # Welcome message for new chat
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">👋 Welcome to AI Chat</h3>
                    <p class="card-subtitle">Start a conversation with {}</p>
                </div>
                <div style="margin: 1.5rem 0;">
                    <h4>💡 Tips for better conversations:</h4>
                    <ul>
                        <li>Be specific and detailed in your questions</li>
                        <li>Provide context for better responses</li>
                        <li>Ask follow-up questions to dive deeper</li>
                        <li>Try different models for varied perspectives</li>
                    </ul>
                    
                    <h4>🎯 Example prompts:</h4>
                    <ul>
                        <li>"Help me analyze the pros and cons of remote work"</li>
                        <li>"Explain quantum computing in simple terms"</li>
                        <li>"Write a business plan for a coffee shop"</li>
                        <li>"Debug this Python code: [paste code]"</li>
                    </ul>
                </div>
            </div>
            """.format(selected_model), unsafe_allow_html=True)
        else:
            # Show chat messages
            render_chat_container(
                messages=st.session_state.messages,
                show_typing=st.session_state.get('is_typing', False),
                typing_persona=None
            )
    
    with col2:
        # Chat statistics
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 Chat Stats</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        render_chat_stats(
            message_count=st.session_state.get('message_count', 0),
            model_count=len(st.session_state.get('models_used', set())),
            session_time=get_session_duration()
        )
        
        # Recent models
        if st.session_state.get('models_used'):
            st.markdown("""
            <div class="card" style="margin-top: 1rem;">
                <div class="card-header">
                    <h4 class="card-title">🤖 Models Used</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            for model in st.session_state.models_used:
                st.markdown(f"""
                <div class="badge badge-secondary" style="margin: 0.25rem;">
                    {model}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input (full width at bottom)
    st.markdown("---")
    
    # Initialize typing state
    if 'is_typing' not in st.session_state:
        st.session_state.is_typing = False
    
    # Chat input
    message, send_clicked = render_chat_input(
        placeholder=f"Ask {selected_model} anything...",
        key="main_chat_input"
    )
    
    # Handle message sending
    if send_clicked and message.strip():
        # Add user message
        add_message_to_session(
            content=message,
            is_user=True,
            model=selected_model
        )
        
        # Show typing indicator
        st.session_state.is_typing = True
        st.rerun()
    
    # Process AI response if we have a pending message
    if st.session_state.is_typing and len(st.session_state.messages) > 0:
        last_message = st.session_state.messages[-1]
        
        if last_message.get('is_user', False):
            # Get AI response
            with st.spinner(f"Getting response from {selected_model}..."):
                try:
                    # Simulate async call
                    response = asyncio.run(get_ai_response(
                        last_message['content'], 
                        selected_model
                    ))
                    
                    # Add AI response
                    add_message_to_session(
                        content=response,
                        is_user=False,
                        model=selected_model
                    )
                    
                    # Stop typing
                    st.session_state.is_typing = False
                    st.rerun()
                    
                except Exception as e:
                    # Handle error
                    add_message_to_session(
                        content=f"❌ Error: {str(e)}",
                        is_user=False,
                        model=selected_model
                    )
                    
                    st.session_state.is_typing = False
                    st.rerun()

if __name__ == "__main__":
    main()