"""
Main entry point for the Market Data Orchestrator.

Handles:
- Configuration loading
- Logging setup
- Orchestrator lifecycle management
- Graceful shutdown on SIGINT/SIGTERM
- Health/Metrics API server
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

import uvicorn
from .orchestrator import MarketDataOrchestrator
from .settings import OrchestratorSettings
from .health import build_app
from .logging_config import setup_logging
from .services.registry_monitor import init_registry_monitor, get_registry_monitor
from .services.schema_audit import init_schema_audit, get_schema_audit
from .pulse.config import PulseConfig

log = logging.getLogger(__name__)


class OrchestratorLauncher:
    """
    Manages the lifecycle of the orchestrator and API server.
    
    Handles graceful shutdown on SIGINT and SIGTERM signals.
    """
    
    def __init__(self, settings: Optional[OrchestratorSettings] = None):
        """
        Initialize the launcher.
        
        Args:
            settings: OrchestratorSettings instance, or None to load from environment
        """
        self.settings = settings or OrchestratorSettings()
        self.orchestrator: Optional[MarketDataOrchestrator] = None
        self.stop_event = asyncio.Event()
        self._shutdown_initiated = False
    
    def _setup_signal_handlers(self) -> None:
        """Configure signal handlers for graceful shutdown."""
        loop = asyncio.get_running_loop()
        
        def _signal_handler(signum: int, frame: Optional[any] = None) -> None:
            if self._shutdown_initiated:
                log.warning("Shutdown already in progress, ignoring signal")
                return
            
            signal_name = signal.Signals(signum).name
            log.info(f"Received signal {signal_name}, initiating graceful shutdown...")
            self._shutdown_initiated = True
            self.stop_event.set()
        
        # Register handlers for SIGINT (Ctrl+C) and SIGTERM
        if sys.platform != "win32":
            # Unix-like systems
            loop.add_signal_handler(signal.SIGINT, lambda: _signal_handler(signal.SIGINT))
            loop.add_signal_handler(signal.SIGTERM, lambda: _signal_handler(signal.SIGTERM))
        else:
            # Windows - use different approach
            signal.signal(signal.SIGINT, _signal_handler)
            signal.signal(signal.SIGTERM, _signal_handler)
    
    async def run(self) -> None:
        """
        Main run loop for the orchestrator.
        
        Flow:
        1. Setup logging
        2. Create orchestrator
        3. Start API server
        4. Start orchestrator
        5. Wait for shutdown signal
        6. Cleanup and exit
        """
        # Setup structured logging
        setup_logging(
            level=self.settings.log_level,
            log_format=self.settings.log_format
        )
        
        log.info("=" * 60)
        log.info("Market Data Orchestrator v0.8.0 - Phase 11.1")
        log.info("=" * 60)
        log.info(f"Runtime mode: {self.settings.runtime_mode}")
        log.info(f"Feedback enabled: {self.settings.feedback_enabled}")
        log.info(f"Autoscale enabled: {self.settings.autoscale_enabled}")
        log.info(f"Health API: http://{self.settings.health_host}:{self.settings.health_port}")
        log.info(f"Registry monitor: {self.settings.registry_monitor_enabled} ({self.settings.registry_url})")
        log.info(f"Schema audit: enabled (drift intelligence)")
        log.info("=" * 60)
        
        try:
            # Setup signal handlers
            self._setup_signal_handlers()
            
            # Create orchestrator
            self.orchestrator = MarketDataOrchestrator(self.settings)
            
            # Phase 11.0E: Initialize registry monitor
            registry_monitor = init_registry_monitor(
                registry_url=self.settings.registry_url,
                poll_interval=self.settings.registry_poll_interval,
                enabled=self.settings.registry_monitor_enabled
            )
            
            # Phase 11.1: Initialize schema audit service
            pulse_cfg = PulseConfig()
            schema_audit = init_schema_audit(cfg=pulse_cfg, enabled=pulse_cfg.enabled)
            
            # Build FastAPI app
            app = build_app(self.orchestrator)
            
            # Configure Uvicorn server
            config = uvicorn.Config(
                app,
                host=self.settings.health_host,
                port=self.settings.health_port,
                log_level=self.settings.log_level.lower(),
                access_log=False  # Use our structured logging instead
            )
            server = uvicorn.Server(config)
            
            # Start API server in background
            server_task = asyncio.create_task(server.serve())
            log.info("Health/Metrics API server starting...")
            
            # Give server time to start
            await asyncio.sleep(0.5)
            
            # Start orchestrator
            await self.orchestrator.start()
            
            # Phase 11.0E: Start registry monitor
            if registry_monitor and registry_monitor.enabled:
                await registry_monitor.start()
                log.info("Registry monitor started")
            
            # Phase 11.1: Start schema audit service
            if schema_audit and schema_audit.enabled:
                await schema_audit.start()
                log.info("Schema audit service started")
            
            # Wait for shutdown signal
            log.info("Orchestrator running. Press Ctrl+C to stop.")
            await self.stop_event.wait()
            
            # Shutdown sequence
            log.info("Starting shutdown sequence...")
            
            # Phase 11.1: Stop schema audit service
            if schema_audit:
                await schema_audit.stop()
                log.info("Schema audit service stopped")
            
            # Phase 11.0E: Stop registry monitor
            if registry_monitor:
                await registry_monitor.stop()
                log.info("Registry monitor stopped")
            
            # Stop orchestrator
            if self.orchestrator:
                await self.orchestrator.stop()
            
            # Stop API server
            log.info("Stopping API server...")
            server.should_exit = True
            await server_task
            
            log.info("✅ Shutdown complete")
            
        except KeyboardInterrupt:
            log.info("Interrupted by user")
            if self.orchestrator and self.orchestrator.is_running:
                await self.orchestrator.stop()
        except Exception as e:
            log.error(f"Fatal error in orchestrator: {e}", exc_info=True)
            if self.orchestrator and self.orchestrator.is_running:
                try:
                    await self.orchestrator.stop()
                except Exception as cleanup_error:
                    log.error(f"Error during cleanup: {cleanup_error}")
            sys.exit(1)


def main() -> None:
    """
    Main entry point for the orchestrator.
    
    Called when running: python -m market_data_orchestrator.launcher
    or via the CLI command: market-data-orchestrator
    """
    try:
        launcher = OrchestratorLauncher()
        asyncio.run(launcher.run())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

