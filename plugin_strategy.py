#!/usr/bin/env python3
"""
Plugin Strategy Pattern for Kong Demo Generator

This module implements the Strategy pattern for Kong plugins
to make it easy to extend the system with new plugin types.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Type

class PluginStrategy(ABC):
    """Abstract base class for Kong plugin strategies"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the plugin"""
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get the configuration for the plugin"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the plugin to a dictionary suitable for Kong"""
        pass


class AuthPluginStrategy(PluginStrategy, ABC):
    """Base class for authentication plugins"""
    
    @abstractmethod
    def get_consumer_auth_config(self, consumer_username: str) -> Dict[str, Any]:
        """Get the consumer authentication configuration"""
        pass


class KeyAuthPlugin(AuthPluginStrategy):
    """Implementation of the key-auth plugin strategy"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with optional config"""
        self.config: Dict[str, Any] = config or {}
        
    def get_name(self) -> str:
        """Get the name of the plugin"""
        return "key-auth"
    
    def get_config(self) -> Dict[str, Any]:
        """Get the configuration for the plugin"""
        return self.config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the plugin to a dictionary suitable for Kong"""
        result: Dict[str, Any] = {"name": self.get_name()}
        if self.config:
            result["config"] = self.config
        return result
    
    def get_consumer_auth_config(self, consumer_username: str) -> Dict[str, Any]:
        """Get the consumer authentication configuration"""
        return {"key": f"demo-key-{consumer_username}"}


class JwtPlugin(AuthPluginStrategy):
    """Implementation of the JWT plugin strategy"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with optional config"""
        self.config: Dict[str, Any] = config or {}
        
    def get_name(self) -> str:
        """Get the name of the plugin"""
        return "jwt"
    
    def get_config(self) -> Dict[str, Any]:
        """Get the configuration for the plugin"""
        return self.config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the plugin to a dictionary suitable for Kong"""
        result: Dict[str, Any] = {"name": self.get_name()}
        if self.config:
            result["config"] = self.config
        return result
    
    def get_consumer_auth_config(self, consumer_username: str) -> Dict[str, Any]:
        """Get the consumer authentication configuration"""
        # A real implementation would generate proper JWT credentials
        return {
            "key": f"{consumer_username}-key",
            "secret": f"{consumer_username}-secret"
        }


class RateLimitingPlugin(PluginStrategy):
    """Implementation of the rate-limiting plugin strategy"""
    
    def __init__(self, limit_per_minute: int = 60, policy: str = "local") -> None:
        """Initialize with rate limit parameters"""
        self.limit_per_minute: int = limit_per_minute
        self.policy: str = policy
        
    def get_name(self) -> str:
        """Get the name of the plugin"""
        return "rate-limiting"
    
    def get_config(self) -> Dict[str, Any]:
        """Get the configuration for the plugin"""
        return {
            "minute": self.limit_per_minute,
            "policy": self.policy
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the plugin to a dictionary suitable for Kong"""
        return {
            "name": self.get_name(),
            "config": self.get_config()
        }


class CorsPlugin(PluginStrategy):
    """Implementation of the CORS plugin strategy"""
    
    def __init__(self, origins: Optional[List[str]] = None, 
                methods: Optional[List[str]] = None, 
                headers: Optional[List[str]] = None) -> None:
        """Initialize with CORS parameters"""
        self.origins: List[str] = origins or ["*"]
        self.methods: List[str] = methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.headers: List[str] = headers or ["Content-Type", "Authorization"]
        
    def get_name(self) -> str:
        """Get the name of the plugin"""
        return "cors"
    
    def get_config(self) -> Dict[str, Any]:
        """Get the configuration for the plugin"""
        return {
            "origins": self.origins,
            "methods": self.methods,
            "headers": self.headers,
            "exposed_headers": ["X-Auth-Token"],
            "max_age": 3600,
            "credentials": True
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the plugin to a dictionary suitable for Kong"""
        return {
            "name": self.get_name(),
            "config": self.get_config()
        }


class HttpLogPlugin(PluginStrategy):
    """Implementation of the HTTP log plugin strategy"""
    
    def __init__(self, http_endpoint: str = "http://logger:3000/log", method: str = "POST") -> None:
        """Initialize with HTTP log parameters"""
        self.http_endpoint: str = http_endpoint
        self.method: str = method
        
    def get_name(self) -> str:
        """Get the name of the plugin"""
        return "http-log"
    
    def get_config(self) -> Dict[str, Any]:
        """Get the configuration for the plugin"""
        return {
            "http_endpoint": self.http_endpoint,
            "method": self.method,
            "timeout": 10000,
            "keepalive": 60000
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the plugin to a dictionary suitable for Kong"""
        return {
            "name": self.get_name(),
            "config": self.get_config()
        }


class PluginFactory:
    """Factory for creating plugin strategies"""
    
    @staticmethod
    def create_auth_plugin(plugin_type: str, config: Optional[Dict[str, Any]] = None) -> Optional[AuthPluginStrategy]:
        """Create an authentication plugin strategy"""
        if plugin_type == "key-auth":
            return KeyAuthPlugin(config)
        elif plugin_type == "jwt":
            return JwtPlugin(config)
        elif plugin_type == "basic-auth":
            # Implement if needed
            pass
        elif plugin_type == "oauth2":
            # Implement if needed
            pass
        else:
            raise ValueError(f"Unsupported auth plugin type: {plugin_type}")
    
    @staticmethod
    def create_plugin(plugin_type: str, **kwargs: Any) -> PluginStrategy:
        """Create a plugin strategy"""
        if plugin_type == "rate-limiting":
            return RateLimitingPlugin(**kwargs)
        elif plugin_type == "cors":
            return CorsPlugin(**kwargs)
        elif plugin_type == "http-log":
            return HttpLogPlugin(**kwargs)
        elif plugin_type in ("key-auth", "jwt", "basic-auth", "oauth2"):
            auth_plugin = PluginFactory.create_auth_plugin(plugin_type, kwargs.get("config"))
            if auth_plugin is None:
                raise ValueError(f"Failed to create auth plugin: {plugin_type}")
            return auth_plugin
        else:
            raise ValueError(f"Unsupported plugin type: {plugin_type}") 