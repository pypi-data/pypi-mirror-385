"""
Data provider configuration settings.

Phase 3 SOLID Refactoring: Focused settings group for market data providers.
"""

from typing import Any, Dict
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderSettings(BaseSettings):
    """
    Market data provider configuration.
    
    Currently supports Interactive Brokers (IBKR) TWS/Gateway.
    """
    
    model_config = SettingsConfigDict(
        env_prefix="ORCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    provider_host: str = Field(
        default="127.0.0.1",
        description="IBKR TWS/Gateway host"
    )
    provider_port: int = Field(
        default=7497,
        description="IBKR TWS/Gateway port"
    )
    provider_client_id: int = Field(
        default=1,
        description="IBKR client ID"
    )
    
    def get_provider_config(self) -> Dict[str, Any]:
        """
        Extract provider-specific configuration for IBKRProvider.
        
        Returns:
            Dictionary with host, port, and client_id
        """
        return {
            "host": self.provider_host,
            "port": self.provider_port,
            "client_id": self.provider_client_id,
        }

