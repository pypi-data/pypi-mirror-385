"""
DecideNode for AI-powered decision branching in flows.
"""

from typing import List, Optional
from dataclasses import dataclass

from .base import Node


@dataclass
class Condition:
    """Condition for decision branching."""
    label: str
    description: str
    id: Optional[str] = None  # Set by backend


class DecideNode(Node):
    """Node for decision making and flow routing."""
    
    def __init__(
        self,
        id: str,
        provider_model_name: Optional[str] = None,
        conditions: Optional[List[Condition]] = None,
        decision_type: str = "ai",
        llm_temperature: Optional[float] = 0.0,
        llm_max_tokens: Optional[int] = 10000,
        function_id: Optional[str] = None
    ):
        conditions = list(conditions or [])
        if decision_type == "function":
            if not function_id:
                raise ValueError("function_id is required when decision_type is 'function'.")
            config = {
                "decision_type": decision_type,
                "function_id": function_id,
                "conditions": [
                    {"label": c.label, "description": c.description}
                    for c in conditions
                ],
            }
        else:
            if not provider_model_name:
                raise ValueError("provider_model_name is required for AI decision types.")
            config = {
                "decision_type": decision_type,
                "provider_model_name": provider_model_name,
                "conditions": [
                    {"label": c.label, "description": c.description}
                    for c in conditions
                ],
                "llm_temperature": llm_temperature if llm_temperature is not None else 0.0,
                "llm_max_tokens": llm_max_tokens if llm_max_tokens is not None else 10000,
            }
        
        # Store conditions for property access
        self._conditions = conditions
        
        super().__init__(
            id=id,
            node_type="decide",
            config=config
        )
    
    @property
    def provider_model_name(self) -> Optional[str]:
        """Get the provider model name."""
        return self.config.get("provider_model_name")
    
    @property
    def conditions(self) -> List[Condition]:
        """Get the conditions list."""
        return self._conditions
    
    @property
    def decision_type(self) -> str:
        """Get the decision type."""
        return self.config["decision_type"]
    
    @property
    def llm_temperature(self) -> Optional[float]:
        """Get the LLM temperature."""
        return self.config.get("llm_temperature")
    
    @property
    def llm_max_tokens(self) -> Optional[int]:
        """Get the LLM max tokens."""
        return self.config.get("llm_max_tokens")
    
    @property
    def function_id(self) -> Optional[str]:
        """Get the function ID for function-based decisions."""
        return self.config.get("function_id")
