"""
Professional Chat Interface Component
WhatsApp-style chat with modern design
"""

import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime
import asyncio

def load_chat_styles():
    """Load professional chat CSS styles"""
    with open("styles/main.css", "r") as f:
        main_css = f.read()
    with open("styles/chat.css", "r") as f:
        chat_css = f.read()
    
    st.markdown(f"""
    <style>
    {main_css}
    {chat_css}
    </style>
    """, unsafe_allow_html=True)

def render_message(message: Dict, is_user: bool = False, persona: Optional[str] = None):
    """Render a single message with professional styling"""
    
    if is_user:
        # User message (right-aligned, blue gradient)
        st.markdown(f"""
        <div class="user-message">
            {message.get('content', '')}
            <div class="message-meta">
                {message.get('timestamp', datetime.now().strftime('%H:%M'))}
                <span class="message-status status-delivered">✓✓</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    elif persona:
        # AI persona message with specific styling
        persona_class = f"{persona.lower()}-message" if persona.lower() in ['ceo', 'cto', 'cmo', 'cfo'] else "ai-message"
        
        st.markdown(f"""
        <div class="{persona_class}">
            <div class="persona-badge">{persona}</div>
            {message.get('content', '')}
            <div class="message-meta">
                {message.get('timestamp', datetime.now().strftime('%H:%M'))}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Regular AI message (left-aligned, light gray)
        st.markdown(f"""
        <div class="ai-message">
            {message.get('content', '')}
            <div class="message-meta">
                {message.get('timestamp', datetime.now().strftime('%H:%M'))}
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_typing_indicator(persona: Optional[str] = None):
    """Render animated typing indicator"""
    persona_text = f"{persona} is typing..." if persona else "AI is typing..."
    
    st.markdown(f"""
    <div class="typing-indicator">
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    </div>
    <div style="font-size: 0.8rem; color: #718096; margin-left: 18px; margin-top: -8px;">
        {persona_text}
    </div>
    """, unsafe_allow_html=True)

def render_chat_container(messages: List[Dict], show_typing: bool = False, typing_persona: Optional[str] = None):
    """Render the main chat container with all messages"""
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown('<div class="messages-container">', unsafe_allow_html=True)
    
    # Render all messages
    for message in messages:
        render_message(
            message, 
            is_user=message.get('is_user', False),
            persona=message.get('persona')
        )
    
    # Show typing indicator if needed
    if show_typing:
        render_typing_indicator(typing_persona)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close messages-container
    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container

def render_chat_input(placeholder: str = "Type your message...", key: str = "chat_input"):
    """Render professional chat input with send button"""
    
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # Create two columns for input and button
    col1, col2 = st.columns([6, 1])
    
    with col1:
        message = st.text_input(
            "",
            placeholder=placeholder,
            key=key,
            label_visibility="collapsed"
        )
    
    with col2:
        send_clicked = st.button("➤", key=f"{key}_send", help="Send message")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Return both the message and whether send was clicked
    return message, send_clicked

def render_model_selector(models: List[str], default_model: Optional[str] = None, key: str = "model_select"):
    """Render professional model selector"""
    
    st.markdown("""
    <div class="model-selector-container">
        <label class="model-selector-label">🤖 AI Model</label>
    </div>
    """, unsafe_allow_html=True)
    
    selected_model = st.selectbox(
        "",
        options=models,
        index=models.index(default_model) if default_model in models else 0,
        key=key,
        label_visibility="collapsed"
    )
    
    return selected_model

def render_mode_toggle(current_mode: str = "chat", key: str = "mode_toggle"):
    """Render toggle between Chat and Boardroom modes"""
    
    st.markdown("""
    <div class="mode-toggle-container">
        <div class="mode-toggle-label">💬 Mode Selection</div>
    </div>
    """, unsafe_allow_html=True)
    
    mode = st.radio(
        "",
        options=["Chat", "Boardroom"],
        index=0 if current_mode == "chat" else 1,
        key=key,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    return mode.lower()

def render_conversation_header(title: str, subtitle: Optional[str] = None, mode: str = "chat"):
    """Render professional conversation header"""
    
    mode_icon = "🏢" if mode == "boardroom" else "💬"
    mode_text = "AI Boardroom Discussion" if mode == "boardroom" else "AI Chat"
    
    st.markdown(f"""
    <div class="app-header">
        <h1>{mode_icon} {title}</h1>
        <p>{subtitle or mode_text}</p>
    </div>
    """, unsafe_allow_html=True)

def render_persona_selector(personas: List[Dict], key: str = "persona_select"):
    """Render persona selector for boardroom mode"""
    
    st.markdown("""
    <div class="persona-selector-container">
        <label class="persona-selector-label">🎭 Available Personas</label>
    </div>
    """, unsafe_allow_html=True)
    
    persona_options = [f"{p['name']} ({p['role']})" for p in personas]
    
    selected = st.multiselect(
        "",
        options=persona_options,
        default=persona_options,  # All selected by default
        key=key,
        label_visibility="collapsed"
    )
    
    return selected

def render_chat_stats(message_count: int, model_count: int, session_time: str):
    """Render chat statistics"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{message_count}</div>
            <div class="metric-label">Messages</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{model_count}</div>
            <div class="metric-label">Models Used</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{session_time}</div>
            <div class="metric-label">Session Time</div>
        </div>
        """, unsafe_allow_html=True)

def render_export_options():
    """Render conversation export options"""
    
    st.markdown("""
    <div class="export-container">
        <h3>📤 Export Conversation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as PDF", key="export_pdf"):
            return "pdf"
    
    with col2:
        if st.button("📝 Export as Markdown", key="export_md"):
            return "markdown"
    
    with col3:
        if st.button("📧 Email Transcript", key="export_email"):
            return "email"
    
    return None

def render_loading_message(message: str = "Processing your request..."):
    """Render loading message with animation"""
    
    st.markdown(f"""
    <div class="ai-message message-loading">
        <div class="spinner"></div>
        <div style="margin-left: 10px; display: inline-block;">{message}</div>
    </div>
    """, unsafe_allow_html=True)

def render_error_message(error: str, show_retry: bool = True):
    """Render error message with optional retry button"""
    
    st.markdown(f"""
    <div class="alert alert-error">
        <strong>⚠️ Error:</strong> {error}
    </div>
    """, unsafe_allow_html=True)
    
    if show_retry:
        return st.button("🔄 Retry", key="retry_button")
    
    return False

def render_success_message(message: str):
    """Render success message"""
    
    st.markdown(f"""
    <div class="alert alert-success">
        <strong>✅ Success:</strong> {message}
    </div>
    """, unsafe_allow_html=True)

def render_info_message(message: str):
    """Render info message"""
    
    st.markdown(f"""
    <div class="alert alert-info">
        <strong>ℹ️ Info:</strong> {message}
    </div>
    """, unsafe_allow_html=True)

def initialize_chat_session():
    """Initialize chat session state"""
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = 'chat'
    
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = 'gpt-4'
    
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    
    if 'message_count' not in st.session_state:
        st.session_state.message_count = 0
    
    if 'models_used' not in st.session_state:
        st.session_state.models_used = set()

def add_message_to_session(content: str, is_user: bool = False, persona: Optional[str] = None, model: Optional[str] = None):
    """Add a message to the session state"""
    
    message = {
        'content': content,
        'is_user': is_user,
        'persona': persona,
        'model': model,
        'timestamp': datetime.now().strftime('%H:%M'),
        'full_timestamp': datetime.now()
    }
    
    st.session_state.messages.append(message)
    st.session_state.message_count += 1
    
    if model:
        st.session_state.models_used.add(model)

def get_session_duration():
    """Get formatted session duration"""
    
    if 'session_start_time' not in st.session_state:
        return "0m"
    
    duration = datetime.now() - st.session_state.session_start_time
    total_minutes = int(duration.total_seconds() / 60)
    
    if total_minutes < 60:
        return f"{total_minutes}m"
    else:
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m"