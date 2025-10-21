"""KuCoin exchange configuration."""

from typing import Dict, List
from .base import BaseExchangeConfig


class KucoinConfig(BaseExchangeConfig):
    """KuCoin exchange configuration with network mappings and deposit addresses."""
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {}))
    
    @networks.setter
    def networks(self, value: Dict[str, str]):
        """Set network mappings."""
        self._config["networks"] = dict(value)
    
    @property
    def networks_for_deposit_addresses(self) -> Dict[str, str]:
        """Get networks available for deposit addresses."""
        return dict(self._config.get("networks_for_deposit_addresses", {}))
    
    @networks_for_deposit_addresses.setter
    def networks_for_deposit_addresses(self, value: Dict[str, str]):
        """Set networks available for deposit addresses."""
        self._config["networks_for_deposit_addresses"] = dict(value) 
