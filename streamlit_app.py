#!/usr/bin/env python3
"""
AI Boardroom - Streamlit Application Entry Point

This is the main entry point for running the AI Boardroom application with Streamlit.
Run with: streamlit run streamlit_app.py
"""

import sys
import os

# Add the current directory to Python path so we can import from backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import and run the main UI
    from backend.app.ui import main
    
    if __name__ == "__main__":
        main()
    else:
        # When imported by Streamlit
        main()
        
except ImportError as e:
    import streamlit as st
    st.error(f"""
    🚨 **Import Error**: {str(e)}
    
    **Possible solutions:**
    1. Install dependencies: `pip install -r requirements.txt`
    2. Ensure you're in the ai-boardroom directory
    3. Check that all backend files exist
    
    **For support:** Run `python -m backend.app.main --mode health`
    """)
    st.stop()
    
except Exception as e:
    import streamlit as st
    st.error(f"""
    🚨 **Application Error**: {str(e)}
    
    **Troubleshooting:**
    1. Check your .env file configuration
    2. Verify OpenRouter API key is set
    3. Run health check: `python -m backend.app.main --mode health`
    
    **Error Details:**
    ```
    {str(e)}
    ```
    """)
    st.stop()