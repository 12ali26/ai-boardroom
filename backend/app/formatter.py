from datetime import datetime
from typing import List, Dict, Any, Optional
import re


class DiscussionFormatter:
    """Handles formatting and presentation of discussion messages."""
    
    @staticmethod
    def format_message(message: Dict[str, Any], include_timestamp: bool = True) -> Dict[str, str]:
        """Format a single message with consistent structure."""
        formatted_message = {
            "persona": message.get("persona", "Unknown"),
            "role": message.get("role", "Unknown"),
            "content": message.get("content", ""),
            "turn": str(message.get("turn", "0")),
            "phase": message.get("phase", "unknown").title()
        }
        
        if include_timestamp:
            # Generate timestamp (in real implementation, this would come from message creation)
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message["timestamp"] = timestamp
        
        return formatted_message
    
    @staticmethod
    def format_message_for_display(message: Dict[str, Any]) -> str:
        """Format message for clean display with headers."""
        formatted = DiscussionFormatter.format_message(message)
        
        header = f"🎭 **{formatted['persona']}** ({formatted['role']}) | Turn {formatted['turn']} | {formatted['phase']} Phase"
        if formatted.get("timestamp"):
            header += f" | {formatted['timestamp']}"
        
        return f"{header}\\n\\n{formatted['content']}"
    
    @staticmethod
    def format_message_for_export(message: Dict[str, Any]) -> str:
        """Format message for text export."""
        formatted = DiscussionFormatter.format_message(message, include_timestamp=False)
        
        header = f"[Turn {formatted['turn']} - {formatted['phase']} Phase] {formatted['persona']} ({formatted['role']})"
        separator = "=" * len(header)
        
        return f"{header}\\n{separator}\\n{formatted['content']}\\n"
    
    @staticmethod
    def generate_discussion_summary(messages: List[Dict[str, Any]], topic: str) -> str:
        """Generate a structured summary of the discussion."""
        if not messages:
            return "No messages to summarize."
        
        # Group messages by phase
        phases = {}
        for msg in messages:
            phase = msg.get("phase", "unknown")
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(msg)
        
        # Count participation
        persona_counts = {}
        for msg in messages:
            persona = msg.get("persona", "Unknown")
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
        
        # Generate summary
        summary_lines = [
            "AI BOARDROOM DISCUSSION SUMMARY",
            "=" * 50,
            f"Topic: {topic}",
            f"Total Messages: {len(messages)}",
            f"Participants: {', '.join(persona_counts.keys())}",
            f"Discussion Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "PARTICIPATION BREAKDOWN:",
            "-" * 25
        ]
        
        for persona, count in persona_counts.items():
            summary_lines.append(f"• {persona}: {count} messages")
        
        summary_lines.extend(["", "PHASE BREAKDOWN:", "-" * 20])
        
        phase_order = ["opening", "debate", "synthesis"]
        for phase in phase_order:
            if phase in phases:
                phase_messages = phases[phase]
                summary_lines.append(f"• {phase.title()} Phase: {len(phase_messages)} messages")
        
        # Key themes analysis
        summary_lines.extend(["", "KEY THEMES DISCUSSED:", "-" * 25])
        all_content = " ".join([msg.get("content", "") for msg in messages]).lower()
        
        # Simple keyword analysis
        business_keywords = ["strategy", "revenue", "growth", "market", "business", "financial"]
        tech_keywords = ["technology", "development", "software", "technical", "system", "developers"]
        people_keywords = ["team", "hiring", "employees", "culture", "management", "staff"]
        
        themes_found = []
        if any(keyword in all_content for keyword in business_keywords):
            themes_found.append("Business Strategy & Growth")
        if any(keyword in all_content for keyword in tech_keywords):
            themes_found.append("Technology & Development")
        if any(keyword in all_content for keyword in people_keywords):
            themes_found.append("Team & Human Resources")
        
        if themes_found:
            for theme in themes_found:
                summary_lines.append(f"• {theme}")
        else:
            summary_lines.append("• General business discussion")
        
        return "\\n".join(summary_lines)
    
    @staticmethod
    def export_discussion_to_text(messages: List[Dict[str, Any]], topic: str) -> str:
        """Export full discussion to formatted text."""
        if not messages:
            return "No discussion to export."
        
        export_lines = [
            "AI BOARDROOM DISCUSSION EXPORT",
            "=" * 60,
            f"Topic: {topic}",
            f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Messages: {len(messages)}",
            "",
            "DISCUSSION TRANSCRIPT:",
            "=" * 60,
            ""
        ]
        
        # Add summary first
        summary = DiscussionFormatter.generate_discussion_summary(messages, topic)
        export_lines.extend([summary, "", "FULL TRANSCRIPT:", "=" * 60, ""])
        
        # Group by phases for better organization
        current_phase = None
        for msg in messages:
            msg_phase = msg.get("phase", "unknown")
            if msg_phase != current_phase:
                current_phase = msg_phase
                export_lines.extend([
                    "",
                    f"--- {msg_phase.upper()} PHASE ---",
                    ""
                ])
            
            formatted_msg = DiscussionFormatter.format_message_for_export(msg)
            export_lines.extend([formatted_msg, ""])
        
        # Add footer
        export_lines.extend([
            "=" * 60,
            "End of Discussion",
            f"Generated by AI Boardroom v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        return "\\n".join(export_lines)
    
    @staticmethod
    def get_discussion_stats(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistical information about the discussion."""
        if not messages:
            return {"total_messages": 0, "participants": {}, "phases": {}}
        
        participants = {}
        phases = {}
        total_words = 0
        
        for msg in messages:
            # Count by participant
            persona = msg.get("persona", "Unknown")
            participants[persona] = participants.get(persona, 0) + 1
            
            # Count by phase
            phase = msg.get("phase", "unknown")
            phases[phase] = phases.get(phase, 0) + 1
            
            # Word count
            content = msg.get("content", "")
            words = len(content.split())
            total_words += words
        
        avg_words = total_words / len(messages) if messages else 0
        
        return {
            "total_messages": len(messages),
            "participants": participants,
            "phases": phases,
            "total_words": total_words,
            "avg_words_per_message": round(avg_words, 1)
        }


def test_formatter():
    """Test the formatter with sample data."""
    print("Testing Discussion Formatter")
    print("=" * 40)
    
    # Sample messages
    sample_messages = [
        {
            "persona": "Alexandra Stone",
            "role": "CEO",
            "content": "We need to carefully consider the strategic implications of hiring more developers. This decision will impact our budget, team dynamics, and long-term growth trajectory.",
            "turn": 1,
            "phase": "opening"
        },
        {
            "persona": "Marcus Chen",
            "role": "CTO", 
            "content": "From a technical perspective, we're definitely understaffed. Our current team is struggling with the backlog, and we're seeing decreased code quality due to rushed deliveries.",
            "turn": 2,
            "phase": "debate"
        }
    ]
    
    formatter = DiscussionFormatter()
    topic = "Should we hire more developers?"
    
    print("1. Formatted Messages:")
    print("-" * 25)
    for msg in sample_messages:
        formatted = formatter.format_message_for_display(msg)
        print(formatted)
        print()
    
    print("2. Discussion Summary:")
    print("-" * 25)
    summary = formatter.generate_discussion_summary(sample_messages, topic)
    print(summary)
    print()
    
    print("3. Discussion Stats:")
    print("-" * 25)
    stats = formatter.get_discussion_stats(sample_messages)
    for key, value in stats.items():
        print(f"{key}: {value}")
    print()
    
    print("4. Export Preview (first 500 chars):")
    print("-" * 25)
    export_text = formatter.export_discussion_to_text(sample_messages, topic)
    print(export_text[:500] + "..." if len(export_text) > 500 else export_text)


if __name__ == "__main__":
    test_formatter()