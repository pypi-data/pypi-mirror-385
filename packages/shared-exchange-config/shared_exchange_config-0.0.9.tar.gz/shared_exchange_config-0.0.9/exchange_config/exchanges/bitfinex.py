"""Bitfinex exchange configuration."""

from typing import Dict, List
from .base import BaseExchangeConfig


class BitfinexConfig(BaseExchangeConfig):
    """Bitfinex exchange configuration with special alias mappings and wallet features."""
    
    @property
    def currency_and_network_to_alias_map(self) -> Dict[str, str]:
        """Get currency-network to alias mapping."""
        return dict(self._config.get("currency_and_network_to_alias_map", {}))
    
    @currency_and_network_to_alias_map.setter
    def currency_and_network_to_alias_map(self, value: Dict[str, str]):
        """Set currency-network to alias mapping."""
        self._config["currency_and_network_to_alias_map"] = dict(value)
    
    @property
    def wallet_type_exchange_deposit_address_available(self) -> List[str]:
        """Get wallet types with exchange deposit address available."""
        return list(self._config.get("wallet_type_exchange_deposit_address_available", []))
    
    @wallet_type_exchange_deposit_address_available.setter
    def wallet_type_exchange_deposit_address_available(self, value: List[str]):
        """Set wallet types with exchange deposit address available."""
        self._config["wallet_type_exchange_deposit_address_available"] = list(value)
    
    @property
    def currency_mapping_reversed(self) -> Dict[str, str]:
        """Get reversed currency mapping."""
        return dict(self._config.get("currency_mapping_reversed", {}))
    
    @currency_mapping_reversed.setter
    def currency_mapping_reversed(self, value: Dict[str, str]):
        """Set reversed currency mapping."""
        self._config["currency_mapping_reversed"] = dict(value)
    
    @property
    def fee_alias_to_currency_network_map(self) -> Dict[str, str]:
        """Get fee alias to currency network mapping."""
        return dict(self._config.get("fee_alias_to_currency_network_map", {}))
    
    @fee_alias_to_currency_network_map.setter
    def fee_alias_to_currency_network_map(self, value: Dict[str, str]):
        """Set fee alias to currency network mapping."""
        self._config["fee_alias_to_currency_network_map"] = dict(value) 