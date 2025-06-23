"""
AI Boardroom Page - Multi-AI Debates
Professional interface for collaborative AI discussions
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
    render_persona_selector,
    render_chat_stats,
    render_export_options,
    render_loading_message,
    render_error_message,
    render_success_message,
    render_info_message,
    initialize_chat_session,
    add_message_to_session,
    get_session_duration
)

def get_available_personas():
    """Get list of available AI personas"""
    return [
        {
            "name": "Alexandra Stone",
            "role": "CEO",
            "model": "gpt-4",
            "personality": "Strategic visionary focused on growth and leadership",
            "expertise": "Business strategy, leadership, market analysis",
            "color": "#e53e3e"
        },
        {
            "name": "Marcus Chen",
            "role": "CTO", 
            "model": "claude-3-sonnet",
            "personality": "Technical innovator focused on implementation",
            "expertise": "Technology, engineering, system architecture",
            "color": "#38a169"
        },
        {
            "name": "Sofia Rodriguez",
            "role": "CMO",
            "model": "gemini-pro",
            "personality": "Creative strategist focused on growth and engagement",
            "expertise": "Marketing, branding, customer acquisition",
            "color": "#dd6b20"
        },
        {
            "name": "David Kim",
            "role": "CFO",
            "model": "gpt-4-turbo",
            "personality": "Analytical thinker focused on financial prudence",
            "expertise": "Finance, risk management, business metrics",
            "color": "#3182ce"
        }
    ]

async def start_boardroom_discussion(topic: str, selected_personas):
    """Start a new boardroom discussion"""
    try:
        # Import backend components
        from backend.app.debate import DiscussionManager
        from backend.app.validators import InputValidator
        
        # Validate topic
        is_valid, cleaned_topic, warnings = InputValidator.validate_topic(topic)
        if not is_valid:
            return None, f"Topic validation failed: {warnings[0] if warnings else 'Invalid topic'}"
        
        # Initialize discussion manager
        discussion_manager = DiscussionManager(use_database=True)
        
        # Start discussion
        discussion_id = discussion_manager.start_discussion(cleaned_topic)
        
        return discussion_id, None
        
    except Exception as e:
        return None, f"Error starting discussion: {str(e)}"

async def get_next_boardroom_response(discussion_id: str):
    """Get next response in boardroom discussion"""
    try:
        from backend.app.debate import DiscussionManager
        
        # Get discussion manager from session state
        discussion_manager = st.session_state.get('discussion_manager')
        if not discussion_manager:
            discussion_manager = DiscussionManager(use_database=True)
            st.session_state.discussion_manager = discussion_manager
        
        # Get next response
        response = await discussion_manager.get_next_response(discussion_id)
        
        if "error" in response:
            return None, response["error"]
        
        return response, None
        
    except Exception as e:
        return None, f"Error getting response: {str(e)}"

def main():
    """Main boardroom page"""
    
    # Set page config
    st.set_page_config(
        page_title="AI Boardroom - AI Boardroom",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load styles
    load_chat_styles()
    
    # Initialize session
    initialize_chat_session()
    
    # Initialize boardroom-specific session state
    if 'boardroom_discussion_id' not in st.session_state:
        st.session_state.boardroom_discussion_id = None
    
    if 'boardroom_active' not in st.session_state:
        st.session_state.boardroom_active = False
    
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = ""
    
    if 'selected_personas' not in st.session_state:
        st.session_state.selected_personas = []
    
    # Render header
    render_conversation_header(
        "AI Boardroom",
        "Collaborative AI discussions with executive personas",
        mode="boardroom"
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-title">🏢 AI Boardroom</div>
        <div class="sidebar-subtitle">Multi-AI Executive Debates</div>
        """, unsafe_allow_html=True)
        
        # Persona selection
        st.markdown("### 🎭 Select Personas")
        available_personas = get_available_personas()
        
        # Show persona cards
        for persona in available_personas:
            selected = st.checkbox(
                f"**{persona['name']}** ({persona['role']})",
                value=True,
                key=f"persona_{persona['role'].lower()}",
                help=f"{persona['personality']} | Model: {persona['model']}"
            )
            
            if selected and persona not in st.session_state.selected_personas:
                st.session_state.selected_personas.append(persona)
            elif not selected and persona in st.session_state.selected_personas:
                st.session_state.selected_personas.remove(persona)
        
        st.markdown("---")
        
        # Discussion controls
        st.markdown("### ⚙️ Discussion Controls")
        
        if not st.session_state.boardroom_active:
            if st.button("🚀 New Discussion", key="new_discussion"):
                # Reset for new discussion
                st.session_state.messages = []
                st.session_state.boardroom_discussion_id = None
                st.session_state.boardroom_active = False
                st.session_state.current_topic = ""
                st.rerun()
        else:
            if st.button("⏹️ End Discussion", key="end_discussion"):
                st.session_state.boardroom_active = False
                st.session_state.boardroom_discussion_id = None
                render_success_message("Discussion ended")
                st.rerun()
            
            if st.button("⏭️ Next Response", key="next_response"):
                if st.session_state.boardroom_discussion_id:
                    st.session_state.waiting_for_response = True
                    st.rerun()
        
        if st.button("🧹 Clear History", key="clear_boardroom"):
            st.session_state.messages = []
            st.session_state.message_count = 0
            st.session_state.boardroom_active = False
            st.session_state.boardroom_discussion_id = None
            render_success_message("Boardroom history cleared")
            st.rerun()
        
        st.markdown("---")
        
        # Export options
        export_format = render_export_options()
        if export_format:
            render_success_message(f"Discussion exported as {export_format}")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        if st.button("🏠 Home", key="nav_home"):
            st.switch_page("Home.py")
        
        if st.button("💬 AI Chat", key="nav_chat"):
            st.switch_page("pages/01_💬_AI_Chat.py")
        
        if st.button("📁 Files", key="nav_files"):
            st.switch_page("pages/03_📁_Files.py")
        
        if st.button("🎨 Images", key="nav_images"):
            st.switch_page("pages/04_🎨_Images.py")
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if not st.session_state.boardroom_active:
            # Discussion setup
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">🎯 Start a New Boardroom Discussion</h3>
                    <p class="card-subtitle">Present your topic to the AI executive team</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Topic input
            topic = st.text_area(
                "Discussion Topic",
                placeholder="Enter a business question or decision that needs multiple perspectives...",
                height=100,
                key="boardroom_topic",
                help="Frame as a question for better discussions. Example: 'Should we expand internationally this year?'"
            )
            
            st.session_state.current_topic = topic
            
            # Example topics
            st.markdown("""
            <div class="card" style="margin-top: 1rem;">
                <div class="card-header">
                    <h4 class="card-title">💡 Example Topics</h4>
                </div>
                <div style="margin: 1rem 0;">
                    <ul>
                        <li><strong>Strategic Planning:</strong> "Should we launch our product in Europe next quarter?"</li>
                        <li><strong>Technology Decisions:</strong> "Should we migrate to microservices architecture?"</li>
                        <li><strong>Marketing Strategy:</strong> "How should we allocate our Q4 marketing budget?"</li>
                        <li><strong>Financial Planning:</strong> "Should we seek Series A funding now or wait?"</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Selected personas preview
            if st.session_state.selected_personas:
                st.markdown("""
                <div class="card" style="margin-top: 1rem;">
                    <div class="card-header">
                        <h4 class="card-title">👥 Selected Personas</h4>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                for persona in st.session_state.selected_personas:
                    st.markdown(f"""
                    <div class="persona-message" style="margin: 0.5rem 0;">
                        <div class="persona-badge">{persona['role']}</div>
                        <strong>{persona['name']}</strong><br>
                        <small>{persona['expertise']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Start discussion button
            if topic.strip() and len(st.session_state.selected_personas) >= 2:
                if st.button("🚀 Start Boardroom Discussion", key="start_boardroom", type="primary"):
                    with st.spinner("Starting boardroom discussion..."):
                        discussion_id, error = asyncio.run(start_boardroom_discussion(
                            topic, 
                            st.session_state.selected_personas
                        ))
                        
                        if error:
                            render_error_message(error)
                        else:
                            st.session_state.boardroom_discussion_id = discussion_id
                            st.session_state.boardroom_active = True
                            
                            # Add initial message
                            add_message_to_session(
                                content=f"📋 **Discussion Topic:** {topic}",
                                is_user=True
                            )
                            
                            render_success_message("Boardroom discussion started!")
                            st.rerun()
            
            elif not topic.strip():
                render_info_message("Please enter a discussion topic to begin")
            
            elif len(st.session_state.selected_personas) < 2:
                render_info_message("Please select at least 2 personas for a discussion")
        
        else:
            # Active discussion
            st.markdown(f"""
            <div class="alert alert-success">
                <strong>🏢 Active Discussion:</strong> {st.session_state.current_topic}
            </div>
            """, unsafe_allow_html=True)
            
            # Show chat messages
            render_chat_container(
                messages=st.session_state.messages,
                show_typing=st.session_state.get('waiting_for_response', False),
                typing_persona="AI Executive"
            )
    
    with col2:
        # Discussion statistics
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 Discussion Stats</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        render_chat_stats(
            message_count=st.session_state.get('message_count', 0),
            model_count=len(st.session_state.selected_personas),
            session_time=get_session_duration()
        )
        
        # Active personas
        if st.session_state.selected_personas:
            st.markdown("""
            <div class="card" style="margin-top: 1rem;">
                <div class="card-header">
                    <h4 class="card-title">👥 Active Personas</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            for persona in st.session_state.selected_personas:
                st.markdown(f"""
                <div style="margin: 0.5rem 0; padding: 0.5rem; background: {persona['color']}20; border-left: 3px solid {persona['color']}; border-radius: 8px;">
                    <strong>{persona['name']}</strong><br>
                    <small>{persona['role']} • {persona['model']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Discussion phases
        if st.session_state.boardroom_active:
            st.markdown("""
            <div class="card" style="margin-top: 1rem;">
                <div class="card-header">
                    <h4 class="card-title">📈 Discussion Phase</h4>
                </div>
                <div style="margin: 1rem 0;">
                    <div class="badge badge-primary">Opening</div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #718096;">
                        Initial perspectives and analysis
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Handle waiting for response
    if st.session_state.get('waiting_for_response') and st.session_state.boardroom_discussion_id:
        with st.spinner("Getting next response from boardroom..."):
            try:
                response, error = asyncio.run(get_next_boardroom_response(
                    st.session_state.boardroom_discussion_id
                ))
                
                if error:
                    render_error_message(error)
                else:
                    # Add AI response
                    add_message_to_session(
                        content=response.get('content', 'No response'),
                        is_user=False,
                        persona=response.get('persona', 'AI Executive'),
                        model=response.get('model')
                    )
                
                st.session_state.waiting_for_response = False
                st.rerun()
                
            except Exception as e:
                render_error_message(f"Error getting response: {str(e)}")
                st.session_state.waiting_for_response = False

if __name__ == "__main__":
    main()