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
    render_skeleton_message,
    render_typing_indicator_enhanced,
    render_connection_status,
    render_error_message,
    render_success_message,
    initialize_chat_session,
    add_message_to_session,
    get_session_duration,
    render_modern_chat_messages,
    render_modern_chat_input
)
from components.theme_manager import apply_theme
from components.session_manager import session_manager
from components.ai_integration import (
    initialize_ai_session,
    get_available_models,
    get_ai_response,
    save_message_to_history,
    get_conversation_history,
    get_conversation_summary,
    export_conversation,
    get_model_info,
    check_context_limit,
    get_api_status
)

def main():
    """Main chat page"""
    
    # Set page config - ChatGPT style
    st.set_page_config(
        page_title="💬 AI Chat - AI Boardroom",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="collapsed"  # Start with sidebar collapsed like ChatGPT
    )
    
    # Load styles
    load_chat_styles()
    
    # Apply theme
    apply_theme()
    
    # Initialize session
    session_manager.initialize_global_session()
    initialize_chat_session()
    initialize_ai_session()
    
    # Get or create conversation ID
    conversation_id = session_manager.get_or_create_conversation_id()
    
    # Minimal header like ChatGPT
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #e9ecef;">
        <h3 style="margin: 0; color: #374151;">AI Chat</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Simplified sidebar like ChatGPT
    with st.sidebar:
        # Simple title
        st.markdown("### 💬 AI Chat")
        
        # Model selection - simplified
        available_models = [model['id'] for model in get_available_models()]
        selected_model = st.selectbox(
            "🤖 Model",
            available_models,
            index=available_models.index(st.session_state.get('selected_model', 'openai/gpt-4')) 
            if st.session_state.get('selected_model', 'openai/gpt-4') in available_models else 0,
            key="chat_model_selector"
        )
        st.session_state.selected_model = selected_model
        
        # Show just the model name
        model_info = get_model_info(selected_model)
        st.caption(f"Using {model_info['name']}")
        
        st.markdown("---")
        
        # Essential controls only
        if st.button("+ New Chat", key="new_chat", use_container_width=True):
            session_manager.reset_conversation()
            st.rerun()
        
        # Simple navigation
        st.markdown("**Navigate**")
        
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.switch_page("Home.py")
        
        if st.button("🏢 Boardroom", key="nav_boardroom", use_container_width=True):
            st.switch_page("pages/02_Boardroom.py")
        
        if st.button("📁 Files", key="nav_files", use_container_width=True):
            st.switch_page("pages/03_Files.py")
        
        # Show file context if any
        from components.file_processor import file_processor
        file_context_count = len(st.session_state.get('file_context', {}))
        if file_context_count > 0:
            st.markdown("---")
            st.caption(f"📎 {file_context_count} file(s) in context")
        
        # Simple connection status
        api_status = get_api_status()
        if api_status != "connected":
            st.markdown("---")
            status_icon = {"connecting": "🟡", "error": "🔴", "disconnected": "⚪"}
            st.caption(f"{status_icon.get(api_status, '⚪')} {api_status.title()}")
    
    # Main chat area - centered like ChatGPT/Claude
    st.markdown("""
    <div style="max-width: 768px; margin: 0 auto; padding: 0 1rem;">
    """, unsafe_allow_html=True)
    
    # Chat container
    if len(st.session_state.messages) == 0:
        # Clean welcome message like Claude/ChatGPT
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; color: #6b7280;">
            <h2 style="color: #374151; margin-bottom: 1rem;">Hi! I'm {}</h2>
            <p style="font-size: 1.1rem; margin-bottom: 2rem;">What can I help you with today?</p>
        </div>
        """.format(get_model_info(selected_model)['name']), unsafe_allow_html=True)
    else:
        # Show chat messages - clean ChatGPT style
        render_modern_chat_messages(st.session_state.messages, st.session_state.get('is_typing', False))
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Initialize typing state
    if 'is_typing' not in st.session_state:
        st.session_state.is_typing = False
    
    # Modern chat input - ChatGPT style
    model_name = get_model_info(selected_model)['name']
    
    # Add some spacing before input
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Chat input container
    st.markdown("""
    <div style="
        max-width: 768px;
        margin: 0 auto;
        padding: 0 1rem;
    ">
    """, unsafe_allow_html=True)
    
    message, send_clicked = render_modern_chat_input(
        placeholder=f"Message {model_name}...",
        key="modern_chat_input"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Handle message sending
    if send_clicked and message.strip():
        # Save user message to history
        user_message = {
            'content': message,
            'is_user': True,
            'model': selected_model,
            'timestamp': datetime.now().isoformat()
        }
        
        save_message_to_history(conversation_id, user_message)
        
        # Add user message to session for display
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
            with st.spinner(f"Getting response from {get_model_info(selected_model)['name']}..."):
                try:
                    # Get real AI response
                    response, error = asyncio.run(get_ai_response(
                        last_message['content'], 
                        selected_model,
                        conversation_id
                    ))
                    
                    if error:
                        # Handle error
                        error_content = f"❌ {error}"
                        add_message_to_session(
                            content=error_content,
                            is_user=False,
                            model=selected_model
                        )
                        
                        # Save error to history
                        error_message = {
                            'content': error_content,
                            'is_user': False,
                            'model': selected_model,
                            'timestamp': datetime.now().isoformat()
                        }
                        save_message_to_history(conversation_id, error_message)
                        
                    else:
                        # Add successful AI response
                        add_message_to_session(
                            content=response,
                            is_user=False,
                            model=selected_model
                        )
                        
                        # Save successful response to history
                        ai_message = {
                            'content': response,
                            'is_user': False,
                            'model': selected_model,
                            'timestamp': datetime.now().isoformat()
                        }
                        save_message_to_history(conversation_id, ai_message)
                    
                    # Stop typing
                    st.session_state.is_typing = False
                    st.rerun()
                    
                except Exception as e:
                    # Handle unexpected error
                    error_content = f"❌ Unexpected error: {str(e)}"
                    add_message_to_session(
                        content=error_content,
                        is_user=False,
                        model=selected_model
                    )
                    
                    # Save error to history
                    error_message = {
                        'content': error_content,
                        'is_user': False,
                        'model': selected_model,
                        'timestamp': datetime.now().isoformat()
                    }
                    save_message_to_history(conversation_id, error_message)
                    
                    st.session_state.is_typing = False
                    st.rerun()

if __name__ == "__main__":
    main()