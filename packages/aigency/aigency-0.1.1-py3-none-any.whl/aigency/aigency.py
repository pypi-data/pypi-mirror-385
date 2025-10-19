"""Aigency server application wrapper."""

import os
from typing import Optional

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv

from aigency.agents.generator import AgentA2AGenerator
from aigency.observability.observability import Observability
from aigency.utils.config_service import ConfigService
from aigency.utils.logger import Logger, get_logger

logger = get_logger()

class Aigency:
    """Encapsulates the Aigency server setup and startup logic."""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        host: str = "0.0.0.0",
        port: int = 8080,
        log_config: Optional[dict] = None
    ):
        """
        Initialize the Aigency server.
        
        Args:
            config_path: Path to agent config file. If None, looks for agent_config.yaml in current dir
            host: Server host address
            port: Server port
            log_config: Logger configuration dict
        """
        self.host = host
        self.port = port
        self.config_path = config_path or self._get_default_config_path()
        self.log_config = log_config or self._get_default_log_config()
        
        # Load environment variables
        load_dotenv()
        
        # Initialize logger
        logger.info("Aigency server initialized")
    
    def _get_default_config_path(self) -> str:
        """Get default config path relative to current directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "agent_config.yaml")
    
    def _get_default_log_config(self) -> dict:
        """Get default logging configuration."""
        return {
            "log_level": "DEBUG",
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "log_file": "app.log",
            "logger_name": "aigency",
        }
    
    def run(self) -> None:
        """Start the Aigency server."""
        try:
            # Load agent configuration
            config_service = ConfigService(config_file=self.config_path)
            agent_config = config_service.config

            #Include observality
            Observability(aigency_config=agent_config)
            
            # Create agent components
            agent = AgentA2AGenerator.create_agent(agent_config=agent_config)
            agent_card = AgentA2AGenerator.build_agent_card(agent_config=agent_config)
            executor = AgentA2AGenerator.build_executor(agent=agent, agent_card=agent_card)
            
            # Setup request handler and server
            request_handler = DefaultRequestHandler(
                agent_executor=executor,
                task_store=InMemoryTaskStore(),
            )
            server = A2AStarletteApplication(
                agent_card=agent_card,
                http_handler=request_handler,
            )
            
            logger.info(f"Server object created: {server}")
            logger.info("🛎️ Starting Aigency server...")
            
            # Start the server
            uvicorn.run(server.build(), host=self.host, port=self.port)
            
        except Exception as e:
            logger.error(f"An error occurred during server startup: {e}")
            raise


def open_aigency(
    config_path: Optional[str] = None,
    host: str = "0.0.0.0", 
    port: int = 8080,
    log_config: Optional[dict] = None
) -> None:
    """
    Convenience function to start an Aigency server with minimal setup.
    
    Args:
        config_path: Path to agent config file
        host: Server host address  
        port: Server port
        log_config: Logger configuration dict
    """
    server = Aigency(
        config_path=config_path,
        host=host,
        port=port,
        log_config=log_config
    )
    server.run()
