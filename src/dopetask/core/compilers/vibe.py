"""Mistral Vibe compiler for MICRO_TASK profile."""

from typing import Dict, Any, List
from dopetask.core.schema import TaskPacket
from dopetask.core.compilers.base import BaseCompiler

class VibeCompiler(BaseCompiler):
    """Compiles generic TPs into the MICRO_TASK format for Mistral Vibe.
    
    This profile slices the TaskPacket into tiny, isolated prompts per task.
    """
    
    def compile(self, tp: TaskPacket) -> List[Dict[str, Any]]:
        """Compile the TaskPacket into the Vibe format.
        
        Args:
            tp: The generic TaskPacket instance.
            
        Returns:
            A list of isolated micro-tasks.
        """
        micro_tasks = []
        
        for step in tp.steps:
            task_description = step.task
            if step.requirements:
                reqs = "\n".join([f"- {r}" for r in step.requirements])
                task_description += f"\n\nRequirements:\n{reqs}"
                
            micro_tasks.append({
                "tp_id": tp.id,
                "step_id": step.id,
                "task": task_description,
                "constraints": [
                    "Do not generalize.",
                    "Do not create extra files.",
                    "Do not explain."
                ]
            })
            
        return micro_tasks
