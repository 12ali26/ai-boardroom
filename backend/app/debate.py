from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from .personas import Persona, PersonaManager
from .openrouter import OpenRouterClient
from .database import DatabaseManager
from .logger import get_logger
import asyncio
import re

logger = get_logger('debate')


class DiscussionPhase(Enum):
    OPENING = "opening"
    DEBATE = "debate"
    SYNTHESIS = "synthesis"


@dataclass
class Message:
    persona: str
    role: str
    content: str
    timestamp: str
    phase: str


class DiscussionManager:
    def __init__(self, use_database: bool = True):
        self.openrouter_client = OpenRouterClient()
        self.persona_manager = PersonaManager()
        self.use_database = use_database
        self.discussions: Dict[str, Dict[str, Any]] = {}  # Memory fallback
        
        # Initialize database if requested
        if self.use_database:
            try:
                self.db_manager = DatabaseManager()
                logger.info("DiscussionManager: Database storage enabled")
            except Exception as e:
                logger.warning(f"DiscussionManager: Database initialization failed, falling back to memory: {e}")
                self.use_database = False
                self.db_manager = None
        else:
            self.db_manager = None
            logger.info("DiscussionManager: Using memory storage only")

    def start_discussion(self, topic: str, personas: Optional[List[Persona]] = None) -> str:
        """Start a new discussion with given topic and personas."""
        if personas is None:
            personas = self.persona_manager.get_all_personas()
        
        # Generate unique discussion ID
        import time
        discussion_id = f"discussion_{int(time.time())}_{len(self.discussions) + 1}"
        
        discussion_data = {
            "id": discussion_id,
            "topic": topic,
            "personas": personas,
            "messages": [],
            "current_turn": 0,
            "current_phase": DiscussionPhase.OPENING,
            "phase_turns": 0,
            "phase_limits": {
                DiscussionPhase.OPENING: 2,
                DiscussionPhase.DEBATE: 4,
                DiscussionPhase.SYNTHESIS: 2
            },
            "turn_order": [p.role for p in personas]
        }
        
        # Store in memory
        self.discussions[discussion_id] = discussion_data
        
        # Save to database if available
        if self.use_database and self.db_manager:
            try:
                self.db_manager.save_discussion(discussion_data)
                logger.debug(f"Discussion {discussion_id} saved to database")
            except Exception as e:
                logger.error(f"Failed to save discussion to database: {e}")
        
        return discussion_id

    def _analyze_message_keywords(self, content: str) -> List[str]:
        """Analyze message content for key topics and themes."""
        # Define keyword mappings for each expertise area
        keyword_mappings = {
            "technology": ["tech", "development", "developers", "software", "system", "architecture", 
                          "code", "programming", "infrastructure", "security", "scalability", "technical"],
            "business": ["strategy", "revenue", "profit", "market", "competition", "growth", 
                        "financial", "budget", "investment", "roi", "business", "vision"],
            "marketing": ["customer", "brand", "marketing", "sales", "acquisition", "retention", 
                         "campaign", "audience", "engagement", "market research", "advertising"]
        }
        
        content_lower = content.lower()
        found_keywords = []
        
        for category, keywords in keyword_mappings.items():
            for keyword in keywords:
                if keyword in content_lower:
                    found_keywords.append(category)
                    break
        
        return found_keywords

    def _select_next_persona_by_expertise(self, discussion_id: str) -> Persona:
        """Select next persona based on expertise relevance to last message."""
        discussion = self.discussions[discussion_id]
        personas = discussion["personas"]
        messages = discussion["messages"]
        
        # If no messages yet, start with CEO
        if not messages:
            return next((p for p in personas if p.role == "CEO"), personas[0])
        
        # Analyze last message
        last_message = messages[-1]
        keywords = self._analyze_message_keywords(last_message.content)
        
        # Score personas based on expertise match
        persona_scores = {}
        for persona in personas:
            score = 0
            expertise_lower = persona.expertise.lower()
            
            # Check if persona already spoke recently (avoid immediate repetition)
            recent_speakers = [msg.persona for msg in messages[-2:] if msg.persona == persona.name]
            if recent_speakers:
                score -= 10  # Penalty for recent speaking
            
            # Score based on keyword matches
            if "technology" in keywords and any(tech_word in expertise_lower for tech_word in 
                ["software", "technology", "technical", "system", "architecture"]):
                score += 5
            if "business" in keywords and any(biz_word in expertise_lower for biz_word in 
                ["strategy", "business", "financial", "leadership", "market"]):
                score += 5
            if "marketing" in keywords and any(mkt_word in expertise_lower for mkt_word in 
                ["marketing", "brand", "customer", "acquisition"]):
                score += 5
            
            persona_scores[persona] = score
        
        # Select persona with highest score
        best_persona = max(persona_scores, key=persona_scores.get)
        return best_persona

    def _get_current_persona(self, discussion_id: str) -> Persona:
        """Get the current persona whose turn it is to speak."""
        discussion = self.discussions[discussion_id]
        current_phase = discussion["current_phase"]
        
        # Use expertise-based selection for debate phase
        if current_phase == DiscussionPhase.DEBATE:
            return self._select_next_persona_by_expertise(discussion_id)
        
        # Use round-robin for opening and synthesis phases
        current_turn = discussion["current_turn"]
        turn_order = discussion["turn_order"]
        personas = discussion["personas"]
        
        current_role = turn_order[current_turn % len(turn_order)]
        
        for persona in personas:
            if persona.role == current_role:
                return persona
        
        return personas[0]  # Fallback

    def _advance_turn(self, discussion_id: str) -> None:
        """Advance to the next person's turn and manage phases."""
        discussion = self.discussions[discussion_id]
        discussion["current_turn"] += 1
        discussion["phase_turns"] += 1
        
        # Check if we need to advance to next phase
        current_phase = discussion["current_phase"]
        phase_limit = discussion["phase_limits"][current_phase]
        
        if discussion["phase_turns"] >= phase_limit:
            # Advance to next phase
            if current_phase == DiscussionPhase.OPENING:
                discussion["current_phase"] = DiscussionPhase.DEBATE
            elif current_phase == DiscussionPhase.DEBATE:
                discussion["current_phase"] = DiscussionPhase.SYNTHESIS
            # SYNTHESIS is the final phase
            
            discussion["phase_turns"] = 0  # Reset phase turn counter

    def _get_phase_instructions(self, phase: DiscussionPhase) -> str:
        """Get phase-specific instructions for personas."""
        instructions = {
            DiscussionPhase.OPENING: "This is the OPENING phase. Present your initial position and key concerns. Be concise and establish your perspective.",
            DiscussionPhase.DEBATE: "This is the DEBATE phase. Engage with others' points, challenge assumptions, and defend your position with specific examples and reasoning.",
            DiscussionPhase.SYNTHESIS: "This is the SYNTHESIS phase. Work toward consensus, summarize key insights, and propose concrete next steps or recommendations."
        }
        return instructions.get(phase, "")

    def _build_context_messages(self, discussion_id: str, current_persona: Persona) -> List[Dict[str, str]]:
        """Build context messages for the AI model."""
        discussion = self.discussions[discussion_id]
        topic = discussion["topic"]
        messages = discussion["messages"]
        current_phase = discussion["current_phase"]
        phase_instructions = self._get_phase_instructions(current_phase)
        
        # System message with persona and context
        system_message = {
            "role": "system",
            "content": f"""You are {current_persona.name}, the {current_persona.role} in a boardroom discussion.

Your personality: {current_persona.personality}
Your expertise: {current_persona.expertise}

You are participating in a structured boardroom debate about: "{topic}"

{phase_instructions}

Guidelines:
- Stay in character as {current_persona.name}
- Provide thoughtful insights from your role's perspective
- Keep responses concise (2-3 paragraphs max)
- Be professional but show your personality
- Build on or respectfully challenge previous points when relevant
- Focus on actionable insights and business implications"""
        }
        
        context_messages = [system_message]
        
        # Add previous discussion messages
        for msg in messages:
            context_messages.append({
                "role": "assistant" if msg.persona != current_persona.name else "user",
                "content": f"[{msg.persona} - {msg.role}] ({msg.phase}): {msg.content}"
            })
        
        # Add current prompt
        if not messages:
            context_messages.append({
                "role": "user",
                "content": f"Please provide your initial thoughts on this topic: {topic}"
            })
        else:
            context_messages.append({
                "role": "user",
                "content": "Please provide your response to the ongoing discussion."
            })
        
        return context_messages

    async def get_next_response(self, discussion_id: str) -> Dict[str, Any]:
        """Get the next response in the discussion."""
        # Try to load from database if not in memory
        if discussion_id not in self.discussions:
            if not self.load_discussion_from_db(discussion_id):
                raise ValueError(f"Discussion {discussion_id} not found")
        
        current_persona = self._get_current_persona(discussion_id)
        context_messages = self._build_context_messages(discussion_id, current_persona)
        
        try:
            # Get response from OpenRouter
            response = await self.openrouter_client.chat_completion(
                model=current_persona.model,
                messages=context_messages,
                max_tokens=500,
                temperature=0.7
            )
            
            content = response["choices"][0]["message"]["content"]
            
            # Store the message
            current_phase = self.discussions[discussion_id]["current_phase"]
            message = Message(
                persona=current_persona.name,
                role=current_persona.role,
                content=content,
                timestamp=str(len(self.discussions[discussion_id]["messages"]) + 1),
                phase=current_phase.value
            )
            
            # Add to memory storage
            self.discussions[discussion_id]["messages"].append(message)
            
            # Save message to database if available
            if self.use_database and self.db_manager:
                try:
                    message_data = {
                        "persona": message.persona,
                        "role": message.role,
                        "content": message.content,
                        "phase": message.phase,
                        "turn": message.timestamp
                    }
                    self.db_manager.save_message(discussion_id, message_data)
                    logger.debug(f"Message saved to database for discussion {discussion_id}")
                except Exception as e:
                    logger.error(f"Failed to save message to database: {e}")
            
            # Advance turn
            self._advance_turn(discussion_id)
            
            # Update discussion state in database
            if self.use_database and self.db_manager:
                try:
                    self.db_manager.save_discussion(self.discussions[discussion_id])
                    logger.debug(f"Discussion state updated in database: {discussion_id}")
                except Exception as e:
                    logger.error(f"Failed to update discussion in database: {e}")
            
            return {
                "persona": current_persona.name,
                "role": current_persona.role,
                "content": content,
                "turn": len(self.discussions[discussion_id]["messages"]),
                "phase": current_phase.value
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get response from {current_persona.name}: {str(e)}",
                "persona": current_persona.name,
                "role": current_persona.role
            }

    def load_discussion_from_db(self, discussion_id: str) -> bool:
        """Load a discussion from database into memory."""
        if not self.use_database or not self.db_manager:
            return False
        
        try:
            db_discussion = self.db_manager.load_discussion(discussion_id)
            if not db_discussion:
                return False
            
            # Convert personas data back to Persona objects
            personas = []
            for p_data in db_discussion.get('personas_data', []):
                from .personas import Persona
                persona = Persona(
                    name=p_data['name'],
                    model=p_data['model'],
                    role=p_data['role'],
                    personality=p_data['personality'],
                    expertise=p_data['expertise']
                )
                personas.append(persona)
            
            # Convert messages to Message objects
            messages = []
            for msg_data in db_discussion.get('messages', []):
                message = Message(
                    persona=msg_data['persona'],
                    role=msg_data['role'],
                    content=msg_data['content'],
                    timestamp=str(msg_data['turn']),
                    phase=msg_data['phase']
                )
                messages.append(message)
            
            # Convert phase string back to enum
            current_phase_str = db_discussion.get('current_phase', 'opening')
            current_phase = DiscussionPhase(current_phase_str)
            
            # Reconstruct phase_limits with enum keys
            phase_limits = {}
            for phase_str, limit in db_discussion.get('phase_limits', {}).items():
                if phase_str in ['opening', 'debate', 'synthesis']:
                    phase_limits[DiscussionPhase(phase_str)] = limit
            
            # Load into memory
            self.discussions[discussion_id] = {
                "id": discussion_id,
                "topic": db_discussion['topic'],
                "personas": personas,
                "messages": messages,
                "current_turn": db_discussion['current_turn'],
                "current_phase": current_phase,
                "phase_turns": db_discussion['phase_turns'],
                "phase_limits": phase_limits,
                "turn_order": db_discussion['turn_order']
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading discussion from database: {e}")
            return False
    
    def list_saved_discussions(self) -> List[Dict[str, Any]]:
        """List saved discussions from database."""
        if not self.use_database or not self.db_manager:
            # Return memory-only discussions
            return [
                {
                    'id': disc_id,
                    'topic': disc_data.get('topic', 'Unknown'),
                    'message_count': len(disc_data.get('messages', [])),
                    'status': 'memory_only'
                }
                for disc_id, disc_data in self.discussions.items()
            ]
        
        try:
            return self.db_manager.list_discussions()
        except Exception as e:
            logger.error(f"Error listing discussions: {e}")
            return []
    
    def delete_discussion(self, discussion_id: str) -> bool:
        """Delete a discussion from both memory and database."""
        success = True
        
        # Remove from memory
        if discussion_id in self.discussions:
            del self.discussions[discussion_id]
        
        # Remove from database
        if self.use_database and self.db_manager:
            try:
                db_success = self.db_manager.delete_discussion(discussion_id)
                success = success and db_success
            except Exception as e:
                logger.error(f"Error deleting discussion from database: {e}")
                success = False
        
        return success
    
    def get_discussion_messages(self, discussion_id: str) -> List[Dict[str, Any]]:
        """Get all messages from a discussion."""
        # Try to load from database if not in memory
        if discussion_id not in self.discussions:
            if not self.load_discussion_from_db(discussion_id):
                return []
        
        if discussion_id not in self.discussions:
            return []
        
        messages = self.discussions[discussion_id]["messages"]
        return [
            {
                "persona": msg.persona,
                "role": msg.role,
                "content": msg.content,
                "turn": msg.timestamp,
                "phase": msg.phase
            }
            for msg in messages
        ]


async def test_discussion():
    """Test the discussion manager with database integration."""
    print("Testing Enhanced Discussion Manager with Database")
    print("=" * 60)
    
    # Test with database enabled
    manager = DiscussionManager(use_database=True)
    topic = "Should we hire more developers?"
    
    # Start discussion
    discussion_id = manager.start_discussion(topic)
    print(f"Started discussion: {topic}")
    print(f"Discussion ID: {discussion_id}")
    print(f"Database enabled: {manager.use_database}")
    print()
    
    # Run full discussion cycle (8 turns total: 2 opening + 4 debate + 2 synthesis)
    max_turns = 8
    for turn_num in range(max_turns):
        discussion = manager.discussions[discussion_id]
        current_phase = discussion["current_phase"]
        phase_turns = discussion["phase_turns"]
        
        print(f"Turn {turn_num + 1} - Phase: {current_phase.value.upper()} ({phase_turns + 1}/{ discussion['phase_limits'][current_phase]}):")
        print("-" * 50)
        
        response = await manager.get_next_response(discussion_id)
        
        if "error" in response:
            print(f"Error: {response['error']}")
            break
        else:
            print(f"🎭 {response['persona']} ({response['role']}) - {response['phase']}:")
            print(f"{response['content']}")
        
        print()
        
        # Check if discussion is complete
        if discussion["current_phase"] == DiscussionPhase.SYNTHESIS and discussion["phase_turns"] >= discussion["phase_limits"][DiscussionPhase.SYNTHESIS]:
            print("🏁 Discussion completed!")
            break
    
    # Test database functionality
    if manager.use_database:
        print("\n💾 Testing Database Features:")
        print("-" * 40)
        
        # List discussions
        discussions = manager.list_saved_discussions()
        print(f"Saved discussions: {len(discussions)}")
        
        # Test loading discussion
        print(f"Reloading discussion {discussion_id}...")
        manager.discussions.clear()  # Clear memory
        reloaded_messages = manager.get_discussion_messages(discussion_id)
        print(f"Reloaded {len(reloaded_messages)} messages from database")
    
    # Show all messages with phase information
    print("\n📋 Full Discussion History:")
    print("=" * 60)
    messages = manager.get_discussion_messages(discussion_id)
    current_phase = None
    for msg in messages:
        if msg['phase'] != current_phase:
            current_phase = msg['phase']
            print(f"\n--- {current_phase.upper()} PHASE ---")
        
        print(f"Turn {msg['turn']} - {msg['persona']} ({msg['role']}):")
        print(f"{msg['content']}")
        print("-" * 40)
    
    # Test memory-only mode
    print("\n🧠 Testing Memory-Only Mode:")
    print("-" * 40)
    memory_manager = DiscussionManager(use_database=False)
    memory_discussion_id = memory_manager.start_discussion("Memory test topic")
    print(f"Memory-only discussion created: {memory_discussion_id}")
    print(f"Database enabled: {memory_manager.use_database}")


if __name__ == "__main__":
    asyncio.run(test_discussion())