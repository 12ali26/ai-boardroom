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
    get_session_duration,
    render_modern_chat_messages,
    render_modern_chat_input
)
from components.theme_manager import apply_theme
from components.session_manager import session_manager
from components.ai_integration import (
    initialize_ai_session,
    get_boardroom_response,
    save_message_to_history,
    get_conversation_history,
    get_conversation_summary,
    export_conversation,
    get_api_status
)

def get_available_personas():
    """Get list of available AI personas from backend"""
    try:
        from backend.app.personas import PersonaManager
        
        persona_manager = PersonaManager()
        backend_personas = persona_manager.get_all_personas()
        
        # Convert to format expected by frontend with colors
        persona_colors = {
            "CEO": "#e53e3e",
            "CTO": "#38a169", 
            "CMO": "#dd6b20",
            "CFO": "#3182ce"
        }
        
        frontend_personas = []
        for persona in backend_personas:
            frontend_personas.append({
                "name": persona.name,
                "role": persona.role,
                "model": persona.model,
                "personality": persona.personality,
                "expertise": persona.expertise,
                "color": persona_colors.get(persona.role, "#718096")
            })
        
        return frontend_personas
        
    except Exception as e:
        st.error(f"Error loading personas: {str(e)}")
        return []

async def start_boardroom_discussion(topic: str, selected_personas):
    """Start a new boardroom discussion"""
    try:
        # Create new conversation ID for boardroom
        conversation_id = session_manager.get_or_create_conversation_id()
        
        # Save initial topic message
        topic_message = {
            'content': f"📋 **Discussion Topic:** {topic}",
            'is_user': True,
            'timestamp': datetime.now().isoformat()
        }
        save_message_to_history(conversation_id, topic_message)
        
        return conversation_id, None
        
    except Exception as e:
        return None, f"Error starting discussion: {str(e)}"

def main():
    """Main boardroom page"""
    
    # Set page config - Modern style like Chat
    st.set_page_config(
        page_title="🏢 AI Boardroom - AI Boardroom",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="collapsed"  # Start collapsed like modern chat
    )
    
    # Load styles
    load_chat_styles()
    
    # Apply theme
    apply_theme()
    
    # Initialize session
    session_manager.initialize_global_session()
    initialize_chat_session()
    initialize_ai_session()
    
    # Minimal header like ChatGPT
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #e9ecef;">
        <h3 style="margin: 0; color: #374151;">🏢 AI Boardroom</h3>
        <p style="margin: 0.25rem 0 0 0; color: #6b7280; font-size: 0.9rem;">Executive AI Discussion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simplified sidebar like modern chat
    with st.sidebar:
        # Simple title
        st.markdown("### 🏢 AI Boardroom")
        
        # Persona selection - simplified
        st.markdown("**👥 Executive Team**")
        available_personas = get_available_personas()
        
        # Show simplified persona selection
        for persona in available_personas:
            selected = st.checkbox(
                f"{persona['role']} - {persona['name']}",
                value=True,
                key=f"persona_{persona['role'].lower()}",
                help=f"{persona['expertise']}"
            )
            
            # Update selected personas list
            if selected and persona not in st.session_state.selected_personas:
                st.session_state.selected_personas.append(persona)
            elif not selected and persona in st.session_state.selected_personas:
                st.session_state.selected_personas.remove(persona)
        
        st.markdown("---")
        
        # Essential controls only
        if not st.session_state.boardroom_active:
            if st.button("+ New Discussion", key="new_discussion", use_container_width=True):
                session_manager.reset_boardroom()
                st.rerun()
        else:
            if st.button("⏭️ Next Response", key="next_response", use_container_width=True):
                if st.session_state.boardroom_discussion_id:
                    st.session_state.waiting_for_response = True
                    st.rerun()
            
            if st.button("⏹️ End Discussion", key="end_discussion", use_container_width=True):
                session_manager.reset_boardroom()
                st.rerun()
        
        # Simple navigation
        st.markdown("**Navigate**")
        
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.switch_page("Home.py")
        
        if st.button("💬 AI Chat", key="nav_chat", use_container_width=True):
            st.switch_page("pages/01_AI_Chat.py")
        
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
        
        # Persona participation stats
        if st.session_state.selected_personas and st.session_state.boardroom_discussion_id:
            st.markdown("""
            <div class="card" style="margin-top: 1rem;">
                <div class="card-header">
                    <h4 class="card-title">👥 Persona Participation</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Get conversation history for stats
            from components.ai_integration import get_conversation_history
            history = get_conversation_history(st.session_state.boardroom_discussion_id)
            
            # Count responses per persona
            persona_stats = {}
            for msg in history:
                if not msg.get('is_user', False) and msg.get('persona'):
                    persona_name = msg.get('persona')
                    persona_stats[persona_name] = persona_stats.get(persona_name, 0) + 1
            
            # Show participation for each selected persona
            for persona in st.session_state.selected_personas:
                response_count = persona_stats.get(persona['name'], 0)
                st.markdown(f"""
                <div style="margin: 0.5rem 0; padding: 0.5rem; background: {persona['color']}15; border-left: 3px solid {persona['color']}; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{persona['name']}</strong><br>
                            <small>{persona['role']} • {persona['model']}</small>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: bold; color: {persona['color']}; font-size: 1.2rem;">{response_count}</div>
                            <div style="font-size: 0.8rem; color: #718096;">responses</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        elif st.session_state.selected_personas:
            st.markdown("""
            <div class="card" style="margin-top: 1rem;">
                <div class="card-header">
                    <h4 class="card-title">👥 Selected Personas</h4>
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
        if st.session_state.boardroom_active and st.session_state.boardroom_discussion_id:
            # Determine discussion phase based on message count
            from components.ai_integration import get_conversation_history
            history = get_conversation_history(st.session_state.boardroom_discussion_id)
            ai_responses = [msg for msg in history if not msg.get('is_user', False)]
            response_count = len(ai_responses)
            
            # Define phases
            if response_count <= 3:
                phase = "Opening"
                phase_desc = "Initial perspectives and analysis"
                phase_color = "#3182ce"
            elif response_count <= 8:
                phase = "Discussion"
                phase_desc = "Active debate and idea exchange"
                phase_color = "#38a169"
            elif response_count <= 15:
                phase = "Deep Dive"
                phase_desc = "Detailed analysis and considerations"
                phase_color = "#dd6b20"
            else:
                phase = "Synthesis"
                phase_desc = "Building consensus and decisions"
                phase_color = "#e53e3e"
            
            st.markdown(f"""
            <div class="card" style="margin-top: 1rem;">
                <div class="card-header">
                    <h4 class="card-title">📈 Discussion Phase</h4>
                </div>
                <div style="margin: 1rem 0;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <div style="width: 12px; height: 12px; background: {phase_color}; border-radius: 50%; margin-right: 0.5rem;"></div>
                        <div style="font-weight: bold; color: {phase_color}; font-size: 1.1rem;">{phase}</div>
                        <div style="margin-left: auto; font-size: 0.8rem; color: #718096;">{response_count} responses</div>
                    </div>
                    <div style="font-size: 0.9rem; color: #718096;">
                        {phase_desc}
                    </div>
                    
                    <!-- Progress bar -->
                    <div style="background: #e2e8f0; height: 4px; border-radius: 2px; margin-top: 0.5rem; overflow: hidden;">
                        <div style="background: {phase_color}; height: 100%; width: {min(100, (response_count / 20) * 100)}%; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Handle waiting for response
    if st.session_state.get('waiting_for_response') and st.session_state.boardroom_discussion_id:
        with st.spinner("Getting next response from boardroom..."):
            try:
                response, error = asyncio.run(get_boardroom_response(
                    st.session_state.current_topic,
                    st.session_state.boardroom_discussion_id,
                    st.session_state.selected_personas
                ))
                
                if error:
                    render_error_message(error)
                    
                    # Save error to history
                    error_message = {
                        'content': f"❌ {error}",
                        'is_user': False,
                        'persona': 'System',
                        'timestamp': datetime.now().isoformat()
                    }
                    save_message_to_history(st.session_state.boardroom_discussion_id, error_message)
                    
                else:
                    # Add AI response
                    add_message_to_session(
                        content=response.get('content', 'No response'),
                        is_user=False,
                        persona=response.get('persona', 'AI Executive'),
                        model=response.get('model')
                    )
                    
                    # Save response to history
                    ai_message = {
                        'content': response.get('content', 'No response'),
                        'is_user': False,
                        'persona': response.get('persona', 'AI Executive'),
                        'model': response.get('model'),
                        'timestamp': datetime.now().isoformat()
                    }
                    save_message_to_history(st.session_state.boardroom_discussion_id, ai_message)
                
                st.session_state.waiting_for_response = False
                st.rerun()
                
            except Exception as e:
                error_msg = f"Error getting response: {str(e)}"
                render_error_message(error_msg)
                
                # Save error to history
                error_message = {
                    'content': f"❌ {error_msg}",
                    'is_user': False,
                    'persona': 'System',
                    'timestamp': datetime.now().isoformat()
                }
                save_message_to_history(st.session_state.boardroom_discussion_id, error_message)
                
                st.session_state.waiting_for_response = False

if __name__ == "__main__":
    main()