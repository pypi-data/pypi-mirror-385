"""
Component registry for initializing and managing orchestrator dependencies.

Phase 2 SOLID Refactoring: Extracted from MarketDataOrchestrator to follow SRP.
This class is responsible ONLY for creating and initializing components.
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Optional, Tuple

if TYPE_CHECKING:
    from ..settings import OrchestratorSettings

log = logging.getLogger(__name__)


class ComponentRegistry:
    """
    Creates and initializes orchestrator components.
    
    Responsibilities (SRP):
    - Create runtime, provider, and feedback components
    - Initialize components with proper configuration
    - Check for required dependencies
    
    Does NOT:
    - Start/stop components (that's LifecycleManager)
    - Handle control operations (that's ControlPlaneService)
    - Aggregate status (that's StatusAggregator)
    """
    
    def __init__(self, settings: OrchestratorSettings):
        """
        Initialize component registry.
        
        Args:
            settings: Orchestrator settings
        """
        self.settings = settings
        self._initialized = False
    
    def initialize(self) -> Tuple[Any, Any, Optional[Any], Optional[Any], Optional[Any]]:
        """
        Initialize all orchestrator components.
        
        Phase 10.1: Now also initializes PulseObserver.
        
        Returns:
            Tuple of (runtime, provider, feedback_bus, feedback_subscriber, pulse_observer)
            
        Raises:
            RuntimeError: If required dependencies are missing
        """
        if self._initialized:
            log.warning("Components already initialized")
            return self._get_components()
        
        log.info("Initializing orchestrator components...")
        
        # Import dependencies at module level for testability
        # Note: These may be monkeypatched by tests
        import sys
        
        # Get module-level attributes (allows monkeypatching by tests)
        current_module = sys.modules[__name__]
        UnifiedRuntime = getattr(current_module, 'UnifiedRuntime', None)
        FeedbackBus = getattr(current_module, 'FeedbackBus', None)
        IBKRProvider = getattr(current_module, 'IBKRProvider', None)
        
        # If not monkeypatched, try real imports
        if UnifiedRuntime is None:
            try:
                from market_data_pipeline.runtime import UnifiedRuntime
            except ImportError:
                raise RuntimeError("market-data-pipeline is not installed")
        
        if FeedbackBus is None and self.settings.feedback_enabled:
            try:
                from market_data_store import FeedbackBus
            except ImportError:
                raise RuntimeError("market-data-store is not installed")
        
        if IBKRProvider is None:
            try:
                from market_data_ibkr import IBKRProvider
            except ImportError:
                raise RuntimeError("market-data-ibkr is not installed")
        
        from ..feedback import FeedbackSubscriber
        
        # Initialize runtime with proper settings
        from market_data_pipeline.runtime.unified_runtime import UnifiedRuntimeSettings, RuntimeMode
        from market_data_pipeline.config import PipelineSettings
        
        # Create PipelineSettings for the classic mode
        pipeline_settings = PipelineSettings(
            ibkr_host=self.settings.provider_host,
            ibkr_port=self.settings.provider_port,
            ibkr_client_id=self.settings.provider_client_id,
            log_level=self.settings.log_level,
            log_format=self.settings.log_format
        )
        
        # Create UnifiedRuntimeSettings with classic mode and pipeline settings as dict
        runtime_settings = UnifiedRuntimeSettings(
            mode=RuntimeMode.CLASSIC,
            classic={'spec': pipeline_settings.model_dump()}
        )
        self._runtime = UnifiedRuntime(settings=runtime_settings)
        log.info(f"UnifiedRuntime initialized with classic mode")
        
        # Initialize feedback bus (no parameters needed)
        if self.settings.feedback_enabled and FeedbackBus:
            self._feedback_bus = FeedbackBus()
            self._feedback_subscriber = FeedbackSubscriber(self._feedback_bus)
            log.info(f"FeedbackBus initialized")
        else:
            self._feedback_bus = None
            self._feedback_subscriber = None
            if not self.settings.feedback_enabled:
                log.warning("Feedback bus disabled by configuration")
        
        # Initialize provider with proper settings
        from market_data_ibkr.settings import IBKRSettings
        provider_config = self.settings.get_provider_config()
        ibkr_settings = IBKRSettings(**provider_config)
        self._provider = IBKRProvider(settings=ibkr_settings)
        log.info(f"IBKRProvider initialized: {provider_config['host']}:{provider_config['port']}")
        
        # Phase 10.1: Initialize Pulse observer
        from ..pulse import PulseObserver, PulseConfig
        pulse_config = PulseConfig()
        if pulse_config.enabled:
            self._pulse_observer = PulseObserver(cfg=pulse_config)
            log.info(f"PulseObserver initialized: backend={pulse_config.backend}, track={pulse_config.track}")
        else:
            self._pulse_observer = None
            log.info("PulseObserver disabled by configuration")
        
        self._initialized = True
        log.info("✅ All components initialized successfully")
        
        return self._get_components()
    
    def _get_components(self) -> Tuple[Any, Any, Optional[Any], Optional[Any], Optional[Any]]:
        """
        Get initialized components.
        
        Phase 10.1: Now also returns PulseObserver.
        
        Returns:
            Tuple of (runtime, provider, feedback_bus, feedback_subscriber, pulse_observer)
        """
        if not self._initialized:
            raise RuntimeError("Components not initialized")
        
        return (
            self._runtime,
            self._provider,
            self._feedback_bus,
            self._feedback_subscriber,
            self._pulse_observer  # Phase 10.1
        )
    
    @property
    def runtime(self) -> Any:
        """Get runtime instance."""
        if not self._initialized:
            raise RuntimeError("Components not initialized")
        return self._runtime
    
    @property
    def provider(self) -> Any:
        """Get provider instance."""
        if not self._initialized:
            raise RuntimeError("Components not initialized")
        return self._provider
    
    @property
    def feedback_bus(self) -> Optional[Any]:
        """Get feedback bus instance."""
        if not self._initialized:
            raise RuntimeError("Components not initialized")
        return self._feedback_bus
    
    @property
    def feedback_subscriber(self) -> Optional[Any]:
        """Get feedback subscriber instance."""
        if not self._initialized:
            raise RuntimeError("Components not initialized")
        return self._feedback_subscriber
    
    @property
    def pulse_observer(self) -> Optional[Any]:
        """Get pulse observer instance. Phase 10.1."""
        if not self._initialized:
            raise RuntimeError("Components not initialized")
        return self._pulse_observer
    
    @property
    def is_initialized(self) -> bool:
        """Check if components are initialized."""
        return self._initialized


