from typing import Dict, Any, List
import os

class KnowledgeSources:
    def __init__(self):
        self.sources: Dict[str, Any] = {}
        
    def add_source(self, name: str, source: Any) -> None:
        """Add a new knowledge source."""
        self.sources[name] = source
        
    def get_source(self, name: str) -> Any:
        """Get a knowledge source by name."""
        return self.sources.get(name)
        
    def list_sources(self) -> List[str]:
        """List all available knowledge sources."""
        return list(self.sources.keys()) 