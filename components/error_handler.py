"""
Error Handler Component
Comprehensive error handling and user feedback system
"""

import streamlit as st
import traceback
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps

# Set up logging
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for AI Boardroom"""
    
    @staticmethod
    def log_error(error: Exception, context: Dict[str, Any] = None):
        """Log error with context information"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        logger.error(f"Error occurred: {error_info}")
        
        # Store in session state for debugging
        if 'error_history' not in st.session_state:
            st.session_state.error_history = []
        
        st.session_state.error_history.append(error_info)
        
        # Keep only last 50 errors
        if len(st.session_state.error_history) > 50:
            st.session_state.error_history = st.session_state.error_history[-50:]
    
    @staticmethod
    def display_error(error: Exception, context: str = "Operation"):
        """Display user-friendly error message"""
        error_type = type(error).__name__
        
        # Map common errors to user-friendly messages
        error_messages = {
            'ConnectionError': "Unable to connect to AI services. Please check your internet connection.",
            'TimeoutError': "Request timed out. Please try again.",
            'ValueError': "Invalid input provided. Please check your data and try again.",
            'KeyError': "Missing required information. Please ensure all fields are filled.",
            'ImportError': "Required component not available. Please contact support.",
            'FileNotFoundError': "Required file not found. Please check your configuration.",
            'PermissionError': "Permission denied. Please check your access rights.",
            'APIError': "AI service is temporarily unavailable. Please try again later.",
            'ValidationError': "Input validation failed. Please check your input and try again."
        }
        
        user_message = error_messages.get(error_type, f"{context} failed. Please try again.")
        
        st.error(f"❌ **{context} Error**\n\n{user_message}")
        
        # Show technical details in expander for debugging
        with st.expander("🔧 Technical Details (for debugging)"):
            st.code(f"""
Error Type: {error_type}
Error Message: {str(error)}
Context: {context}
Timestamp: {datetime.now().isoformat()}
            """)
    
    @staticmethod
    def display_warning(message: str, details: str = None):
        """Display warning message"""
        st.warning(f"⚠️ **Warning**\n\n{message}")
        
        if details:
            with st.expander("More Details"):
                st.info(details)
    
    @staticmethod
    def display_success(message: str):
        """Display success message"""
        st.success(f"✅ {message}")
    
    @staticmethod
    def display_info(message: str):
        """Display info message"""
        st.info(f"ℹ️ {message}")

def handle_errors(context: str = "Operation"):
    """Decorator for automatic error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(e, {
                    'function': func.__name__,
                    'args': str(args)[:100],  # Truncate for safety
                    'kwargs': str(kwargs)[:100]
                })
                ErrorHandler.display_error(e, context)
                return None
        return wrapper
    return decorator

def handle_async_errors(context: str = "Operation"):
    """Decorator for automatic async error handling"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(e, {
                    'function': func.__name__,
                    'args': str(args)[:100],  # Truncate for safety
                    'kwargs': str(kwargs)[:100]
                })
                ErrorHandler.display_error(e, context)
                return None
        return wrapper
    return decorator

def validate_input(data: Any, field_name: str, required: bool = True) -> bool:
    """Validate input data"""
    try:
        if required and (data is None or data == ""):
            ErrorHandler.display_warning(f"{field_name} is required")
            return False
        
        if isinstance(data, str) and len(data.strip()) == 0 and required:
            ErrorHandler.display_warning(f"{field_name} cannot be empty")
            return False
        
        return True
        
    except Exception as e:
        ErrorHandler.log_error(e, {'field_name': field_name, 'data_type': type(data).__name__})
        return False

def check_api_status() -> bool:
    """Check if API services are available"""
    try:
        api_status = st.session_state.get('api_status', 'disconnected')
        
        if api_status == 'error':
            ErrorHandler.display_warning(
                "AI services are currently experiencing issues",
                "Please wait a moment and try again. If the problem persists, check your API configuration."
            )
            return False
        
        if api_status == 'disconnected':
            ErrorHandler.display_info("Connecting to AI services...")
            return False
        
        return True
        
    except Exception as e:
        ErrorHandler.log_error(e, {'context': 'api_status_check'})
        return False

def check_conversation_limits(conversation_id: str, max_messages: int = 100) -> bool:
    """Check conversation limits"""
    try:
        from components.ai_integration import get_conversation_history
        
        history = get_conversation_history(conversation_id)
        
        if len(history) >= max_messages:
            ErrorHandler.display_warning(
                f"Conversation has reached the maximum of {max_messages} messages",
                "Consider starting a new conversation or exporting the current one."
            )
            return False
        
        return True
        
    except Exception as e:
        ErrorHandler.log_error(e, {'conversation_id': conversation_id})
        return False

def safe_api_call(func, *args, context: str = "API Call", **kwargs):
    """Safely execute API calls with error handling"""
    try:
        if not check_api_status():
            return None, "API services unavailable"
        
        result = func(*args, **kwargs)
        return result, None
        
    except ConnectionError as e:
        error_msg = "Connection to AI services failed. Please check your internet connection."
        ErrorHandler.log_error(e, {'context': context})
        return None, error_msg
        
    except TimeoutError as e:
        error_msg = "Request timed out. Please try again."
        ErrorHandler.log_error(e, {'context': context})
        return None, error_msg
        
    except Exception as e:
        error_msg = f"{context} failed: {str(e)}"
        ErrorHandler.log_error(e, {'context': context})
        return None, error_msg

def get_error_summary() -> Dict[str, int]:
    """Get summary of recent errors"""
    if 'error_history' not in st.session_state:
        return {}
    
    error_counts = {}
    for error in st.session_state.error_history:
        error_type = error.get('error_type', 'Unknown')
        error_counts[error_type] = error_counts.get(error_type, 0) + 1
    
    return error_counts

def clear_error_history():
    """Clear error history"""
    if 'error_history' in st.session_state:
        st.session_state.error_history = []

def render_error_dashboard():
    """Render error dashboard for debugging"""
    st.markdown("### 🔧 Error Dashboard")
    
    error_summary = get_error_summary()
    
    if not error_summary:
        st.success("No recent errors! 🎉")
        return
    
    # Show error summary
    st.markdown("#### Recent Error Summary")
    for error_type, count in error_summary.items():
        st.markdown(f"- **{error_type}**: {count} occurrences")
    
    # Show recent errors
    if st.button("Show Recent Errors"):
        st.markdown("#### Recent Error Details")
        
        if 'error_history' in st.session_state:
            for i, error in enumerate(reversed(st.session_state.error_history[-10:])):
                with st.expander(f"Error {i+1}: {error.get('error_type', 'Unknown')}"):
                    st.json(error)
    
    # Clear errors button
    if st.button("Clear Error History"):
        clear_error_history()
        st.success("Error history cleared!")
        st.rerun()