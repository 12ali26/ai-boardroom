"""
File Processing Page - Document Upload and Analysis
Professional interface for file processing capabilities
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.chat_interface import (
    load_chat_styles,
    render_conversation_header,
    render_info_message,
    render_success_message,
    render_error_message
)
from components.theme_manager import apply_theme
from components.file_processor import file_processor
from components.error_handler import ErrorHandler

def main():
    """Main file processing page"""
    
    # Set page config
    st.set_page_config(
        page_title="📁 File Processing - AI Boardroom",
        page_icon="📁",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load styles and apply theme
    load_chat_styles()
    apply_theme()
    
    # Initialize file processor
    file_processor.initialize_session_state()
    
    # Render header
    render_conversation_header(
        "File Processing",
        "Upload and analyze documents for AI discussions",
        mode="files"
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-title">📁 File Manager</div>
        <div class="sidebar-subtitle">Document Processing</div>
        """, unsafe_allow_html=True)
        
        # File upload section
        st.markdown("### 📤 Upload Files")
        
        # Quick upload buttons
        if st.button("📄 Upload Documents", key="upload_docs"):
            st.session_state.show_uploader = True
        
        if st.button("📊 Upload Data Files", key="upload_data"):
            st.session_state.show_uploader = True
        
        st.markdown("---")
        
        # File management
        st.markdown("### 📋 File Management")
        
        uploaded_count = len(st.session_state.get('uploaded_files', {}))
        context_count = len(st.session_state.get('file_context', {}))
        
        st.markdown(f"""
        <div class="alert alert-info">
            📁 {uploaded_count} files uploaded<br>
            📎 {context_count} files in context
        </div>
        """, unsafe_allow_html=True)
        
        if uploaded_count > 0:
            if st.button("🗑️ Clear All Files", key="clear_all"):
                st.session_state.uploaded_files = {}
                st.session_state.processed_files = {}
                st.session_state.file_context = {}
                render_success_message("All files cleared!")
                st.rerun()
        
        st.markdown("---")
        
        # File processing stats
        st.markdown("### 📊 Processing Stats")
        
        if uploaded_count > 0:
            total_size = sum(file_info['size'] for file_info in st.session_state.uploaded_files.values())
            st.markdown(f"""
            <div style="font-size: 0.9rem;">
                • Total files: {uploaded_count}<br>
                • Total size: {total_size:,} bytes<br>
                • In context: {context_count} files
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("No files processed yet")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        if st.button("🏠 Home", key="nav_home"):
            st.switch_page("Home.py")
        
        if st.button("💬 AI Chat", key="nav_chat"):
            st.switch_page("pages/01_AI_Chat.py")
        
        if st.button("🏢 Boardroom", key="nav_boardroom"):
            st.switch_page("pages/02_Boardroom.py")
        
        if st.button("🎨 Images", key="nav_images"):
            st.switch_page("pages/04_Images.py")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload section
        if st.session_state.get('show_uploader', True):
            st.markdown("### 📤 Upload Files")
            
            # File uploader
            try:
                uploaded_files = file_processor.render_file_uploader(
                    key="main_file_uploader",
                    accept_multiple=True
                )
                
                if uploaded_files:
                    st.success(f"✅ {len(uploaded_files)} file(s) processed successfully!")
                    
                    # Show quick actions for uploaded files
                    st.markdown("#### 🚀 Quick Actions")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if st.button("💬 Discuss in Chat", key="quick_chat"):
                            # Add all files to context
                            for file_info in uploaded_files:
                                file_processor.add_file_to_context(file_info['id'])
                            st.switch_page("pages/01_AI_Chat.py")
                    
                    with col_b:
                        if st.button("🏢 Boardroom Analysis", key="quick_boardroom"):
                            # Add all files to context
                            for file_info in uploaded_files:
                                file_processor.add_file_to_context(file_info['id'])
                            st.switch_page("pages/02_Boardroom.py")
                    
                    with col_c:
                        if st.button("📋 View Details", key="quick_details"):
                            st.session_state.show_file_details = True
                            st.rerun()
                
            except Exception as e:
                ErrorHandler.log_error(e, {'context': 'file_upload'})
                render_error_message("File upload failed. Please try again.")
        
        # File management section
        st.markdown("---")
        st.markdown("### 📋 File Management")
        
        # Show uploaded files
        file_processor.render_uploaded_files()
        
        # File context status
        file_processor.render_file_context_status()
    
    with col2:
        # File processing capabilities
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">🔧 Processing Capabilities</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin: 1rem 0;">
            <h4>📄 Document Types</h4>
            <ul style="font-size: 0.9rem;">
                <li><strong>Text:</strong> TXT, MD, HTML</li>
                <li><strong>Documents:</strong> PDF, DOCX, RTF</li>
                <li><strong>Data:</strong> CSV, JSON, XLSX</li>
            </ul>
            
            <h4>🤖 AI Analysis</h4>
            <ul style="font-size: 0.9rem;">
                <li>Content summarization</li>
                <li>Q&A on documents</li>
                <li>Multi-persona analysis</li>
                <li>Executive insights</li>
            </ul>
            
            <h4>⚙️ Features</h4>
            <ul style="font-size: 0.9rem;">
                <li>Real-time processing</li>
                <li>Context integration</li>
                <li>Conversation export</li>
                <li>Multi-file analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Processing tips
        st.markdown("""
        <div class="card" style="margin-top: 1rem;">
            <div class="card-header">
                <h4 class="card-title">💡 Processing Tips</h4>
            </div>
            <div style="margin: 1rem 0; font-size: 0.9rem;">
                <strong>For best results:</strong><br>
                • Upload clean, text-based documents<br>
                • Use descriptive filenames<br>
                • Keep files under 10MB<br>
                • Add files to context before discussion<br>
                • Use specific questions about content
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # File processing examples
        st.markdown("""
        <div class="card" style="margin-top: 1rem;">
            <div class="card-header">
                <h4 class="card-title">🎯 Example Use Cases</h4>
            </div>
            <div style="margin: 1rem 0; font-size: 0.9rem;">
                <strong>Business Documents:</strong><br>
                • Financial reports analysis<br>
                • Contract review<br>
                • Market research synthesis<br><br>
                
                <strong>Technical Documents:</strong><br>
                • Code documentation review<br>
                • Requirements analysis<br>
                • Architecture discussions<br><br>
                
                <strong>Research Papers:</strong><br>
                • Academic paper analysis<br>
                • Literature review<br>
                • Data interpretation
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()