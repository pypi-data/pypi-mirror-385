"""Configuration management for market_data_core.

DEPRECATED: Use market_data_core.settings.CoreSettings instead.

This module is deprecated and will be removed in v2.0.
The new settings module uses Pydantic for validation and type safety.
"""

import os
import warnings
from typing import Any, Dict

warnings.warn(
    "market_data_core.config.Config is deprecated. "
    "Use market_data_core.settings.CoreSettings instead.",
    DeprecationWarning,
    stacklevel=2
)


class Config:
    """Configuration manager for market_data_core."""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Pipeline configuration (professional pipeline only)
        self._config.update({
            'pipeline_batch_size': int(os.getenv('PIPELINE_BATCH_SIZE', '500')),
            'pipeline_flush_ms': int(os.getenv('PIPELINE_FLUSH_MS', '1000')),
            'pipeline_pacing_burst': int(os.getenv('PIPELINE_PACING_BURST', '1000')),
            'pipeline_pacing_refill': int(os.getenv('PIPELINE_PACING_REFILL', '1000')),
        })
        
        # Database configuration
        self._config.update({
            'database_url': os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/market_data'),
            'database_pool_max': int(os.getenv('DATABASE_POOL_MAX', '10')),
        })
        
        # IBKR configuration
        self._config.update({
            'ibkr_host': os.getenv('IBKR_HOST', '127.0.0.1'),
            'ibkr_port': int(os.getenv('IBKR_PORT', '4001')),
            'ibkr_client_id': int(os.getenv('IBKR_CLIENT_ID', '1')),
        })
        
        # Telemetry configuration
        self._config.update({
            'telemetry_enabled': os.getenv('TELEMETRY_ENABLED', 'true').lower() == 'true',
            'metrics_port': int(os.getenv('METRICS_PORT', '8000')),
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
    
    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get pipeline-specific configuration."""
        return {
            'batch_size': self.get('pipeline_batch_size'),
            'flush_ms': self.get('pipeline_flush_ms'),
            'pacing_budget': (self.get('pipeline_pacing_burst'), self.get('pipeline_pacing_refill')),
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database-specific configuration."""
        return {
            'dsn': self.get('database_url'),
            'pool_max': self.get('database_pool_max'),
        }
    
    def get_ibkr_config(self) -> Dict[str, Any]:
        """Get IBKR-specific configuration."""
        return {
            'host': self.get('ibkr_host'),
            'port': self.get('ibkr_port'),
            'client_id': self.get('ibkr_client_id'),
        }


# Global configuration instance
config = Config()


def get_websocket_config() -> Dict[str, Any]:
    """Get WebSocket-specific configuration."""
    return {
        'max_connections': config.get('websocket_max_connections', 1000),
        'rate_limit_per_second': config.get('websocket_rate_limit', 100),
        'max_queue_size': config.get('websocket_queue_size', 1000),
        'max_messages_per_second': config.get('websocket_max_messages_per_second', 100),
    }


def get_options_config() -> Dict[str, Any]:
    """Get options-specific configuration."""
    return {
        'semaphore_size': config.get('options_semaphore_size', 5),
        'base_delay': config.get('options_base_delay', 0.1),
        'max_contracts': config.get('options_max_contracts', 50),
        'max_retries': config.get('options_max_retries', 3),
        'backoff_multiplier': config.get('options_backoff_multiplier', 1.5),
    }