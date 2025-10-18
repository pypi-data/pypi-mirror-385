"""Track event for analytics."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from .context import RequestContext


class EventType(Enum):
    """Event types for tracking."""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


class TrackEvent:
    """Track event for analytics."""
    
    def __init__(
        self,
        variant_key: str,
        event_type: EventType,
        reward: Optional[float] = None,
        context: Optional[RequestContext] = None,
        created_at: Optional[datetime] = None,
        dedup_key: Optional[str] = None
    ):
        """Initialize track event.
        
        Args:
            variant_key: The variant key that was evaluated
            event_type: Type of event
            reward: Optional reward value
            context: RequestContext instance
            created_at: When the event occurred
            dedup_key: Deduplication key to prevent duplicate events
        """
        self.variant_key = variant_key
        self.event_type = event_type
        self.reward = reward
        self.context = context or RequestContext.new()
        self.created_at = created_at
        self.dedup_key = dedup_key
    
    @classmethod
    def new(
        cls,
        variant_key: str,
        event_type: Union[EventType, str],
        **kwargs
    ) -> "TrackEvent":
        """Create a new track event.
        
        Args:
            variant_key: The variant key that was evaluated
            event_type: Type of event (EventType enum or string)
            **kwargs: Additional parameters
            
        Returns:
            New TrackEvent instance
        """
        if isinstance(event_type, str):
            event_type = EventType(event_type)
        
        return cls(
            variant_key=variant_key,
            event_type=event_type,
            **kwargs
        )
    
    def with_reward(self, reward: float) -> "TrackEvent":
        """Add a reward value to the track event.
        
        Args:
            reward: Reward value
            
        Returns:
            Updated TrackEvent instance
        """
        self.reward = reward
        return self
    
    def with_context(self, key: str, value: Any) -> "TrackEvent":
        """Add context data to the track event using RequestContext.
        
        Args:
            key: Context key
            value: Context value
            
        Returns:
            Updated TrackEvent instance
        """
        self.context.set(key, value)
        return self
    
    def with_contexts(self, contexts: Dict[str, Any]) -> "TrackEvent":
        """Add multiple context key-value pairs to the track event.
        
        Args:
            contexts: Dictionary of context data
            
        Returns:
            Updated TrackEvent instance
        """
        for key, value in contexts.items():
            self.context.set(key, value)
        return self
    
    def with_request_context(self, context: RequestContext) -> "TrackEvent":
        """Set the context to a specific RequestContext instance.
        
        Args:
            context: RequestContext instance
            
        Returns:
            Updated TrackEvent instance
        """
        self.context = context
        return self
    
    def with_created_at(self, created_at: datetime) -> "TrackEvent":
        """Set the creation timestamp for the track event.
        
        Args:
            created_at: Creation timestamp
            
        Returns:
            Updated TrackEvent instance
        """
        self.created_at = created_at
        return self
    
    def with_dedup_key(self, dedup_key: str) -> "TrackEvent":
        """Set the deduplication key for the track event.
        
        Args:
            dedup_key: Deduplication key
            
        Returns:
            Updated TrackEvent instance
        """
        self.dedup_key = dedup_key
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the track event to a dictionary for API requests.
        
        Returns:
            Dictionary representation of the track event
        """
        result = {
            "variant_key": self.variant_key,
            "event_type": self.event_type.value,
            "context": self.context.to_dict()
        }
        
        if self.reward is not None:
            result["reward"] = self.reward
        
        if self.created_at is not None:
            result["created_at"] = self.created_at.isoformat()
        
        if self.dedup_key is not None:
            result["dedup_key"] = self.dedup_key
        
        return result
    
    def __repr__(self) -> str:
        """String representation of the track event."""
        return (f"TrackEvent(variant_key='{self.variant_key}', "
                f"event_type={self.event_type.value}, "
                f"reward={self.reward}, "
                f"context={self.context}, "
                f"created_at={self.created_at}, "
                f"dedup_key='{self.dedup_key}')")
