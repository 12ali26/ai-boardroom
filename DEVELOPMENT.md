# AI Boardroom Development Guide

## Overview

This project uses Streamlit as the web interface for the AI Boardroom application, providing an intuitive and interactive user experience.

## Architecture

- **UI**: Streamlit web interface (`backend/app/ui.py`)
- **Backend**: Python application with modular components
- **Database**: SQLite with memory fallback
- **AI**: OpenRouter integration with multiple LLM providers

## Development Setup

### Prerequisites

- Python 3.8+
- OpenRouter API key

### Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenRouter API key
   ```

3. **Run health check**:
   ```bash
   python -m backend.app.main --mode health
   ```

## Running the Application

### Streamlit Web Interface

```bash
streamlit run streamlit_app.py
# Or: python run.py app
```

The application will be available at http://localhost:8501

## Application Features

- **AI Executive Personas** - CEO, CTO, CMO with distinct personalities
- **Structured Discussions** - Opening, Debate, and Synthesis phases
- **Real-time AI Responses** - Interactive conversation flow
- **Discussion Management** - Save, load, and export discussions
- **Health Monitoring** - System status and error tracking
- **Export Functionality** - Download discussion transcripts

## Project Structure

```
ai-boardroom/
├── backend/app/
│   ├── ui.py              # Streamlit web interface
│   ├── main.py            # Application entry point
│   ├── debate.py          # Discussion management
│   ├── personas.py        # AI persona definitions
│   ├── openrouter.py      # OpenRouter API client
│   ├── database.py        # SQLite persistence
│   ├── formatter.py       # Message formatting
│   ├── validators.py      # Input validation
│   └── logger.py          # Logging system
├── logs/                  # Application logs
├── streamlit_app.py       # Streamlit entry point
├── run.py                 # Convenience runner
└── requirements.txt       # Python dependencies
```

## Testing

### System Tests
```bash
python -m backend.app.main --mode test
```

### Health Checks
```bash
python -m backend.app.main --mode health
```

## Troubleshooting

1. **Application won't start**: Check OpenRouter API key configuration
2. **Database issues**: Application falls back to memory storage if SQLite fails
3. **AI responses failing**: Check API key and run health check
4. **Logging issues**: Check `/logs/` directory for error details