import json
from typing import Dict, Any, List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import config


class EmbeddingProcessor:
    """Class for processing embeddings and combining instructions with user context."""
    
    def __init__(self):
        """Initialize the embedding processor with the specified model."""
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.prebuilt_instructions = self._load_prebuilt_instructions()
    
    def _load_prebuilt_instructions(self) -> List[str]:
        """Load prebuilt instructions from a file or define them directly."""
        # In a real application, these might be loaded from a file
        return [
            "Provide accurate event information based on user preferences.",
            "Suggest events that match the user's budget constraints.",
            "Consider accessibility needs when recommending events and transportation.",
            "Verify that suggested events are available during the user's specified time window.",
            "Provide clear navigation instructions between events.",
            "Prioritize events that match the user's specified theme or interests.",
            "Ensure travel times between events are reasonable and account for transportation mode."
        ]
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate an embedding for the given text."""
        return self.model.encode(text)
    
    def combine_instructions_with_context(self, user_context: Dict[str, Any]) -> str:
        """Combine prebuilt instructions with user context to create a prompt for Claude."""
        # Convert user context to a string representation
        context_str = json.dumps(user_context, indent=2)
        
        # Combine instructions with context
        combined_prompt = "User Information:\n" + context_str + "\n\nInstructions:\n"
        
        # Add each instruction
        for i, instruction in enumerate(self.prebuilt_instructions):
            combined_prompt += f"{i+1}. {instruction}\n"
        
        # Add final guidance
        combined_prompt += "\nBased on the above user information and instructions, please provide event recommendations and navigation details."
        
        return combined_prompt
    
    def create_claude_prompt(self, user_context: Dict[str, Any], user_query: Optional[str] = None) -> str:
        """Create a complete prompt for Claude AI."""
        combined_instructions = self.combine_instructions_with_context(user_context)
        
        if user_query:
            prompt = f"User Query: {user_query}\n\n{combined_instructions}"
        else:
            prompt = combined_instructions
            
        return prompt 