"""
File Processing Component
Handles file uploads, processing, and integration with AI discussions
"""

import streamlit as st
import os
import tempfile
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import mimetypes
from pathlib import Path

# Import error handling
from components.error_handler import ErrorHandler, handle_errors, validate_input

class FileProcessor:
    """Handles file upload and processing for AI Boardroom"""
    
    # Supported file types
    SUPPORTED_TYPES = {
        'text/plain': ['txt'],
        'text/markdown': ['md'],
        'application/pdf': ['pdf'],
        'text/csv': ['csv'],
        'application/json': ['json'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx'],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['xlsx'],
        'text/html': ['html', 'htm'],
        'application/rtf': ['rtf']
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize file processing session state"""
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = {}
        
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = {}
        
        if 'file_processing_status' not in st.session_state:
            st.session_state.file_processing_status = {}
    
    @handle_errors("File Upload")
    def render_file_uploader(self, key: str = "file_uploader", accept_multiple: bool = True) -> List[Any]:
        """Render file uploader component"""
        
        # Get supported extensions
        all_extensions = []
        for extensions in self.SUPPORTED_TYPES.values():
            all_extensions.extend(extensions)
        
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <h4 class="card-title">📁 Upload Files</h4>
                <p class="card-subtitle">Upload documents for AI analysis and discussion</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files",
            type=all_extensions,
            accept_multiple_files=accept_multiple,
            key=key,
            help=f"Supported formats: {', '.join(all_extensions)}. Max size: {self.MAX_FILE_SIZE // (1024*1024)}MB per file."
        )
        
        if uploaded_files:
            if not isinstance(uploaded_files, list):
                uploaded_files = [uploaded_files]
            
            # Process each uploaded file
            processed_files = []
            for uploaded_file in uploaded_files:
                try:
                    if self._validate_file(uploaded_file):
                        file_info = self._process_uploaded_file(uploaded_file)
                        if file_info:
                            processed_files.append(file_info)
                            st.success(f"✅ {uploaded_file.name} processed successfully")
                        else:
                            st.error(f"❌ Failed to process {uploaded_file.name}")
                    else:
                        st.error(f"❌ {uploaded_file.name} is not valid")
                except Exception as e:
                    ErrorHandler.log_error(e, {'filename': uploaded_file.name})
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            
            return processed_files
        
        # Show supported file types
        st.markdown("""
        <div class="alert alert-info">
            <strong>💡 Supported File Types:</strong><br>
            • Text files (TXT, MD, HTML)<br>
            • Documents (PDF, DOCX, RTF)<br>
            • Data files (CSV, JSON, XLSX)<br>
            • Maximum size: 10MB per file
        </div>
        """, unsafe_allow_html=True)
        
        return []
    
    def _validate_file(self, uploaded_file) -> bool:
        """Validate uploaded file"""
        try:
            # Check file size
            if uploaded_file.size > self.MAX_FILE_SIZE:
                ErrorHandler.display_warning(
                    f"File '{uploaded_file.name}' is too large",
                    f"Maximum allowed size is {self.MAX_FILE_SIZE // (1024*1024)}MB. Your file is {uploaded_file.size // (1024*1024)}MB."
                )
                return False
            
            # Check file type
            file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
            
            supported_extensions = []
            for extensions in self.SUPPORTED_TYPES.values():
                supported_extensions.extend(extensions)
            
            if file_extension not in supported_extensions:
                ErrorHandler.display_warning(
                    f"File type '{file_extension}' not supported",
                    f"Supported types: {', '.join(supported_extensions)}"
                )
                return False
            
            return True
            
        except Exception as e:
            ErrorHandler.log_error(e, {'filename': uploaded_file.name})
            return False
    
    def _process_uploaded_file(self, uploaded_file) -> Optional[Dict]:
        """Process uploaded file and extract content"""
        try:
            # Generate file hash for deduplication
            file_content = uploaded_file.read()
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Check if file already processed
            if file_hash in st.session_state.processed_files:
                return st.session_state.processed_files[file_hash]
            
            # Extract content based on file type
            file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
            
            extracted_content = self._extract_content(uploaded_file, file_extension)
            
            if not extracted_content:
                return None
            
            # Create file info
            file_info = {
                'id': file_hash,
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'type': file_extension,
                'content': extracted_content,
                'processed_at': datetime.now().isoformat(),
                'summary': self._generate_summary(extracted_content[:1000])  # First 1000 chars for summary
            }
            
            # Store in session state
            st.session_state.uploaded_files[file_hash] = file_info
            st.session_state.processed_files[file_hash] = file_info
            
            return file_info
            
        except Exception as e:
            ErrorHandler.log_error(e, {'filename': uploaded_file.name})
            return None
    
    def _extract_content(self, uploaded_file, file_extension: str) -> Optional[str]:
        """Extract text content from uploaded file"""
        try:
            if file_extension in ['txt', 'md', 'html', 'htm', 'rtf']:
                # Text-based files
                return uploaded_file.read().decode('utf-8', errors='ignore')
            
            elif file_extension == 'csv':
                # CSV files
                import pandas as pd
                df = pd.read_csv(uploaded_file)
                return f"CSV Data Summary:\nColumns: {', '.join(df.columns)}\nRows: {len(df)}\n\nFirst 5 rows:\n{df.head().to_string()}"
            
            elif file_extension == 'json':
                # JSON files
                import json
                data = json.load(uploaded_file)
                return f"JSON Data:\n{json.dumps(data, indent=2, ensure_ascii=False)[:2000]}..."
            
            elif file_extension == 'pdf':
                # PDF files (basic extraction)
                try:
                    import PyPDF2
                    from io import BytesIO
                    
                    pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
                    text = ""
                    for page in pdf_reader.pages[:10]:  # Limit to first 10 pages
                        text += page.extract_text() + "\n"
                    return text
                except ImportError:
                    return "PDF processing requires PyPDF2. Content extraction not available."
                except Exception:
                    return "Could not extract text from PDF file."
            
            elif file_extension in ['docx']:
                # Word documents
                try:
                    from docx import Document
                    from io import BytesIO
                    
                    doc = Document(BytesIO(uploaded_file.read()))
                    text = ""
                    for paragraph in doc.paragraphs[:100]:  # Limit to first 100 paragraphs
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    return "DOCX processing requires python-docx. Content extraction not available."
                except Exception:
                    return "Could not extract text from Word document."
            
            elif file_extension == 'xlsx':
                # Excel files
                try:
                    import pandas as pd
                    df = pd.read_excel(uploaded_file, sheet_name=0)  # First sheet only
                    return f"Excel Data Summary:\nColumns: {', '.join(df.columns)}\nRows: {len(df)}\n\nFirst 5 rows:\n{df.head().to_string()}"
                except ImportError:
                    return "Excel processing requires pandas and openpyxl. Content extraction not available."
                except Exception:
                    return "Could not extract data from Excel file."
            
            else:
                return f"File type '{file_extension}' content extraction not implemented."
                
        except Exception as e:
            ErrorHandler.log_error(e, {'file_extension': file_extension})
            return None
    
    def _generate_summary(self, content: str) -> str:
        """Generate a brief summary of file content"""
        if not content:
            return "Empty file"
        
        lines = content.split('\n')
        word_count = len(content.split())
        
        summary = f"Content preview: {word_count} words, {len(lines)} lines"
        
        if len(content) > 200:
            preview = content[:200] + "..."
        else:
            preview = content
        
        return f"{summary}\n\nPreview: {preview}"
    
    def render_uploaded_files(self) -> None:
        """Render list of uploaded files"""
        if not st.session_state.uploaded_files:
            st.info("📁 No files uploaded yet")
            return
        
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <h4 class="card-title">📋 Uploaded Files</h4>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        for file_id, file_info in st.session_state.uploaded_files.items():
            with st.expander(f"📄 {file_info['name']} ({file_info['type'].upper()})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Size:** {file_info['size']:,} bytes")
                    st.markdown(f"**Processed:** {file_info['processed_at']}")
                    st.markdown(f"**Summary:** {file_info['summary']}")
                
                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_{file_id}"):
                        self.remove_file(file_id)
                        st.rerun()
                    
                    if st.button(f"💬 Discuss", key=f"discuss_{file_id}"):
                        self.add_file_to_context(file_id)
                        st.success("File added to discussion context!")
                
                # Show content preview
                if st.checkbox(f"Show content preview", key=f"preview_{file_id}"):
                    content = file_info['content']
                    if len(content) > 1000:
                        st.text_area("Content Preview", content[:1000] + "\n... (truncated)", height=200, key=f"content_{file_id}")
                    else:
                        st.text_area("Content Preview", content, height=200, key=f"content_{file_id}")
    
    def remove_file(self, file_id: str) -> None:
        """Remove uploaded file"""
        if file_id in st.session_state.uploaded_files:
            del st.session_state.uploaded_files[file_id]
        
        if file_id in st.session_state.processed_files:
            del st.session_state.processed_files[file_id]
    
    def add_file_to_context(self, file_id: str) -> bool:
        """Add file content to discussion context"""
        try:
            if file_id not in st.session_state.uploaded_files:
                return False
            
            file_info = st.session_state.uploaded_files[file_id]
            
            # Initialize file context if not exists
            if 'file_context' not in st.session_state:
                st.session_state.file_context = {}
            
            st.session_state.file_context[file_id] = {
                'name': file_info['name'],
                'content': file_info['content'],
                'added_at': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            ErrorHandler.log_error(e, {'file_id': file_id})
            return False
    
    def get_file_context(self) -> str:
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
    
    def clear_file_context(self) -> None:
        """Clear file context"""
        if 'file_context' in st.session_state:
            st.session_state.file_context = {}
    
    def render_file_context_status(self) -> None:
        """Render current file context status"""
        if 'file_context' not in st.session_state or not st.session_state.file_context:
            return
        
        file_count = len(st.session_state.file_context)
        st.markdown(f"""
        <div class="alert alert-info">
            📎 {file_count} file{'s' if file_count != 1 else ''} added to discussion context
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear file context"):
            self.clear_file_context()
            st.success("File context cleared!")
            st.rerun()

# Global file processor instance
file_processor = FileProcessor()