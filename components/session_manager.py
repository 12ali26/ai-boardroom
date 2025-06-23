"""
Session State Manager
Centralized session state management for AI Boardroom
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional
from components.ai_integration import create_conversation_id

class SessionManager:
    """Centralized session state management"""
    
    @staticmethod
    def initialize_global_session():
        """Initialize global session state variables"""
        
        # Core conversation management
        if 'current_conversation_id' not in st.session_state:
            st.session_state.current_conversation_id = None
        
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = {}
        
        # Chat interface state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'message_count' not in st.session_state:
            st.session_state.message_count = 0
        
        if 'models_used' not in st.session_state:
            st.session_state.models_used = set()
        
        if 'is_typing' not in st.session_state:
            st.session_state.is_typing = False
        
        # File processing state
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = {}
        
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = {}
        
        if 'file_context' not in st.session_state:
            st.session_state.file_context = {}
        
        # AI integration state
        if 'api_status' not in st.session_state:
            st.session_state.api_status = "disconnected"
        
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = 'openai/gpt-4'
        
        # Boardroom specific state
        if 'boardroom_discussion_id' not in st.session_state:
            st.session_state.boardroom_discussion_id = None
        
        if 'boardroom_active' not in st.session_state:
            st.session_state.boardroom_active = False
        
        if 'current_topic' not in st.session_state:
            st.session_state.current_topic = ""
        
        if 'selected_personas' not in st.session_state:
            st.session_state.selected_personas = []
        
        if 'waiting_for_response' not in st.session_state:
            st.session_state.waiting_for_response = False
        
        # Theme and UI state
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
        
        # Session tracking
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = datetime.now()
        
        # Error tracking
        if 'error_history' not in st.session_state:
            st.session_state.error_history = []
    
    @staticmethod
    def get_or_create_conversation_id() -> str:
        """Get existing conversation ID or create new one"""
        if not st.session_state.current_conversation_id:
            st.session_state.current_conversation_id = create_conversation_id()
        return st.session_state.current_conversation_id
    
    @staticmethod
    def reset_conversation():
        """Reset current conversation state"""
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.session_state.current_conversation_id = create_conversation_id()
        st.session_state.is_typing = False
    
    @staticmethod
    def reset_boardroom():
        """Reset boardroom discussion state"""
        st.session_state.boardroom_discussion_id = None
        st.session_state.boardroom_active = False
        st.session_state.current_topic = ""
        st.session_state.waiting_for_response = False
        st.session_state.messages = []
        st.session_state.message_count = 0
    
    @staticmethod
    def clear_file_context():
        """Clear file context"""
        st.session_state.file_context = {}
    
    @staticmethod
    def clear_all_files():
        """Clear all uploaded files and context"""
        st.session_state.uploaded_files = {}
        st.session_state.processed_files = {}
        st.session_state.file_context = {}
    
    @staticmethod
    def get_session_stats() -> Dict[str, Any]:
        """Get session statistics"""
        session_duration = datetime.now() - st.session_state.session_start_time
        
        return {
            'session_duration': session_duration,
            'messages_sent': st.session_state.message_count,
            'models_used': len(st.session_state.models_used),
            'files_uploaded': len(st.session_state.uploaded_files),
            'conversations_active': 1 if st.session_state.current_conversation_id else 0,
            'boardroom_active': st.session_state.boardroom_active,
            'api_status': st.session_state.api_status,
            'theme': st.session_state.theme
        }
    
    @staticmethod
    def debug_session_state() -> Dict[str, Any]:
        """Get debug information about session state"""
        debug_info = {}
        
        # Safe keys to include in debug
        safe_keys = [
            'current_conversation_id', 'message_count', 'api_status',
            'selected_model', 'boardroom_active', 'theme', 'is_typing',
            'waiting_for_response'
        ]
        
        for key in safe_keys:
            if key in st.session_state:
                debug_info[key] = st.session_state[key]
        
        # Add counts for complex objects
        debug_info['uploaded_files_count'] = len(st.session_state.get('uploaded_files', {}))
        debug_info['file_context_count'] = len(st.session_state.get('file_context', {}))
        debug_info['conversation_history_count'] = len(st.session_state.get('conversation_history', {}))
        debug_info['selected_personas_count'] = len(st.session_state.get('selected_personas', []))
        
        return debug_info

# Global session manager instance
session_manager = SessionManager()