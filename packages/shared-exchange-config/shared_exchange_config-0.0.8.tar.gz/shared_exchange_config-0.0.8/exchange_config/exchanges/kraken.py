"""Kraken exchange configuration."""

from typing import Dict, List, Optional
from .base import BaseExchangeConfig
from ..exceptions import CurrencyNotFoundError


class KrakenConfig(BaseExchangeConfig):
    """Kraken exchange configuration with currency aliases and network alias mappings."""
    
    @property
    def alias_to_currency_map(self) -> Dict[str, str]:
        """Get alias to currency mapping."""
        return dict(self._config.get("alias_to_currency_map", {}))
    
    @alias_to_currency_map.setter
    def alias_to_currency_map(self, value: Dict[str, str]):
        """Set alias to currency mapping."""
        self._config["alias_to_currency_map"] = dict(value)
    
    @property
    def currency_and_network_to_alias_map(self) -> Dict[str, str]:
        """Get currency-network to alias mapping."""
        return dict(self._config.get("currency_and_network_to_alias_map", {}))
    
    @currency_and_network_to_alias_map.setter
    def currency_and_network_to_alias_map(self, value: Dict[str, str]):
        """Set currency-network to alias mapping."""
        self._config["currency_and_network_to_alias_map"] = dict(value)
    
    @property
    def currency_and_network_to_alias_map_for_deposit_address(self) -> Dict[str, str]:
        """Get currency-network to alias mapping for deposit addresses."""
        return dict(self._config.get("currency_and_network_to_alias_map_for_deposit_address", {}))
    
    @currency_and_network_to_alias_map_for_deposit_address.setter
    def currency_and_network_to_alias_map_for_deposit_address(self, value: Dict[str, str]):
        """Set currency-network to alias mapping for deposit addresses."""
        self._config["currency_and_network_to_alias_map_for_deposit_address"] = dict(value)
    
    @property
    def currency_and_network_to_alias_map_for_whitelist(self) -> Dict[str, str]:
        """Get currency-network to alias mapping for whitelist."""
        return dict(self._config.get("currency_and_network_to_alias_map_for_whitelist", {}))
    
    @currency_and_network_to_alias_map_for_whitelist.setter
    def currency_and_network_to_alias_map_for_whitelist(self, value: Dict[str, str]):
        """Set currency-network to alias mapping for whitelist."""
        self._config["currency_and_network_to_alias_map_for_whitelist"] = dict(value)
    
    @property
    def alias_to_network_map(self) -> Dict[str, str]:
        """Get alias to network mapping."""
        return dict(self._config.get("alias_to_network_map", {}))
    
    @alias_to_network_map.setter
    def alias_to_network_map(self, value: Dict[str, str]):
        """Set alias to network mapping."""
        self._config["alias_to_network_map"] = dict(value)
    
    # Alias Methods
    def get_currency_alias(self, alias: str) -> Optional[str]:
        """Get currency for an alias."""
        return self.alias_to_currency_map.get(alias)
    
    def get_currency_aliases(self, currency: str) -> List[str]:
        """Get all aliases for a currency."""
        return [alias for alias, curr in self.alias_to_currency_map.items() if curr == currency]
