"""Task Packet Parser and Normalizer."""

import json
from typing import Dict, Any, Union
from pathlib import Path

from dopetask.core.schema import TaskPacket
from dopetask.core.compilers.base import BaseCompiler
from dopetask.core.compilers.gemini import GeminiCompiler
from dopetask.core.compilers.codex import CodexCompiler
from dopetask.core.compilers.vibe import VibeCompiler

class TPParser:
    """Parses raw Task Packet data into the generic schema."""
    
    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> TaskPacket:
        """Parse a dictionary into a TaskPacket object.
        
        Args:
            data: The raw dictionary containing TP data.
            
        Returns:
            A generic TaskPacket instance.
            
        Raises:
            ValueError: If the required fields are missing.
        """
        if "id" not in data:
            raise ValueError("TaskPacket must have an 'id'.")
            
        return TaskPacket.from_dict(data)
        
    @staticmethod
    def parse_file(path: Union[str, Path]) -> TaskPacket:
        """Parse a JSON file into a TaskPacket object.
        
        Args:
            path: Path to the JSON file.
            
        Returns:
            A generic TaskPacket instance.
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return TPParser.parse_dict(data)


class TPNormalizer:
    """Routes a generic TaskPacket to the appropriate compiler profile."""
    
    COMPILERS = {
        "gemini": GeminiCompiler,
        "codex": CodexCompiler,
        "vibe": VibeCompiler
    }
    
    @classmethod
    def compile(cls, tp: TaskPacket, profile: str) -> Any:
        """Compile a TaskPacket using the requested agent profile.
        
        Args:
            tp: The generic TaskPacket instance.
            profile: The target agent profile ("gemini", "codex", "vibe").
            
        Returns:
            The profile-specific compiled TP structure.
            
        Raises:
            ValueError: If the profile is unknown or if the compiler rejects the TP.
        """
        profile = profile.lower()
        if profile not in cls.COMPILERS:
            raise ValueError(f"Unknown compilation profile: {profile}. Available: {list(cls.COMPILERS.keys())}")
            
        compiler_cls = cls.COMPILERS[profile]
        compiler = compiler_cls()
        
        return compiler.compile(tp)
