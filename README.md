# 🏢 AI Boardroom

An enterprise-grade AI-powered boardroom debate system that enables structured discussions and decision-making using artificial intelligence agents representing different executive perspectives and stakeholders.

## ✨ Features

### 🎭 **AI Executive Personas**
- **Alexandra Stone (CEO)** - Strategic visionary powered by GPT-4
- **Marcus Chen (CTO)** - Technical innovator using Claude-3-Sonnet  
- **Sofia Rodriguez (CMO)** - Creative strategist with Gemini-Pro

### 🎯 **Intelligent Discussion Management**
- **Smart Turn Selection** - AI chooses speakers based on expertise relevance
- **Structured Phases** - Opening (2 turns) → Debate (4 turns) → Synthesis (2 turns)
- **Context-Aware Responses** - Each persona builds on previous discussions
- **Real-time Validation** - Input sanitization and business context checking

### 🛡️ **Enterprise-Grade Error Handling**
- **API Fallback System** - Automatic model fallbacks (GPT-4 → GPT-4-turbo → GPT-3.5)
- **Retry Logic** - Exponential backoff with jitter for failed requests
- **Rate Limiting** - Built-in API protection and quota management
- **Graceful Degradation** - Continues operation even with component failures

### 📊 **Comprehensive Analytics**
- **Discussion Statistics** - Participation tracking and word counts
- **Export Functionality** - Download complete transcripts
- **Summary Generation** - AI-powered discussion summaries
- **Health Monitoring** - Real-time system status and error tracking

### 💾 **Persistent Storage**
- **SQLite Database** - Automatic discussion and message persistence
- **Memory Fallback** - Seamless operation if database unavailable
- **Data Recovery** - Load previous discussions from storage

### 📱 **Modern Web Interface**
- **Streamlit UI** - Responsive and intuitive interface
- **Real-time Updates** - Live discussion progress tracking
- **Error Feedback** - User-friendly error messages with solutions
- **Input Validation** - Real-time topic validation and suggestions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenRouter API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-boardroom
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenRouter API key
   ```

4. **Run health check**
   ```bash
   python -m backend.app.main --mode health
   ```

5. **Start the application**
   ```bash
   streamlit run streamlit_app.py
   # Or use the convenience runner:
   python run.py app
   ```

## 📖 Usage

### Starting a Discussion
1. Enter a business topic (e.g., "Should we hire more developers?")
2. Click "Start New Discussion"
3. Use "Next Response" to advance the conversation
4. Export or save discussions when complete

### Best Practices
- **Frame as questions** for better debates
- **Include business context** (revenue, strategy, timeline)
- **Use specific scenarios** rather than abstract concepts
- **Review suggestions** for topic improvements

## 🏗️ Architecture

### Core Components

```
ai-boardroom/
├── backend/app/
│   ├── config.py          # Pydantic configuration
│   ├── openrouter.py      # API client with fallbacks
│   ├── personas.py        # Executive persona definitions
│   ├── debate.py          # Discussion orchestration
│   ├── database.py        # SQLite persistence layer
│   ├── formatter.py       # Message formatting & export
│   ├── validators.py      # Input validation & security
│   ├── logger.py          # Centralized logging system
│   ├── ui.py             # Streamlit interface
│   └── main.py           # Application entry point
├── logs/                  # Application logs
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

### System Flow
1. **Input Validation** → Topic sanitization and business context checking
2. **Discussion Creation** → Initialize personas and phase management
3. **AI Orchestration** → Smart speaker selection based on expertise
4. **Response Generation** → Context-aware AI responses with fallbacks
5. **Persistence** → Automatic saving to database with memory backup
6. **Formatting & Export** → Professional output and transcript generation

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Optional
DATABASE_URL=sqlite:///./ai_boardroom.db  # Database connection
DEBUG=true                                # Debug mode
```

### Supported Models
- **OpenAI**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic**: Claude-3-Sonnet, Claude-3-Haiku
- **Google**: Gemini-Pro

## 🛠️ Development

### Running Tests
```bash
# System health check
python run.py health
# OR: python -m backend.app.main --mode health

# Run all tests  
python run.py test
# OR: python -m backend.app.main --mode test

# Test individual components
python -m backend.app.validators
python -m backend.app.config
```

### Debug Mode
```bash
# Enable detailed logging
python -m backend.app.main --log-level DEBUG
```

### Development Features
- **Comprehensive Logging** - File and console output with rotation
- **Error Tracking** - Detailed error context and recovery suggestions
- **Performance Monitoring** - API response times and usage tracking
- **Input Sanitization** - XSS and injection prevention

## 📊 Monitoring

### Health Monitoring
The system provides real-time health monitoring for:
- ✅ Configuration validation
- ✅ Database connectivity  
- ✅ OpenRouter API access
- ✅ Persona loading

### Logging
- **Daily log rotation** in `/logs/` directory
- **Structured logging** with timestamps and context
- **Error classification** and recovery suggestions
- **Performance metrics** and API usage tracking

## 🔒 Security

### Input Protection
- Content filtering for malicious patterns
- XSS and injection prevention
- Input length limits and sanitization
- Business context validation

### API Security
- Rate limiting to prevent quota exhaustion
- API key validation and secure storage
- Fallback model hierarchy for resilience
- Request timeout protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `python -m backend.app.main --mode test`
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and support:
1. Check the health status: `python -m backend.app.main --mode health`
2. Review logs in `/logs/ai_boardroom_*.log`
3. Verify API key configuration
4. Report issues with full error context

## 📈 Roadmap

- [ ] Multi-language support
- [ ] Custom persona creation
- [ ] Advanced analytics dashboard
- [ ] Integration with business tools
- [ ] Voice interface support
- [ ] Advanced AI model support