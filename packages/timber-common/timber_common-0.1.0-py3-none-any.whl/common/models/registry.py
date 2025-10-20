# timber/common/models/registry.py
"""
Model Registry for Dynamic Model Management

Provides centralized registration and retrieval of SQLAlchemy models.
Supports models defined in code or generated from configuration files.
"""

from typing import Dict, Type, Optional, List
from sqlalchemy.ext.declarative import DeclarativeMeta
import logging

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Singleton registry for SQLAlchemy models.
    
    Allows applications (Canopy, Grove) to register models dynamically
    without modifying Timber's core code.
    """
    
    _instance = None
    _models: Dict[str, Type[DeclarativeMeta]] = {}
    _model_configs: Dict[str, dict] = {}
    _session_types: Dict[str, Type[DeclarativeMeta]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        logger.info("Model Registry initialized")
    
    def register_model(
        self, 
        model_class: Type[DeclarativeMeta],
        config: Optional[dict] = None,
        force: bool = False
    ) -> None:
        """
        Register a SQLAlchemy model.
        
        Args:
            model_class: The SQLAlchemy model class
            config: Optional configuration dict for the model
            force: If True, overwrite existing registration
        
        Raises:
            ValueError: If model already registered and force=False
        """
        model_name = model_class.__name__
        
        if model_name in self._models and not force:
            raise ValueError(
                f"Model '{model_name}' already registered. "
                f"Use force=True to overwrite."
            )
        
        self._models[model_name] = model_class
        
        if config:
            self._model_configs[model_name] = config
        
        # If model has __session_type__, register it for session lookup
        if hasattr(model_class, '__session_type__'):
            session_type = getattr(model_class, '__session_type__')
            self._session_types[session_type] = model_class
            logger.debug(f"Registered session type '{session_type}' -> {model_name}")
        
        logger.info(f"Registered model: {model_name}")
    
    def get_model(self, model_name: str) -> Optional[Type[DeclarativeMeta]]:
        """
        Retrieve a registered model by name.
        
        Args:
            model_name: Name of the model class
        
        Returns:
            The model class or None if not found
        """
        return self._models.get(model_name)
    
    def get_session_model(self, session_type: str) -> Optional[Type[DeclarativeMeta]]:
        """
        Retrieve a session model by its session_type attribute.
        
        Args:
            session_type: The session type identifier (e.g., 'stock_research')
        
        Returns:
            The session model class or None if not found
        """
        return self._session_types.get(session_type)
    
    def get_model_config(self, model_name: str) -> Optional[dict]:
        """
        Retrieve configuration for a registered model.
        
        Args:
            model_name: Name of the model
        
        Returns:
            Configuration dict or None if not found
        """
        return self._model_configs.get(model_name)
    
    def list_models(self) -> List[str]:
        """Return list of all registered model names."""
        return list(self._models.keys())
    
    def list_session_types(self) -> List[str]:
        """Return list of all registered session types."""
        return list(self._session_types.keys())
    
    def unregister_model(self, model_name: str) -> bool:
        """
        Unregister a model.
        
        Args:
            model_name: Name of the model to unregister
        
        Returns:
            True if model was unregistered, False if not found
        """
        if model_name not in self._models:
            return False
        
        model_class = self._models[model_name]
        
        # Remove from session types if registered
        if hasattr(model_class, '__session_type__'):
            session_type = getattr(model_class, '__session_type__')
            self._session_types.pop(session_type, None)
        
        # Remove from main registry
        self._models.pop(model_name)
        self._model_configs.pop(model_name, None)
        
        logger.info(f"Unregistered model: {model_name}")
        return True
    
    def clear(self) -> None:
        """Clear all registered models. Use with caution!"""
        self._models.clear()
        self._model_configs.clear()
        self._session_types.clear()
        logger.warning("Model registry cleared")
    
    def has_model(self, model_name: str) -> bool:
        """Check if a model is registered."""
        return model_name in self._models
    
    def get_models_by_tablename(self, table_name: str) -> List[Type[DeclarativeMeta]]:
        """
        Find models by their table name.
        
        Args:
            table_name: The __tablename__ to search for
        
        Returns:
            List of model classes with matching table name
        """
        return [
            model_class 
            for model_class in self._models.values()
            if hasattr(model_class, '__tablename__') 
            and model_class.__tablename__ == table_name
        ]


# Singleton instance
model_registry = ModelRegistry()


# Convenience functions
def register_model(model_class: Type[DeclarativeMeta], config: Optional[dict] = None) -> None:
    """Convenience function to register a model."""
    model_registry.register_model(model_class, config)


def get_model(model_name: str) -> Optional[Type[DeclarativeMeta]]:
    """Convenience function to retrieve a model."""
    return model_registry.get_model(model_name)


def get_session_model(session_type: str) -> Optional[Type[DeclarativeMeta]]:
    """Convenience function to retrieve a session model by type."""
    return model_registry.get_session_model(session_type)