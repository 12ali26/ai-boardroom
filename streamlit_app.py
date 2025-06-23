#!/usr/bin/env python3
"""
AI Boardroom - Professional Streamlit Application Entry Point

This is the main entry point for the professional AI Boardroom application.
Run with: streamlit run streamlit_app.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import and run the new professional home page
    from Home import main as home_main
    
    if __name__ == "__main__":
        home_main()
    else:
        # When imported by Streamlit
        home_main()
        
except ImportError as e:
    # Fallback to legacy UI if new interface fails
    try:
        from backend.app.ui import main as legacy_main
        legacy_main()
    except Exception as legacy_e:
        import streamlit as st
        st.error(f"""
        🚨 **Application Error**: Could not load interface
        
        **Primary Error**: {str(e)}
        **Fallback Error**: {str(legacy_e)}
        
        **Troubleshooting:**
        1. Install dependencies: `pip install -r requirements.txt`
        2. Run health check: `python -m backend.app.main --mode health`
        3. Check your .env file configuration
        
        **For support:** Verify all files exist and API keys are configured
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