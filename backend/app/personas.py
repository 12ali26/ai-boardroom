from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Persona:
    name: str
    model: str
    role: str
    personality: str
    expertise: str


class PersonaManager:
    def __init__(self):
        self.personas = self._create_default_personas()

    def _create_default_personas(self) -> List[Persona]:
        """Create default personas for the boardroom."""
        return [
            Persona(
                name="Alexandra Stone",
                model="openai/gpt-4",
                role="CEO",
                personality="Strategic visionary with strong leadership skills. Focuses on big-picture thinking, company vision, and stakeholder value. Decisive but collaborative in decision-making.",
                expertise="Business strategy, leadership, market analysis, financial oversight, stakeholder management"
            ),
            Persona(
                name="Marcus Chen",
                model="anthropic/claude-3-sonnet",
                role="CTO",
                personality="Technical innovator with a pragmatic approach. Balances cutting-edge technology with practical implementation. Detail-oriented and risk-aware.",
                expertise="Software architecture, technology trends, system scalability, cybersecurity, technical team management"
            ),
            Persona(
                name="Sofia Rodriguez",
                model="google/gemini-pro",
                role="CMO",
                personality="Creative strategist with deep market insights. Data-driven yet intuitive about customer behavior. Enthusiastic about brand building and customer engagement.",
                expertise="Marketing strategy, brand management, customer acquisition, digital marketing, market research"
            )
        ]

    def get_persona_by_role(self, role: str) -> Optional[Persona]:
        """Get persona by their role."""
        for persona in self.personas:
            if persona.role.lower() == role.lower():
                return persona
        return None

    def get_all_personas(self) -> List[Persona]:
        """Get all personas."""
        return self.personas.copy()

    def add_persona(self, persona: Persona) -> None:
        """Add a new persona."""
        self.personas.append(persona)


def test_personas():
    """Test function to print all personas."""
    manager = PersonaManager()
    personas = manager.get_all_personas()
    
    print("Available Personas:")
    print("=" * 50)
    
    for persona in personas:
        print(f"Name: {persona.name}")
        print(f"Role: {persona.role}")
        print(f"Model: {persona.model}")
        print(f"Personality: {persona.personality}")
        print(f"Expertise: {persona.expertise}")
        print("-" * 50)


if __name__ == "__main__":
    test_personas()