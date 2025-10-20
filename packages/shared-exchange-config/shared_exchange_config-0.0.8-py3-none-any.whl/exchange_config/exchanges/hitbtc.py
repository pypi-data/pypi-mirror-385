"""HitBTC exchange configuration."""

from typing import Dict
from .base import BaseExchangeConfig


class HitbtcConfig(BaseExchangeConfig):
    """HitBTC exchange configuration with network mappings and aliases."""
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {}))
    
    @networks.setter
    def networks(self, value: Dict[str, str]):
        """Set network mappings."""
        self._config["networks"] = dict(value)
    
    @property
    def currency_and_network_to_alias_map(self) -> Dict[str, str]:
        """Get currency-network to alias mapping."""
        return dict(self._config.get("currency_and_network_to_alias_map", {}))
    
    @currency_and_network_to_alias_map.setter
    def currency_and_network_to_alias_map(self, value: Dict[str, str]):
        """Set currency-network to alias mapping."""
        self._config["currency_and_network_to_alias_map"] = dict(value) 