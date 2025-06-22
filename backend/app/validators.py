import re
from typing import Dict, List, Optional, Tuple
from .logger import get_logger

logger = get_logger('validators')


class InputValidator:
    """Validates user inputs for AI Boardroom application."""
    
    # Topic validation constants
    MIN_TOPIC_LENGTH = 10
    MAX_TOPIC_LENGTH = 500
    
    # Forbidden patterns (basic content filtering)
    FORBIDDEN_PATTERNS = [
        r'\b(hack|exploit|malicious|virus|spam)\b',
        r'\b(illegal|fraud|scam|phishing)\b',
        r'<script.*?>',  # Prevent script injection
        r'javascript:',  # Prevent javascript execution
    ]
    
    # Common business topic keywords (for suggestions)
    BUSINESS_KEYWORDS = [
        'strategy', 'growth', 'revenue', 'market', 'customer', 'product',
        'team', 'hire', 'budget', 'investment', 'technology', 'digital',
        'innovation', 'competition', 'expansion', 'cost', 'profit', 'risk'
    ]
    
    @staticmethod
    def validate_topic(topic: str) -> Tuple[bool, str, List[str]]:
        """Validate discussion topic input.
        
        Returns:
            Tuple of (is_valid, cleaned_topic, warnings)
        """
        warnings = []
        
        if not topic or not isinstance(topic, str):
            return False, "", ["Topic cannot be empty"]
        
        # Clean and normalize
        cleaned_topic = topic.strip()
        
        # Length validation
        if len(cleaned_topic) < InputValidator.MIN_TOPIC_LENGTH:
            return False, cleaned_topic, [f"Topic must be at least {InputValidator.MIN_TOPIC_LENGTH} characters long"]
        
        if len(cleaned_topic) > InputValidator.MAX_TOPIC_LENGTH:
            return False, cleaned_topic, [f"Topic must be less than {InputValidator.MAX_TOPIC_LENGTH} characters"]
        
        # Content validation
        for pattern in InputValidator.FORBIDDEN_PATTERNS:
            if re.search(pattern, cleaned_topic, re.IGNORECASE):
                logger.warning(f"Topic contains forbidden pattern: {pattern}")
                return False, cleaned_topic, ["Topic contains inappropriate content"]
        
        # Check if topic looks like a business discussion
        has_business_keywords = any(
            keyword in cleaned_topic.lower() 
            for keyword in InputValidator.BUSINESS_KEYWORDS
        )
        
        if not has_business_keywords:
            warnings.append("Consider adding business-related keywords for better discussion")
        
        # Check if it's a question
        if not (cleaned_topic.endswith('?') or any(word in cleaned_topic.lower() for word in ['should', 'how', 'what', 'when', 'where', 'why'])):
            warnings.append("Consider framing as a question for better debate")
        
        logger.info(f"Topic validated successfully: {cleaned_topic[:50]}...")
        return True, cleaned_topic, warnings
    
    @staticmethod
    def validate_persona_selection(selected_personas: List[str]) -> Tuple[bool, List[str]]:
        """Validate persona selection.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not selected_personas:
            errors.append("At least one persona must be selected")
        
        if len(selected_personas) > 5:
            errors.append("Maximum 5 personas allowed for manageable discussions")
        
        # Check for duplicates
        if len(selected_personas) != len(set(selected_personas)):
            errors.append("Duplicate personas selected")
        
        valid_roles = ['CEO', 'CTO', 'CMO', 'CFO', 'COO']  # Add more as needed
        for persona in selected_personas:
            if persona not in valid_roles:
                errors.append(f"Invalid persona role: {persona}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_discussion_settings(settings: Dict) -> Tuple[bool, Dict, List[str]]:
        """Validate discussion configuration settings.
        
        Returns:
            Tuple of (is_valid, cleaned_settings, error_messages)
        """
        errors = []
        cleaned_settings = settings.copy()
        
        # Validate max turns
        max_turns = settings.get('max_turns', 8)
        if not isinstance(max_turns, int) or max_turns < 3 or max_turns > 20:
            errors.append("Max turns must be between 3 and 20")
            cleaned_settings['max_turns'] = 8
        
        # Validate temperature
        temperature = settings.get('temperature', 0.7)
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            errors.append("Temperature must be between 0 and 2")
            cleaned_settings['temperature'] = 0.7
        
        # Validate phase limits
        phase_limits = settings.get('phase_limits', {})
        if phase_limits:
            total_turns = sum(phase_limits.values())
            if total_turns != max_turns:
                errors.append(f"Phase limits ({total_turns}) must sum to max turns ({max_turns})")
        
        return len(errors) == 0, cleaned_settings, errors
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize text input to prevent injection attacks."""
        if not isinstance(text, str):
            return str(text)
        
        # Remove potential script tags and javascript
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        # Limit length
        return text[:1000]  # Reasonable limit
    
    @staticmethod
    def suggest_topic_improvements(topic: str) -> List[str]:
        """Suggest improvements for a topic."""
        suggestions = []
        
        topic_lower = topic.lower()
        
        # Suggest making it a question
        if not topic.endswith('?') and not any(word in topic_lower for word in ['should', 'how', 'what']):
            suggestions.append("💡 Try rephrasing as a question (e.g., 'Should we...' or 'How can we...')")
        
        # Suggest adding context
        if len(topic) < 30:
            suggestions.append("💡 Consider adding more context or background to the topic")
        
        # Suggest business focus
        business_words = ['budget', 'revenue', 'market', 'customer', 'team', 'strategy']
        if not any(word in topic_lower for word in business_words):
            suggestions.append("💡 Consider relating the topic to business outcomes (revenue, customers, strategy, etc.)")
        
        # Suggest specific timeframes
        time_words = ['quarterly', 'annual', 'next year', 'short-term', 'long-term']
        if not any(word in topic_lower for word in time_words):
            suggestions.append("💡 Consider adding a timeframe (e.g., 'this quarter', 'next year')")
        
        return suggestions[:3]  # Limit to 3 suggestions


def test_validators():
    """Test the input validators."""
    print("Testing Input Validators")
    print("=" * 40)
    
    validator = InputValidator()
    
    # Test topics
    test_topics = [
        "Should we hire more developers?",  # Good
        "Hi",  # Too short
        "Should we hack the competition?",  # Forbidden content
        "Let's discuss quarterly revenue growth strategies",  # Good business topic
        "a" * 600,  # Too long
    ]
    
    print("1. Testing topic validation:")
    for i, topic in enumerate(test_topics, 1):
        is_valid, cleaned, warnings = validator.validate_topic(topic)
        print(f"  {i}. '{topic[:50]}...' -> Valid: {is_valid}")
        if warnings:
            print(f"     Warnings: {', '.join(warnings)}")
    
    # Test persona selection
    print("\n2. Testing persona validation:")
    test_personas = [
        ['CEO', 'CTO'],  # Valid
        [],  # Empty
        ['CEO', 'CTO', 'CMO', 'CFO', 'COO', 'INVALID'],  # Too many + invalid
    ]
    
    for i, personas in enumerate(test_personas, 1):
        is_valid, errors = validator.validate_persona_selection(personas)
        print(f"  {i}. {personas} -> Valid: {is_valid}")
        if errors:
            print(f"     Errors: {', '.join(errors)}")
    
    # Test suggestions
    print("\n3. Testing topic suggestions:")
    test_topic = "hire people"
    suggestions = validator.suggest_topic_improvements(test_topic)
    print(f"  Topic: '{test_topic}'")
    for suggestion in suggestions:
        print(f"  {suggestion}")


if __name__ == "__main__":
    test_validators()