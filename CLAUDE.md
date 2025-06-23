# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 🤖 AI Boardroom: Professional Streamlit AI Super-App

## 📋 Executive Summary

AI Boardroom is a **uniquely positioned AI platform** with the world's first working AI Boardroom debate system. While competitors focus on basic chat, you own the premium differentiator that enables collaborative AI decision-making through structured debates between AI personas representing different executive roles.

**Current Status**: Enterprise-grade backend infrastructure with functional Streamlit interface
**Strategic Goal**: Transform into professional-grade AI platform in 6 weeks using advanced Streamlit
**Competitive Advantage**: Only platform offering AI executive advisory board functionality

## 🏗️ Architecture

- **UI**: Professional Streamlit multi-page application
- **Backend**: Python with FastAPI-ready modular components
- **Database**: SQLite with PostgreSQL upgrade path
- **AI Integration**: OpenRouter with 322+ models and smart fallbacks
- **Unique Feature**: Multi-persona debate system (CEO, CTO, CMO, CFO)

## 🚀 Essential Development Commands

### **Application Development**
```bash
pip install -r requirements.txt                    # Install dependencies
streamlit run streamlit_app.py                     # Start Streamlit app
python run.py app                                  # Alternative startup method
python -m backend.app.main --mode health          # Run health checks
python -m backend.app.main --mode test            # Run system tests
python -m backend.app.main --log-level DEBUG      # Debug mode
```

### **Development Workflow**
```bash
# Daily development cycle
python -m backend.app.main --mode health          # Verify system health
streamlit run streamlit_app.py                     # Start development server
# Make changes to pages/ or components/
# Changes auto-reload in browser
```

## 📈 6-Week Implementation Roadmap

### **Phase 1: Professional Interface (Weeks 1-2)**
*Transform existing Streamlit into professional-grade interface*

#### **Week 1: Visual & UX Overhaul**
- **Days 1-2**: WhatsApp-style chat bubbles with custom CSS
- **Days 3-4**: Multi-page architecture with professional navigation  
- **Days 5-7**: Mobile-responsive layouts and theme toggle

#### **Week 2: Advanced Features**
- **Days 1-2**: Enhanced Boardroom interface with persona avatars
- **Days 3-4**: Export functionality and conversation management
- **Days 5-7**: Mobile optimization and error handling

### **Phase 2: Standard AI Features (Weeks 3-4)**
*Add competitive features while maintaining unique advantages*

#### **Week 3: Core AI Functionality**
- **Days 1-2**: Single AI chat mode toggle
- **Days 3-4**: File processing (PDF, images, documents)
- **Days 5-7**: Image generation integration

#### **Week 4: User Management & Billing**
- **Days 1-2**: Email authentication and user profiles
- **Days 3-4**: Subscription tiers and usage tracking
- **Days 5-7**: Stripe integration and billing dashboard

### **Phase 3: Premium Features (Weeks 5-6)**
*Leverage unique advantages for market positioning*

#### **Week 5: Advanced Boardroom**
- **Days 1-2**: Industry-specific personas
- **Days 3-4**: Custom persona creation
- **Days 5-7**: Team collaboration features

#### **Week 6: Launch Preparation**
- **Days 1-2**: Security audit and performance optimization
- **Days 3-4**: User onboarding and documentation
- **Days 5-7**: Final polish and launch preparation

## 🏢 Business Model & Competitive Positioning

### **Subscription Tiers**

#### 🆓 **Starter (Free)**
- 20 messages/day with basic models
- Standard chat mode only
- Limited file uploads (5MB)
- Community support

#### 💼 **Professional ($29/month)**
- Unlimited standard chat
- 20+ premium models
- File processing (100MB)
- Export functionality
- Email support

#### 🏆 **Boardroom ($99/month)**
- Everything in Professional
- **AI Boardroom debates** (unique feature)
- Custom personas
- Advanced analytics
- Team collaboration
- Priority support

#### 🚀 **Enterprise ($299/month)**
- Everything in Boardroom
- White-label options
- Advanced security controls
- Custom integrations
- Dedicated support

### **Competitive Advantage**
- **Unique Value**: Only platform with AI executive advisory board
- **Pricing Power**: 3-5x higher than basic chat platforms ($99 vs $20)
- **Market Position**: Premium business decision-making tool
- **Differentiation**: Collaborative AI vs individual chat

## 🎯 Technical Architecture

### **Professional Streamlit Structure**
```
streamlit_app/
├── 🏠_Home.py                 # Landing page with onboarding
├── pages/
│   ├── 01_💬_AI_Chat.py       # Single AI conversations
│   ├── 02_🏢_Boardroom.py     # Multi-AI debates (UNIQUE)
│   ├── 03_📁_Files.py         # File processing & analysis
│   ├── 04_🎨_Images.py        # Image generation
│   ├── 05_⚙️_Settings.py      # User preferences
│   ├── 06_📊_Usage.py         # Analytics dashboard
│   └── 07_💳_Billing.py       # Subscription management
├── components/
│   ├── chat_interface.py      # Professional chat UI
│   ├── persona_manager.py     # Boardroom interface
│   ├── file_processor.py      # File upload/analysis
│   ├── auth_manager.py        # Authentication
│   └── billing_manager.py     # Subscription logic
├── styles/
│   ├── main.css              # Professional styling
│   ├── chat.css              # Chat-specific styles
│   └── mobile.css            # Responsive design
└── utils/
    ├── session_manager.py     # State management
    ├── api_client.py          # Backend integration
    └── subscription_logic.py  # Tier management
```

### **Backend Components (backend/app/)**
- `ui.py` - Streamlit web interface (legacy, being replaced)
- `debate.py` - Discussion orchestration and phase management
- `personas.py` - AI executive persona definitions (CEO, CTO, CMO, CFO)
- `openrouter.py` - OpenRouter API client with 322+ models
- `database.py` - SQLite persistence with PostgreSQL upgrade path
- `validators.py` - Input validation and security
- `main.py` - Application entry point and health checks
- `formatter.py` - Message formatting and export functionality
- `logger.py` - Comprehensive logging system

## 🎨 Professional Streamlit Features

### **WhatsApp-Style Chat Interface**
```python
# Professional chat styling example
st.markdown("""
<style>
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    font-family: 'Inter', sans-serif;
}
.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 18px;
    border-radius: 20px 20px 5px 20px;
    margin: 8px 0 8px auto;
    max-width: 70%;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.ai-message {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    color: #333;
    padding: 12px 18px;
    border-radius: 20px 20px 20px 5px;
    margin: 8px auto 8px 0;
    max-width: 70%;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)
```

### **Multi-Page Navigation**
```python
# Professional page setup
st.set_page_config(
    page_title="AI Boardroom",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Boardroom")
    st.markdown("*Your AI Advisory Board*")
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Optional
DATABASE_URL=sqlite:///./ai_boardroom.db
DEBUG=true
SUBSCRIPTION_MODE=true
STRIPE_API_KEY=sk_test_your_stripe_key
```

### **Streamlit Configuration**
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#333333"

[server]
maxUploadSize = 200
enableCORS = false
```

## 💡 Key Development Patterns

### **Streamlit-Specific Patterns**
1. **State Management**: Use `st.session_state` for persistent data
2. **Page Navigation**: Multi-page app with shared state
3. **Component Reusability**: Custom functions for repeated UI elements
4. **CSS Integration**: Professional styling with `st.markdown(unsafe_allow_html=True)`
5. **Mobile Responsiveness**: CSS media queries for mobile layouts

### **AI Integration Patterns**
1. **Multi-Model Orchestration**: Smart routing between personas
2. **Conversation Context**: Maintain context across AI interactions
3. **Error Handling**: Graceful fallbacks for API failures
4. **Rate Limiting**: Subscription-based usage controls
5. **Performance**: Async processing for better UX

### **Business Logic Patterns**
1. **Subscription Gating**: Feature access based on user tier
2. **Usage Tracking**: Monitor and limit API consumption
3. **Authentication**: Simple email-based user management
4. **Billing Integration**: Seamless Stripe subscription handling
5. **Analytics**: User behavior and feature adoption tracking

## 📊 Testing and Health Checks

### **System Health Monitoring**
```bash
# Comprehensive health check
python -m backend.app.main --mode health

# Component-specific tests
python -m backend.app.main --mode test

# Debug mode with verbose logging
python -m backend.app.main --log-level DEBUG
```

### **Health Check Components**
- ✅ Configuration validation (API keys, settings)
- ✅ Database connectivity (SQLite/PostgreSQL)
- ✅ OpenRouter API access (322+ models)
- ✅ Persona loading (CEO, CTO, CMO, CFO)
- ✅ Subscription system (Stripe integration)
- ✅ File processing capabilities

### **Performance Monitoring**
- Response time tracking for AI models
- Database query performance
- File upload/processing speed
- User session management
- Subscription tier enforcement

## 🚀 Weekly Task Breakdown

### **Week 1: Visual Transformation**
1. ✅ Create WhatsApp-style chat CSS
2. ✅ Implement professional typography
3. ✅ Set up multi-page architecture
4. ✅ Design professional navigation
5. ✅ Add loading states and animations
6. ✅ Create responsive mobile layouts
7. ✅ Implement theme toggle
8. ✅ Professional form styling

### **Week 2: Advanced Interface**
1. ⏳ Enhance persona displays with avatars
2. ⏳ Create debate flow visualization
3. ⏳ Add @mention functionality UI
4. ⏳ Implement export to PDF/Markdown
5. ⏳ Create conversation search/filter
6. ⏳ Build usage statistics dashboard
7. ⏳ Optimize mobile responsiveness
8. ⏳ Implement comprehensive error handling

### **Week 3: Core Features**
1. ⏳ Create chat/boardroom mode toggle
2. ⏳ Add individual model conversations
3. ⏳ Implement file upload interface
4. ⏳ Add PDF analysis functionality
5. ⏳ Create image upload processing
6. ⏳ Add document Q&A features
7. ⏳ Implement image generation UI
8. ⏳ Create file management system

### **Week 4: User Management**
1. ⏳ Build email authentication system
2. ⏳ Create user profile management
3. ⏳ Implement subscription tier logic
4. ⏳ Add usage tracking system
5. ⏳ Create upgrade prompts
6. ⏳ Integrate Stripe billing
7. ⏳ Build billing dashboard
8. ⏳ Add subscription management

### **Week 5: Premium Features**
1. ⏳ Add industry-specific personas
2. ⏳ Create custom persona builder
3. ⏳ Implement advanced analytics
4. ⏳ Add team collaboration features
5. ⏳ Create enterprise reporting
6. ⏳ Build API access system
7. ⏳ Add integration capabilities
8. ⏳ Implement advanced exports

### **Week 6: Launch Preparation**
1. ⏳ Conduct security audit
2. ⏳ Optimize performance
3. ⏳ Create user onboarding flow
4. ⏳ Build help documentation
5. ⏳ Set up support system
6. ⏳ Final UI/UX polish
7. ⏳ Cross-platform testing
8. ⏳ Launch preparation checklist

## 📚 Documentation and Resources

### **Development Resources**
- Streamlit documentation: https://docs.streamlit.io/
- OpenRouter API docs: https://openrouter.ai/docs
- Custom CSS examples in `/styles/` directory
- Component examples in `/components/` directory

### **Business Resources**
- Subscription tier comparison
- Competitive analysis dashboard
- User feedback collection system
- Analytics and usage reporting

## 🔒 Security and Compliance

### **Security Measures**
- Input validation and sanitization
- API key secure storage
- User authentication and session management
- Subscription tier enforcement
- Rate limiting and abuse prevention

### **Privacy and Data**
- User data encryption
- Conversation privacy controls
- GDPR compliance considerations
- Data retention policies
- Export and deletion capabilities

## 🎯 Success Metrics

### **Technical KPIs**
- **Response Time**: <2 seconds for AI responses
- **Uptime**: 99.9% availability target
- **Error Rate**: <1% of API calls fail
- **Performance**: <5 second page load times

### **Business KPIs**
- **User Conversion**: 4% free to paid conversion
- **Feature Adoption**: 60% use Boardroom within first month
- **Retention**: <5% monthly churn for paid users
- **Revenue**: $50k MRR target by month 12

## 💰 Revenue Projections

| Month | Free Users | Pro ($29) | Boardroom ($99) | Enterprise ($299) | MRR |
|-------|------------|-----------|-----------------|-------------------|-----|
| 1 | 500 | 20 | 5 | 1 | $1,374 |
| 3 | 2,000 | 100 | 25 | 3 | $6,272 |
| 6 | 5,000 | 300 | 75 | 10 | $19,115 |
| 12 | 15,000 | 750 | 200 | 25 | $49,025 |

## 🚀 Go-to-Market Strategy

### **Phase 1: Stealth Launch (Month 1)**
- Target: Early adopters and AI enthusiasts
- Channel: Product Hunt, AI communities
- Goal: 100 users, product-market fit validation

### **Phase 2: Public Launch (Month 2-3)**
- Target: Business professionals, consultants
- Channel: Content marketing, social media
- Goal: 1,000 users, initial revenue traction

### **Phase 3: Enterprise Outreach (Month 4-6)**
- Target: Mid-market companies, consulting firms
- Channel: Direct sales, partnerships
- Goal: 10 enterprise customers, $20k+ MRR

## 🎯 Immediate Next Steps

1. **Start Week 1 tasks** - Begin visual transformation
2. **Set up development environment** - Ensure all dependencies installed
3. **Create task tracking** - Use TodoWrite to manage daily progress
4. **Run health checks** - Verify all systems operational
5. **Begin professional CSS implementation** - Start with chat interface

---

*This document serves as the comprehensive guide for transforming AI Boardroom into a professional, competitive AI platform using advanced Streamlit techniques. The focus is on rapid development while maintaining the unique AI Boardroom competitive advantage.*

**Last Updated**: June 23, 2025  
**Next Review**: Weekly during development phases  
**Current Phase**: Week 1 - Visual Transformation