"""
AI Integration Component
Handles real AI model interactions and responses
"""

import streamlit as st
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from components.error_handler import ErrorHandler, handle_async_errors, validate_input, safe_api_call

def initialize_ai_session():
    """Initialize AI session state"""
    if 'ai_models' not in st.session_state:
        st.session_state.ai_models = get_available_models()
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = {}
    
    if 'current_conversation_id' not in st.session_state:
        st.session_state.current_conversation_id = None
    
    if 'api_status' not in st.session_state:
        st.session_state.api_status = "disconnected"

def get_available_models() -> List[Dict]:
    """Get list of available AI models with metadata"""
    return [
        {
            "id": "openai/gpt-4",
            "name": "GPT-4",
            "provider": "OpenAI",
            "description": "Most capable OpenAI model for complex tasks",
            "context_length": 8192,
            "cost": "High",
            "speed": "Medium"
        },
        {
            "id": "openai/gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "provider": "OpenAI", 
            "description": "Faster GPT-4 variant with updated training",
            "context_length": 128000,
            "cost": "Medium",
            "speed": "Fast"
        },
        {
            "id": "openai/gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "provider": "OpenAI",
            "description": "Fast and efficient for most tasks",
            "context_length": 16384,
            "cost": "Low",
            "speed": "Very Fast"
        },
        {
            "id": "anthropic/claude-3-sonnet",
            "name": "Claude-3 Sonnet",
            "provider": "Anthropic",
            "description": "Balanced performance and speed",
            "context_length": 200000,
            "cost": "Medium",
            "speed": "Fast"
        },
        {
            "id": "anthropic/claude-3-haiku",
            "name": "Claude-3 Haiku", 
            "provider": "Anthropic",
            "description": "Fastest Claude model",
            "context_length": 200000,
            "cost": "Low",
            "speed": "Very Fast"
        },
        {
            "id": "google/gemini-pro",
            "name": "Gemini Pro",
            "provider": "Google",
            "description": "Google's most capable model",
            "context_length": 32768,
            "cost": "Medium",
            "speed": "Fast"
        },
        {
            "id": "google/gemini-flash",
            "name": "Gemini Flash",
            "provider": "Google",
            "description": "Fastest Gemini model",
            "context_length": 32768,
            "cost": "Low",
            "speed": "Very Fast"
        }
    ]

@handle_async_errors("AI Response")
async def get_ai_response(message: str, model_id: str, conversation_id: Optional[str] = None) -> Tuple[str, str]:
    """
    Get AI response using the backend OpenRouter integration
    Returns: (response_text, error_message)
    """
    # Validate inputs
    if not validate_input(message, "Message"):
        return "", "Invalid message input"
    
    if not validate_input(model_id, "Model ID"):
        return "", "Invalid model ID"
    
    try:
        # Import backend components
        from backend.app.openrouter import OpenRouterClient
        from backend.app.validators import InputValidator
        
        # Update connection status
        st.session_state.api_status = "connecting"
        
        # Validate input using backend validator
        is_valid, cleaned_message, warnings = InputValidator.validate_topic(message)
        if not is_valid:
            error_msg = f"Input validation failed: {warnings[0] if warnings else 'Invalid input'}"
            st.session_state.api_status = "error"
            ErrorHandler.display_warning("Invalid input", error_msg)
            return "", error_msg
        
        # Initialize OpenRouter client
        client = OpenRouterClient()
        
        # Check if we have conversation history
        conversation_history = []
        if conversation_id and conversation_id in st.session_state.conversation_history:
            # Get last few messages for context
            history = st.session_state.conversation_history[conversation_id]
            conversation_history = history[-10:]  # Last 10 messages for context
        
        # Create message payload
        messages = []
        
        # Add file context if available
        file_context = get_file_context()
        if file_context:
            messages.append({
                "role": "system",
                "content": f"""You have access to the following uploaded documents for reference:

{file_context}

When answering, you can reference these documents directly. If the user asks about content in these files, provide specific, detailed answers based on the actual content."""
            })
        
        # Add conversation history
        for msg in conversation_history:
            role = "user" if msg.get('is_user', False) else "assistant"
            messages.append({
                "role": role,
                "content": msg.get('content', '')
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": cleaned_message
        })
        
        # Update connection status
        st.session_state.api_status = "connected"
        
        # Make API call
        response = await client.generate_response(
            model_id=model_id,
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        if response and response.get('error'):
            st.session_state.api_status = "error"
            error_msg = response['error']
            ErrorHandler.display_error(Exception(error_msg), "AI Response")
            return "", error_msg
        
        response_text = response.get('content', 'No response received') if response else ""
        st.session_state.api_status = "connected"
        
        return response_text, ""
        
    except Exception as e:
        st.session_state.api_status = "error"
        ErrorHandler.log_error(e, {
            'model_id': model_id,
            'conversation_id': conversation_id,
            'message_length': len(message)
        })
        return "", f"Error getting AI response: {str(e)}"

async def get_boardroom_response(topic: str, conversation_id: str, selected_personas: List = None) -> Tuple[Dict, str]:
    """
    Get next response in boardroom discussion with persona rotation
    Returns: (response_dict, error_message)
    """
    try:
        from backend.app.openrouter import OpenRouterClient
        from backend.app.validators import InputValidator
        from backend.app.personas import PersonaManager
        
        # Update connection status
        st.session_state.api_status = "connecting"
        
        # Validate topic
        is_valid, cleaned_topic, warnings = InputValidator.validate_topic(topic)
        if not is_valid:
            st.session_state.api_status = "error"
            return {}, f"Topic validation failed: {warnings[0] if warnings else 'Invalid topic'}"
        
        # Get personas
        persona_manager = PersonaManager()
        available_personas = persona_manager.get_all_personas()
        
        # Use selected personas or default to all
        if selected_personas:
            active_personas = [p for p in available_personas if any(sp.get('role') == p.role for sp in selected_personas)]
        else:
            active_personas = available_personas
        
        if not active_personas:
            st.session_state.api_status = "error"
            return {}, "No active personas selected"
        
        # Get conversation history to determine next persona
        history = get_conversation_history(conversation_id)
        
        # Determine which persona should respond next
        persona_responses = {}
        for msg in history:
            if not msg.get('is_user', False) and msg.get('persona'):
                persona_name = msg.get('persona')
                persona_responses[persona_name] = persona_responses.get(persona_name, 0) + 1
        
        # Find persona with least responses (round-robin style)
        next_persona = min(active_personas, key=lambda p: persona_responses.get(p.name, 0))
        
        # Create OpenRouter client
        client = OpenRouterClient()
        
        # Build conversation context for this persona
        messages = []
        
        # Add file context if available
        file_context = get_file_context()
        file_context_note = ""
        if file_context:
            file_context_note = f"""

You also have access to the following uploaded documents for reference:
{file_context}

Reference these documents in your analysis when relevant."""
        
        # Add persona system prompt
        system_prompt = f"""You are {next_persona.name}, {next_persona.role} of the company.

Your personality: {next_persona.personality}

Your expertise: {next_persona.expertise}

You are participating in a boardroom discussion about: "{cleaned_topic}"{file_context_note}

Instructions:
1. Respond as {next_persona.name} would, staying true to your role and personality
2. Provide insights based on your expertise area
3. Keep responses concise but substantive (2-4 sentences)
4. Reference specific business considerations relevant to your role
5. Engage with other executives' points when appropriate
6. Use a professional but conversational tone
7. If relevant documents are available, reference them in your analysis

Remember: You are {next_persona.role}, so focus on {next_persona.role.lower()}-related aspects of the discussion."""
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add conversation history (last 10 messages for context)
        recent_history = history[-10:] if len(history) > 10 else history
        for msg in recent_history:
            if msg.get('is_user', False):
                messages.append({
                    "role": "user",
                    "content": f"Discussion Topic: {msg.get('content', '')}"
                })
            else:
                persona_name = msg.get('persona', 'Executive')
                content = msg.get('content', '')
                messages.append({
                    "role": "assistant",
                    "content": f"{persona_name}: {content}"
                })
        
        # If no recent history, add the topic as user message
        if not recent_history or recent_history[0].get('is_user', False):
            messages.append({
                "role": "user",
                "content": f"Let's discuss: {cleaned_topic}"
            })
        
        # Update connection status
        st.session_state.api_status = "connected"
        
        # Get AI response
        response = await client.generate_response(
            model_id=next_persona.model,
            messages=messages,
            max_tokens=1000,
            temperature=0.8  # Higher creativity for persona responses
        )
        
        if response.get('error'):
            st.session_state.api_status = "error"
            return {}, response['error']
        
        response_content = response.get('content', 'No response received')
        
        # Format response
        response_dict = {
            'content': response_content,
            'persona': next_persona.name,
            'role': next_persona.role,
            'model': next_persona.model,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.api_status = "connected"
        return response_dict, ""
        
    except Exception as e:
        st.session_state.api_status = "error"
        error_msg = f"Error getting boardroom response: {str(e)}"
        return {}, error_msg

def create_conversation_id() -> str:
    """Create a unique conversation ID"""
    timestamp = int(time.time() * 1000)
    return f"conv_{timestamp}"

def save_message_to_history(conversation_id: str, message: Dict):
    """Save message to conversation history"""
    if conversation_id not in st.session_state.conversation_history:
        st.session_state.conversation_history[conversation_id] = []
    
    # Add timestamp if not present
    if 'timestamp' not in message:
        message['timestamp'] = datetime.now().isoformat()
    
    st.session_state.conversation_history[conversation_id].append(message)
    
    # Limit conversation history to last 100 messages
    if len(st.session_state.conversation_history[conversation_id]) > 100:
        st.session_state.conversation_history[conversation_id] = \
            st.session_state.conversation_history[conversation_id][-100:]

def get_conversation_history(conversation_id: str) -> List[Dict]:
    """Get conversation history for a given conversation ID"""
    return st.session_state.conversation_history.get(conversation_id, [])

def get_conversation_summary(conversation_id: str) -> Dict:
    """Get summary information about a conversation"""
    history = get_conversation_history(conversation_id)
    
    if not history:
        return {
            "message_count": 0,
            "duration": "0m",
            "last_activity": None,
            "models_used": [],
            "personas_active": []
        }
    
    # Count messages
    user_messages = len([msg for msg in history if msg.get('is_user', False)])
    ai_messages = len([msg for msg in history if not msg.get('is_user', False)])
    
    # Get models used
    models_used = list(set([msg.get('model', '') for msg in history if msg.get('model')]))
    
    # Get personas active (for boardroom)
    personas_active = list(set([msg.get('persona', '') for msg in history if msg.get('persona')]))
    
    # Calculate duration
    first_message = history[0]
    last_message = history[-1]
    
    try:
        first_time = datetime.fromisoformat(first_message.get('timestamp', ''))
        last_time = datetime.fromisoformat(last_message.get('timestamp', ''))
        duration_minutes = int((last_time - first_time).total_seconds() / 60)
        duration = f"{duration_minutes}m" if duration_minutes < 60 else f"{duration_minutes//60}h {duration_minutes%60}m"
    except:
        duration = "Unknown"
    
    return {
        "message_count": len(history),
        "user_messages": user_messages,
        "ai_messages": ai_messages,
        "duration": duration,
        "last_activity": last_message.get('timestamp'),
        "models_used": [m for m in models_used if m],
        "personas_active": [p for p in personas_active if p]
    }

def clear_conversation_history(conversation_id: str):
    """Clear history for a specific conversation"""
    if conversation_id in st.session_state.conversation_history:
        del st.session_state.conversation_history[conversation_id]

def export_conversation(conversation_id: str, format: str = "markdown") -> str:
    """Export conversation to specified format"""
    history = get_conversation_history(conversation_id)
    
    if not history:
        return "No conversation history to export."
    
    if format == "markdown":
        lines = ["# AI Conversation Export", "", f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
        
        for msg in history:
            timestamp = msg.get('timestamp', '')
            if msg.get('is_user', False):
                lines.append(f"## 👤 User ({timestamp})")
                lines.append(f"{msg.get('content', '')}")
            else:
                persona = msg.get('persona', 'AI')
                model = msg.get('model', '')
                model_info = f" ({model})" if model else ""
                lines.append(f"## 🤖 {persona}{model_info} ({timestamp})")
                lines.append(f"{msg.get('content', '')}")
            lines.append("")
        
        return "\n".join(lines)
    
    elif format == "json":
        import json
        export_data = {
            "conversation_id": conversation_id,
            "exported_at": datetime.now().isoformat(),
            "summary": get_conversation_summary(conversation_id),
            "messages": history
        }
        return json.dumps(export_data, indent=2)
    
    else:
        # Plain text format
        lines = [f"AI Conversation Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
        
        for msg in history:
            timestamp = msg.get('timestamp', '')
            if msg.get('is_user', False):
                lines.append(f"USER ({timestamp}): {msg.get('content', '')}")
            else:
                persona = msg.get('persona', 'AI')
                lines.append(f"{persona} ({timestamp}): {msg.get('content', '')}")
            lines.append("")
        
        return "\n".join(lines)

def get_model_info(model_id: str) -> Dict:
    """Get detailed information about a specific model"""
    models = get_available_models()
    for model in models:
        if model['id'] == model_id:
            return model
    
    # Return default info if model not found
    return {
        "id": model_id,
        "name": model_id.split('/')[-1] if '/' in model_id else model_id,
        "provider": "Unknown",
        "description": "AI model",
        "context_length": 4096,
        "cost": "Unknown",
        "speed": "Unknown"
    }

def estimate_token_count(text: str) -> int:
    """Rough estimate of token count"""
    # Very rough approximation: ~4 characters per token
    return len(text) // 4

def check_context_limit(conversation_id: str, model_id: str) -> Tuple[bool, int, int]:
    """
    Check if conversation is approaching context limit
    Returns: (within_limit, current_tokens, max_tokens)
    """
    model_info = get_model_info(model_id)
    max_tokens = model_info.get('context_length', 4096)
    
    history = get_conversation_history(conversation_id)
    current_tokens = 0
    
    for msg in history:
        current_tokens += estimate_token_count(msg.get('content', ''))
    
    # Reserve 1000 tokens for response
    within_limit = current_tokens < (max_tokens - 1000)
    
    return within_limit, current_tokens, max_tokens

def get_api_status() -> str:
    """Get current API connection status"""
    return st.session_state.get('api_status', 'disconnected')

def set_api_status(status: str):
    """Set API connection status"""
    st.session_state.api_status = status

def get_file_context() -> str:
    """Get file context for AI discussions"""
    if 'file_context' not in st.session_state or not st.session_state.file_context:
        return ""
    
    context_parts = []
    for file_id, file_data in st.session_state.file_context.items():
        context_parts.append(f"""
File: {file_data['name']}
Content:
{file_data['content'][:2000]}{'...' if len(file_data['content']) > 2000 else ''}
---
""")
    
    return "\n".join(context_parts)