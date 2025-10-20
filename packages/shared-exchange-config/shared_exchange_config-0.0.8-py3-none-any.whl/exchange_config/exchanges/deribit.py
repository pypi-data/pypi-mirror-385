"""Deribit exchange configuration."""

from typing import Dict
from .base import BaseExchangeConfig


class DeribitConfig(BaseExchangeConfig):
    """Deribit exchange configuration with simple network mappings."""
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {}))
    
    @networks.setter
    def networks(self, value: Dict[str, str]):
        """Set network mappings."""
        self._config["networks"] = dict(value) 