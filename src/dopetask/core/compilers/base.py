"""Base interface for all TP Compilers."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from dopetask.core.schema import TaskPacket

class BaseCompiler(ABC):
    """Abstract base class for TP Compilers.
    
    A compiler translates a generic TaskPacket into an agent-specific execution profile.
    """
    
    @abstractmethod
    def compile(self, tp: TaskPacket) -> Any:
        """Compile a TaskPacket into a profile-specific format.
        
        Args:
            tp: The generic TaskPacket instance.
            
        Returns:
            The compiled structure (e.g., dictionary, list of prompts) specific to the agent.
            
        Raises:
            ValueError: If the generic TP lacks required fields for this specific profile.
        """
        pass
