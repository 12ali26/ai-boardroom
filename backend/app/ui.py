import streamlit as st
import asyncio
from typing import Optional
from .debate import DiscussionManager
from .personas import PersonaManager
from .formatter import DiscussionFormatter
from .validators import InputValidator
from .logger import get_logger
from datetime import datetime
import traceback

# Initialize logger
logger = get_logger('ui')


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    logger.info("Initializing Streamlit session state")
    
    if 'discussion_manager' not in st.session_state:
        try:
            st.session_state.discussion_manager = DiscussionManager(use_database=True)
            logger.info("DiscussionManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DiscussionManager: {str(e)}")
            st.error(f"⚠️ System initialization error. Using fallback mode.")
            st.session_state.discussion_manager = DiscussionManager(use_database=False)
    
    if 'current_discussion_id' not in st.session_state:
        st.session_state.current_discussion_id = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'discussion_active' not in st.session_state:
        st.session_state.discussion_active = False
    
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = ""
    
    if 'error_count' not in st.session_state:
        st.session_state.error_count = 0
    
    if 'last_error' not in st.session_state:
        st.session_state.last_error = None


def display_persona_info():
    """Display information about the personas."""
    st.sidebar.header("🎭 Boardroom Personas")
    
    persona_manager = PersonaManager()
    personas = persona_manager.get_all_personas()
    
    for persona in personas:
        with st.sidebar.expander(f"{persona.name} - {persona.role}"):
            st.write(f"**Model:** {persona.model}")
            st.write(f"**Personality:** {persona.personality}")
            st.write(f"**Expertise:** {persona.expertise}")


def display_messages():
    """Display the conversation messages with enhanced formatting."""
    if st.session_state.messages:
        col_messages, col_stats = st.columns([3, 1])
        
        with col_messages:
            st.header("💬 Discussion")
            
            # Group messages by phase for better organization
            current_phase = None
            for message in st.session_state.messages:
                msg_phase = message.get('phase', 'unknown')
                
                # Show phase header when phase changes
                if msg_phase != current_phase:
                    current_phase = msg_phase
                    st.subheader(f"📍 {msg_phase.title()} Phase")
                
                # Format and display message
                formatted_msg = DiscussionFormatter.format_message(message)
                
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        # Display persona avatar and info with phase
                        st.markdown(f"**{formatted_msg['persona']}**")
                        st.caption(f"{formatted_msg['role']} • Turn {formatted_msg['turn']}")
                        if formatted_msg.get('timestamp'):
                            st.caption(f"⏰ {formatted_msg['timestamp']}")
                    
                    with col2:
                        # Display message content with better styling
                        with st.expander(f"Turn {formatted_msg['turn']} - {formatted_msg['persona']}", expanded=True):
                            st.markdown(formatted_msg['content'])
                    
                    st.divider()
        
        with col_stats:
            # Discussion statistics
            st.header("📊 Stats")
            stats = DiscussionFormatter.get_discussion_stats(st.session_state.messages)
            
            st.metric("Total Messages", stats['total_messages'])
            st.metric("Total Words", stats['total_words'])
            st.metric("Avg Words/Message", stats['avg_words_per_message'])
            
            # Participation breakdown
            st.subheader("👥 Participation")
            for persona, count in stats['participants'].items():
                st.write(f"• {persona}: {count}")
            
            # Phase breakdown
            st.subheader("🏁 Phases")
            for phase, count in stats['phases'].items():
                st.write(f"• {phase.title()}: {count}")


def show_error_details(error: Exception, context: str = ""):
    """Display detailed error information to users."""
    st.session_state.error_count += 1
    st.session_state.last_error = str(error)
    
    logger.error(f"UI Error in {context}: {str(error)}")
    
    with st.expander(f"❌ Error Details ({context})", expanded=False):
        st.error(f"**Error:** {str(error)}")
        
        # Provide user-friendly suggestions
        if "API" in str(error) or "OpenRouter" in str(error):
            st.info("💡 **Possible solutions:**")
            st.write("• Check your OpenRouter API key configuration")
            st.write("• Verify your internet connection")
            st.write("• The AI service might be temporarily unavailable")
            st.write("• Try again in a few moments")
        elif "database" in str(error).lower():
            st.info("💡 **Database issue detected:**")
            st.write("• The system will continue using memory storage")
            st.write("• Your current discussion won't be permanently saved")
        else:
            st.info("💡 **General troubleshooting:**")
            st.write("• Try refreshing the page")
            st.write("• Check your input for any unusual characters")
            st.write("• Contact support if the issue persists")
        
        if st.session_state.error_count > 3:
            st.warning("⚠️ Multiple errors detected. Consider refreshing the page.")

async def get_next_response():
    """Get the next response from the discussion manager with error handling."""
    if not st.session_state.current_discussion_id:
        st.error("No active discussion found")
        return False
    
    try:
        logger.info(f"Getting next response for discussion {st.session_state.current_discussion_id}")
        
        response = await st.session_state.discussion_manager.get_next_response(
            st.session_state.current_discussion_id
        )
        
        if 'error' not in response:
            st.session_state.messages.append(response)
            logger.info(f"Successfully got response from {response.get('persona', 'unknown')}")
            
            # Show fallback model warning if used
            metadata = response.get('_ai_boardroom_metadata')
            if metadata and metadata.get('used_fallback'):
                st.warning(f"⚠️ Used fallback model {metadata['actual_model']} instead of {metadata['requested_model']}")
            
            return True
        else:
            error_msg = response['error']
            logger.error(f"Error in get_next_response: {error_msg}")
            show_error_details(Exception(error_msg), "Getting AI Response")
            return False
            
    except Exception as e:
        logger.error(f"Exception in get_next_response: {str(e)}")
        show_error_details(e, "Getting AI Response")
        return False


def show_system_status():
    """Display system status and health information."""
    with st.sidebar:
        st.header("🔋 System Status")
        
        # Database status
        db_status = "Connected" if st.session_state.discussion_manager.use_database else "Memory Only"
        db_color = "green" if st.session_state.discussion_manager.use_database else "orange"
        st.markdown(f"**Database:** :{db_color}[{db_status}]")
        
        # Error count
        if st.session_state.error_count > 0:
            st.markdown(f"**Errors:** :red[{st.session_state.error_count}]")
            if st.session_state.last_error:
                st.caption(f"Last: {str(st.session_state.last_error)[:50]}...")
        else:
            st.markdown("**Errors:** :green[None]")
        
        # Session info
        st.markdown(f"**Session:** {datetime.now().strftime('%H:%M:%S')}")
        
        if st.button("🔄 Clear Errors"):
            st.session_state.error_count = 0
            st.session_state.last_error = None
            st.rerun()

def main():
    """Main Streamlit application with comprehensive error handling."""
    try:
        st.set_page_config(
            page_title="AI Boardroom",
            page_icon="🏢",
            layout="wide"
        )
        
        logger.info("Starting AI Boardroom application")
        initialize_session_state()
        
    except Exception as e:
        st.error(f"❌ Critical error during application startup: {str(e)}")
        logger.critical(f"Application startup failed: {str(e)}")
        return
    
    # Main header
    st.title("🏢 AI Boardroom")
    st.markdown("*Where AI executives debate business decisions*")
    
    # Sidebar with persona information and system status
    try:
        display_persona_info()
        show_system_status()
    except Exception as e:
        logger.error(f"Error displaying sidebar: {str(e)}")
        st.sidebar.error("Sidebar display error")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Topic input with validation
        st.header("📋 Discussion Setup")
        
        topic_input = st.text_input(
            "Enter discussion topic:",
            placeholder="e.g., Should we hire more developers?",
            help="Describe the business decision or topic you want the AI executives to discuss",
            max_chars=500
        )
        
        # Real-time topic validation and suggestions
        if topic_input:
            is_valid, cleaned_topic, warnings = InputValidator.validate_topic(topic_input)
            
            if not is_valid:
                st.error(f"❌ {warnings[0] if warnings else 'Invalid topic'}")
                topic = None
            else:
                topic = cleaned_topic
                
                # Show warnings as info
                if warnings:
                    for warning in warnings:
                        st.info(f"💡 {warning}")
                
                # Show suggestions
                suggestions = InputValidator.suggest_topic_improvements(topic)
                if suggestions:
                    with st.expander("💡 Topic Improvement Suggestions", expanded=False):
                        for suggestion in suggestions:
                            st.write(suggestion)
        else:
            topic = None
        
        # Control buttons
        col_start, col_next, col_reset = st.columns(3)
        
        with col_start:
            start_disabled = not topic or not topic.strip()
            
            if st.button("🚀 Start New Discussion", type="primary", disabled=start_disabled):
                if topic and topic.strip():
                    try:
                        logger.info(f"Starting new discussion with topic: {topic}")
                        
                        # Validate one more time before starting
                        is_valid, cleaned_topic, warnings = InputValidator.validate_topic(topic)
                        
                        if not is_valid:
                            st.error(f"❌ Cannot start discussion: {warnings[0] if warnings else 'Invalid topic'}")
                        else:
                            with st.spinner("🎬 Starting discussion..."):
                                discussion_id = st.session_state.discussion_manager.start_discussion(cleaned_topic)
                                st.session_state.current_discussion_id = discussion_id
                                st.session_state.messages = []
                                st.session_state.discussion_active = True
                                st.session_state.current_topic = cleaned_topic
                                st.success(f"✅ Started discussion: {cleaned_topic}")
                                logger.info(f"Discussion started successfully: {discussion_id}")
                                st.rerun()
                                
                    except Exception as e:
                        logger.error(f"Failed to start discussion: {str(e)}")
                        show_error_details(e, "Starting Discussion")
                else:
                    st.error("❌ Please enter a valid discussion topic")
        
        with col_next:
            next_disabled = not st.session_state.discussion_active or not st.session_state.current_discussion_id
            
            if st.button("➡️ Next Response", disabled=next_disabled):
                if st.session_state.current_discussion_id:
                    try:
                        with st.spinner("🤔 AI is thinking..."):
                            # Run async function with timeout
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            try:
                                # Add timeout to prevent hanging
                                success = loop.run_until_complete(
                                    asyncio.wait_for(get_next_response(), timeout=60.0)
                                )
                            except asyncio.TimeoutError:
                                logger.error("Timeout getting AI response")
                                st.error("⏱️ Request timed out. Please try again.")
                                success = False
                            finally:
                                loop.close()
                            
                            if success:
                                st.rerun()
                                
                    except Exception as e:
                        logger.error(f"Error in next response: {str(e)}")
                        show_error_details(e, "Getting Next Response")
                else:
                    st.error("❌ No active discussion found")
        
        with col_reset:
            if st.button("🔄 Reset Discussion"):
                try:
                    logger.info("Resetting discussion")
                    st.session_state.current_discussion_id = None
                    st.session_state.messages = []
                    st.session_state.discussion_active = False
                    st.session_state.current_topic = ""
                    st.session_state.error_count = 0
                    st.session_state.last_error = None
                    st.success("✅ Discussion reset successfully")
                    st.rerun()
                except Exception as e:
                    logger.error(f"Error resetting discussion: {str(e)}")
                    st.error(f"❌ Error resetting discussion: {str(e)}")
    
    with col2:
        # Discussion status
        st.header("📊 Status")
        
        if st.session_state.discussion_active:
            st.success("✅ Discussion Active")
            st.info(f"Messages: {len(st.session_state.messages)}")
            
            if st.session_state.current_discussion_id:
                discussion = st.session_state.discussion_manager.discussions.get(
                    st.session_state.current_discussion_id
                )
                if discussion:
                    current_phase = discussion.get('current_phase')
                    if current_phase:
                        st.info(f"Current Phase: {current_phase.value.title()}")
                    
                    # Show phase progress
                    phase_turns = discussion.get('phase_turns', 0)
                    phase_limits = discussion.get('phase_limits', {})
                    if current_phase and current_phase in phase_limits:
                        progress = phase_turns / phase_limits[current_phase]
                        st.progress(progress, f"Phase Progress: {phase_turns}/{phase_limits[current_phase]}")
        else:
            st.warning("⏸️ No Active Discussion")
        
        # Export and Summary Section
        if st.session_state.messages:
            st.subheader("📄 Export & Summary")
            
            # Generate summary button
            if st.button("📋 Generate Summary"):
                try:
                    with st.spinner("Generating summary..."):
                        summary = DiscussionFormatter.generate_discussion_summary(
                            st.session_state.messages, 
                            st.session_state.current_topic
                        )
                        st.text_area("Discussion Summary", summary, height=200)
                        logger.info("Summary generated successfully")
                except Exception as e:
                    logger.error(f"Error generating summary: {str(e)}")
                    show_error_details(e, "Generating Summary")
            
            # Export to text file
            if st.button("💾 Export Discussion"):
                try:
                    with st.spinner("Preparing export..."):
                        export_text = DiscussionFormatter.export_discussion_to_text(
                            st.session_state.messages,
                            st.session_state.current_topic
                        )
                        
                        # Create download button
                        filename = f"ai_boardroom_discussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        st.download_button(
                            label="📥 Download Export",
                            data=export_text,
                            file_name=filename,
                            mime="text/plain",
                            help="Download the complete discussion transcript"
                        )
                        logger.info(f"Export prepared: {filename}")
                except Exception as e:
                    logger.error(f"Error preparing export: {str(e)}")
                    show_error_details(e, "Preparing Export")
        
        # Quick topic suggestions
        st.subheader("💡 Topic Suggestions")
        suggestions = [
            "Should we hire more developers?",
            "Is it time to expand internationally?",
            "Should we acquire our main competitor?",
            "How should we respond to AI disruption?",
            "Should we pivot to a subscription model?",
            "Is remote work hurting our culture?",
            "Should we invest in blockchain technology?",
            "How do we improve customer retention?"
        ]
        
        for suggestion in suggestions:
            if st.button(f"💭 {suggestion}", key=f"suggest_{suggestion}"):
                # Set the topic in the input field (this would require st.session_state management)
                st.info(f"Click the topic input above and paste: {suggestion}")
    
    # Display messages (only if there are messages)
    try:
        if st.session_state.messages:
            display_messages()
        elif st.session_state.discussion_active:
            st.info("🎬 Discussion started! Click 'Next Response' to begin the conversation.")
        else:
            st.info("👋 Welcome to AI Boardroom! Enter a topic above to start a discussion.")
    except Exception as e:
        logger.error(f"Error displaying messages: {str(e)}")
        show_error_details(e, "Displaying Messages")
    
    # Footer with additional info
    st.markdown("---")
    col_footer1, col_footer2 = st.columns(2)
    
    with col_footer1:
        st.markdown(
            "*Built with Streamlit • Powered by OpenRouter API*\n\n"
            "**Models:** GPT-4, Claude-3-Sonnet, Gemini-Pro"
        )
    
    with col_footer2:
        if st.session_state.current_topic:
            st.markdown(f"**Current Topic:** {st.session_state.current_topic}")
        st.markdown(f"**Session:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application crashed: {str(e)}")
        st.code(traceback.format_exc())
        logger.critical(f"Application crashed: {str(e)}\n{traceback.format_exc()}")
        
        if st.button("🔄 Restart Application"):
            st.rerun()