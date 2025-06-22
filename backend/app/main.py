#!/usr/bin/env python3
"""
AI Boardroom - Main Application Entry Point

This module provides the main entry point for the AI Boardroom application
with comprehensive error handling, logging, and health checks.
"""

import os
import sys
import asyncio
from typing import Optional
from .logger import get_logger, AIBoardroomLogger
from .config import settings

logger = get_logger('main')


async def health_check() -> bool:
    """Perform comprehensive health check of all system components."""
    logger.info("Starting system health check...")
    
    health_status = {
        'config': False,
        'database': False,
        'openrouter': False,
        'personas': False
    }
    
    # Check configuration
    try:
        api_key = getattr(settings, 'openrouter_api_key', None)
        if api_key and len(api_key) > 10:
            health_status['config'] = True
            logger.info("✅ Configuration check passed")
        else:
            logger.warning("⚠️ openrouter_api_key not configured properly")
    except Exception as e:
        logger.error(f"❌ Configuration check failed: {e}")
    
    # Check database
    try:
        from .database import DatabaseManager
        db_manager = DatabaseManager()
        stats = db_manager.get_database_stats()
        health_status['database'] = True
        logger.info(f"✅ Database check passed (DB size: {stats['db_size_mb']} MB)")
    except Exception as e:
        logger.error(f"❌ Database check failed: {e}")
    
    # Check OpenRouter API
    try:
        from .openrouter import OpenRouterClient
        client = OpenRouterClient()
        models = await client.list_models()
        if models and 'data' in models:
            health_status['openrouter'] = True
            logger.info(f"✅ OpenRouter API check passed ({len(models['data'])} models available)")
        else:
            logger.warning("⚠️ OpenRouter API returned unexpected response")
    except Exception as e:
        logger.error(f"❌ OpenRouter API check failed: {e}")
    
    # Check personas
    try:
        from .personas import PersonaManager
        persona_manager = PersonaManager()
        personas = persona_manager.get_all_personas()
        if personas and len(personas) >= 3:
            health_status['personas'] = True
            logger.info(f"✅ Personas check passed ({len(personas)} personas loaded)")
        else:
            logger.warning("⚠️ Insufficient personas loaded")
    except Exception as e:
        logger.error(f"❌ Personas check failed: {e}")
    
    # Overall health
    healthy_components = sum(health_status.values())
    total_components = len(health_status)
    
    logger.info(f"Health check complete: {healthy_components}/{total_components} components healthy")
    
    if healthy_components == total_components:
        logger.info("🎉 All systems operational!")
        return True
    elif healthy_components >= total_components - 1:
        logger.warning("⚠️ System operational with minor issues")
        return True
    else:
        logger.error("❌ System has critical issues")
        return False


def setup_environment():
    """Setup and validate the runtime environment."""
    logger.info("Setting up environment...")
    
    # Create necessary directories
    directories = ['logs', 'data']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        logger.error(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        return False
    
    logger.info(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required environment variables
    required_env_vars = ['OPENROUTER_API_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var) and not hasattr(settings, var.lower()):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        logger.info("The application will work in demo mode with limited functionality")
    
    return True


async def main():
    """Main application entry point."""
    logger.info("🚀 Starting AI Boardroom application...")
    
    # Setup environment
    if not setup_environment():
        logger.error("Environment setup failed")
        return 1
    
    # Perform health check
    if not await health_check():
        logger.warning("Health check failed, but continuing with limited functionality...")
    
    # Import and start Streamlit app
    try:
        logger.info("Launching Streamlit interface...")
        from .ui import main as ui_main
        ui_main()
        return 0
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    
    except Exception as e:
        logger.critical(f"Critical application error: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


def run_streamlit():
    """Run the Streamlit application directly."""
    try:
        # Initialize logging
        AIBoardroomLogger()
        logger.info("🎯 Starting AI Boardroom Streamlit app...")
        
        from .ui import main as ui_main
        ui_main()
        
    except Exception as e:
        print(f"Failed to start Streamlit app: {e}")
        import traceback
        traceback.print_exc()


def run_tests():
    """Run basic system tests."""
    async def test_runner():
        logger.info("🧪 Running system tests...")
        
        # Test health check
        health_ok = await health_check()
        
        # Test discussion creation
        try:
            from .debate import DiscussionManager
            manager = DiscussionManager(use_database=False)  # Use memory for testing
            discussion_id = manager.start_discussion("Test topic for system validation")
            logger.info(f"✅ Discussion creation test passed: {discussion_id}")
        except Exception as e:
            logger.error(f"❌ Discussion creation test failed: {e}")
            health_ok = False
        
        # Test formatters
        try:
            from .formatter import DiscussionFormatter
            test_message = {
                'persona': 'Test Persona',
                'role': 'Test Role',
                'content': 'Test content',
                'turn': 1,
                'phase': 'test'
            }
            formatted = DiscussionFormatter.format_message(test_message)
            logger.info("✅ Formatter test passed")
        except Exception as e:
            logger.error(f"❌ Formatter test failed: {e}")
            health_ok = False
        
        if health_ok:
            logger.info("🎉 All tests passed!")
            return 0
        else:
            logger.error("❌ Some tests failed")
            return 1
    
    return asyncio.run(test_runner())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Boardroom Application")
    parser.add_argument('--mode', choices=['run', 'test', 'health'], default='run',
                       help='Application mode (default: run)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Initialize logging with specified level
    AIBoardroomLogger().setup_logging(log_level=args.log_level)
    
    if args.mode == 'test':
        exit_code = run_tests()
        sys.exit(exit_code)
    elif args.mode == 'health':
        exit_code = asyncio.run(health_check())
        sys.exit(0 if exit_code else 1)
    else:
        # Default run mode
        exit_code = asyncio.run(main())
        sys.exit(exit_code)