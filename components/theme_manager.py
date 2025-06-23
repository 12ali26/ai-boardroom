"""
Theme Manager Component
Handles dark/light theme switching and persistence
"""

import streamlit as st
from typing import Literal

ThemeType = Literal["light", "dark", "auto"]

def initialize_theme():
    """Initialize theme system in session state"""
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"
    
    if 'theme_preference' not in st.session_state:
        st.session_state.theme_preference = "auto"

def get_theme_css(theme: ThemeType = None) -> str:
    """Get CSS for the specified theme"""
    
    if theme is None:
        theme = st.session_state.get('theme', 'light')
    
    if theme == "dark":
        return """
        <style>
        /* Dark Theme Variables */
        :root[data-theme="dark"] {
            --primary-color: #7c3aed;
            --primary-dark: #6d28d9;
            --secondary-color: #8b5cf6;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --info-color: #3b82f6;
            
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e0;
            --text-muted: #94a3b8;
            
            --border-color: #334155;
            --border-light: #475569;
            
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 8px 25px rgba(0, 0, 0, 0.5);
        }
        
        /* Apply dark theme */
        html[data-theme="dark"],
        html[data-theme="dark"] body,
        html[data-theme="dark"] .main {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        
        /* Dark theme chat messages */
        html[data-theme="dark"] .user-message {
            background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%) !important;
            color: white !important;
        }
        
        html[data-theme="dark"] .ai-message {
            background: var(--bg-secondary) !important;
            border-color: var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        html[data-theme="dark"] .persona-message {
            background: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
        }
        
        /* Dark theme cards */
        html[data-theme="dark"] .card {
            background: var(--bg-secondary) !important;
            border-color: var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        html[data-theme="dark"] .metric-card {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%) !important;
            border-color: var(--border-color) !important;
        }
        
        /* Dark theme header */
        html[data-theme="dark"] .app-header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
            color: var(--text-primary) !important;
        }
        
        /* Dark theme sidebar */
        html[data-theme="dark"] .sidebar .sidebar-content {
            background: var(--bg-tertiary) !important;
            color: var(--text-primary) !important;
        }
        
        /* Dark theme inputs */
        html[data-theme="dark"] .stTextInput > div > div > input,
        html[data-theme="dark"] .stTextArea > div > div > textarea,
        html[data-theme="dark"] .stSelectbox > div > div > select {
            background: var(--bg-secondary) !important;
            border-color: var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        html[data-theme="dark"] .chat-input-container {
            background: var(--bg-primary) !important;
            border-color: var(--border-color) !important;
        }
        
        /* Dark theme alerts */
        html[data-theme="dark"] .alert-success {
            background: rgba(16, 185, 129, 0.1) !important;
            border-color: var(--success-color) !important;
            color: #34d399 !important;
        }
        
        html[data-theme="dark"] .alert-warning {
            background: rgba(245, 158, 11, 0.1) !important;
            border-color: var(--warning-color) !important;
            color: #fbbf24 !important;
        }
        
        html[data-theme="dark"] .alert-error {
            background: rgba(239, 68, 68, 0.1) !important;
            border-color: var(--error-color) !important;
            color: #f87171 !important;
        }
        
        html[data-theme="dark"] .alert-info {
            background: rgba(59, 130, 246, 0.1) !important;
            border-color: var(--info-color) !important;
            color: #60a5fa !important;
        }
        
        /* Dark theme loading states */
        html[data-theme="dark"] .skeleton-line {
            background: linear-gradient(90deg, #334155 25%, #475569 50%, #334155 75%) !important;
        }
        
        html[data-theme="dark"] .skeleton-card {
            background: var(--bg-secondary) !important;
        }
        
        html[data-theme="dark"] .typing-indicator,
        html[data-theme="dark"] .typing-indicator-enhanced {
            background: var(--bg-secondary) !important;
            color: var(--text-secondary) !important;
        }
        </style>
        """
    else:
        return """
        <style>
        /* Light Theme (Default) */
        html[data-theme="light"],
        html[data-theme="light"] body,
        html[data-theme="light"] .main {
            background-color: #ffffff !important;
            color: #2d3748 !important;
        }
        </style>
        """

def render_theme_toggle(key: str = "theme_toggle") -> ThemeType:
    """Render theme toggle component"""
    
    initialize_theme()
    
    # Theme options
    theme_options = {
        "🌞 Light": "light",
        "🌙 Dark": "dark",
        "🔄 Auto": "auto"
    }
    
    # Get current theme display name
    current_display = next(
        (display for display, value in theme_options.items() 
         if value == st.session_state.theme_preference), 
        "🌞 Light"
    )
    
    # Render toggle
    selected_display = st.selectbox(
        "Theme",
        options=list(theme_options.keys()),
        index=list(theme_options.keys()).index(current_display),
        key=key,
        help="Choose your preferred theme"
    )
    
    # Update theme preference
    new_theme = theme_options[selected_display]
    st.session_state.theme_preference = new_theme
    
    # Set actual theme based on preference
    if new_theme == "auto":
        # For now, default to light. In a real app, you'd detect system preference
        st.session_state.theme = "light"
    else:
        st.session_state.theme = new_theme
    
    return st.session_state.theme

def apply_theme():
    """Apply the current theme to the page"""
    
    initialize_theme()
    
    theme = st.session_state.get('theme', 'light')
    
    # Set HTML data attribute for theme
    st.markdown(f"""
    <script>
    document.documentElement.setAttribute('data-theme', '{theme}');
    </script>
    """, unsafe_allow_html=True)
    
    # Apply theme CSS
    theme_css = get_theme_css(theme)
    st.markdown(theme_css, unsafe_allow_html=True)

def get_theme_colors(theme: ThemeType = None) -> dict:
    """Get color values for the current theme"""
    
    if theme is None:
        theme = st.session_state.get('theme', 'light')
    
    if theme == "dark":
        return {
            "primary": "#7c3aed",
            "secondary": "#8b5cf6",
            "background": "#0f172a",
            "surface": "#1e293b",
            "text": "#f1f5f9",
            "text_secondary": "#cbd5e0",
            "border": "#334155",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "info": "#3b82f6"
        }
    else:
        return {
            "primary": "#667eea",
            "secondary": "#764ba2",
            "background": "#ffffff",
            "surface": "#f8f9fa",
            "text": "#2d3748",
            "text_secondary": "#4a5568",
            "border": "#e9ecef",
            "success": "#38a169",
            "warning": "#dd6b20",
            "error": "#e53e3e",
            "info": "#3182ce"
        }

def render_theme_preview():
    """Render theme preview component"""
    
    colors = get_theme_colors()
    theme = st.session_state.get('theme', 'light')
    
    st.markdown(f"""
    <div class="card" style="margin: 1rem 0;">
        <div class="card-header">
            <h4 class="card-title">🎨 {theme.title()} Theme Preview</h4>
        </div>
        <div style="margin: 1rem 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.5rem;">
                <div style="background: {colors['primary']}; color: white; padding: 0.5rem; border-radius: 8px; text-align: center; font-size: 0.8rem;">
                    Primary
                </div>
                <div style="background: {colors['secondary']}; color: white; padding: 0.5rem; border-radius: 8px; text-align: center; font-size: 0.8rem;">
                    Secondary
                </div>
                <div style="background: {colors['success']}; color: white; padding: 0.5rem; border-radius: 8px; text-align: center; font-size: 0.8rem;">
                    Success
                </div>
                <div style="background: {colors['warning']}; color: white; padding: 0.5rem; border-radius: 8px; text-align: center; font-size: 0.8rem;">
                    Warning
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def save_theme_preference(theme: ThemeType):
    """Save theme preference (placeholder for future persistence)"""
    # In a real app, you might save to local storage or user preferences
    st.session_state.theme_preference = theme
    st.session_state.theme = theme if theme != "auto" else "light"

def load_theme_preference() -> ThemeType:
    """Load saved theme preference (placeholder for future persistence)"""
    # In a real app, you might load from local storage or user preferences
    return st.session_state.get('theme_preference', 'light')

def detect_system_theme() -> ThemeType:
    """Detect system theme preference (placeholder for future implementation)"""
    # This would require JavaScript integration to detect system theme
    # For now, default to light
    return "light"

def render_theme_settings():
    """Render comprehensive theme settings"""
    
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">🎨 Theme Settings</h3>
            <p class="card-subtitle">Customize your visual experience</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Theme selection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        theme = render_theme_toggle("main_theme_toggle")
        
        # Theme description
        theme_descriptions = {
            "light": "🌞 **Light Theme** - Clean and bright interface, perfect for daytime use",
            "dark": "🌙 **Dark Theme** - Easy on the eyes, ideal for low-light environments", 
            "auto": "🔄 **Auto Theme** - Automatically adapts to your system preferences"
        }
        
        current_theme = st.session_state.get('theme_preference', 'light')
        st.markdown(theme_descriptions.get(current_theme, theme_descriptions['light']))
    
    with col2:
        render_theme_preview()
    
    # Apply theme immediately
    apply_theme()
    
    # Additional theme options
    st.markdown("### 🛠️ Advanced Options")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        # High contrast mode (placeholder)
        high_contrast = st.checkbox(
            "High Contrast Mode",
            help="Increase contrast for better accessibility",
            key="high_contrast_mode"
        )
        
        # Reduced motion (placeholder)
        reduced_motion = st.checkbox(
            "Reduce Animations",
            help="Minimize animations for better performance",
            key="reduced_motion"
        )
    
    with col4:
        # Font size adjustment (placeholder)
        font_size = st.selectbox(
            "Font Size",
            options=["Small", "Medium", "Large"],
            index=1,
            help="Adjust text size for better readability",
            key="font_size"
        )
        
        # Compact mode (placeholder)
        compact_mode = st.checkbox(
            "Compact Mode",
            help="Reduce spacing for more content on screen",
            key="compact_mode"
        )
    
    # Save preferences
    if st.button("💾 Save Preferences", key="save_theme_prefs"):
        save_theme_preference(st.session_state.theme_preference)
        st.success("✅ Theme preferences saved!")
    
    return theme