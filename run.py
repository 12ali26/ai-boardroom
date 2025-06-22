#!/usr/bin/env python3
"""
AI Boardroom - Development Runner

A convenience script for running the AI Boardroom application in different modes.
"""

import sys
import subprocess
import argparse


def run_streamlit():
    """Run the Streamlit application."""
    print("🚀 Starting AI Boardroom Streamlit application...")
    print("📝 Access the app at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped")
        return 0


def run_health_check():
    """Run system health check."""
    print("🔍 Running system health check...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "backend.app.main", "--mode", "health"
        ], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Health check failed: {e}")
        return 1


def run_tests():
    """Run system tests."""
    print("🧪 Running system tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "backend.app.main", "--mode", "test"
        ], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="AI Boardroom Development Runner")
    parser.add_argument("command", choices=["app", "health", "test"], 
                       help="Command to run")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.command == "app":
        return run_streamlit()
    elif args.command == "health":
        return run_health_check()
    elif args.command == "test":
        return run_tests()


if __name__ == "__main__":
    sys.exit(main())