#!/usr/bin/env python3
"""
Kong Configuration Generator from API Specification

This module generates Kong configuration based on an API specification.
"""

from typing import Dict, List, Any, Optional
from config_manager import ConfigurationManager

class KongConfigFromSpecGenerator:
    """Generates Kong configuration from API specifications"""
    
    def __init__(self, specification: Optional[Dict[str, Any]] = None):
        """
        Initialize the generator with an API specification
        
        Args:
            specification: API specification dictionary
        """
        self.specification = specification or {}
        
    def generate_kong_config(self, config_manager: Optional[ConfigurationManager] = None, features: Optional[List[str]] = None) -> ConfigurationManager:
        """
        Generate Kong configuration from API specification
        
        Args:
            config_manager: Optional existing ConfigurationManager to update
            features: List of Kong features to configure
            
        Returns:
            ConfigurationManager with updated configuration
        """
        # Create or use provided ConfigurationManager
        config = config_manager or ConfigurationManager()
        features = features or []
        
        # Generate services and routes from specification
        if "services" in self.specification:
            for service_spec in self.specification["services"]:
                service_name = service_spec.get("name", "")
                service_url = service_spec.get("url", f"http://{service_name}:8080")
                
                # Add service to configuration
                service_name = config.add_service(service_name, service_url)
                
                # Add routes for this service
                if "routes" in service_spec:
                    for route_spec in service_spec["routes"]:
                        route_path = route_spec.get("path", f"/{service_name}")
                        route_name = route_spec.get("name", f"{service_name}-route")
                        
                        # Add route to configuration
                        config.add_route(service_name, [route_path], route_name)
                        
        # Add specified Kong features as plugins
        self._add_feature_plugins(config, features)
        
        return config
    
    def _add_feature_plugins(self, config: ConfigurationManager, features: List[str]) -> None:
        """
        Add plugins to configuration based on feature list
        
        Args:
            config: ConfigurationManager to update
            features: List of Kong features to configure
        """
        for feature in features:
            feature_lower = feature.lower()
            
            # Authentication plugins
            if feature_lower in ["key-auth", "jwt", "oauth2", "basic-auth"]:
                config.add_plugin(feature_lower)
                
                # Add a demo consumer with this auth type
                username = "demo-user"
                config.add_consumer(username, feature_lower)
                
            # Rate limiting
            elif feature_lower == "rate-limiting":
                config.add_plugin("rate-limiting", {
                    "minute": 60,
                    "policy": "local"
                })
                
            # Response transformations
            elif feature_lower == "response-transformer":
                config.add_plugin("response-transformer", {
                    "add": {
                        "headers": ["x-kong-gateway: true"]
                    }
                })
                
            # Request transformations
            elif feature_lower == "request-transformer":
                config.add_plugin("request-transformer", {
                    "add": {
                        "headers": ["x-kong-request: true"]
                    }
                })
                
            # Logging
            elif feature_lower == "http-log" or feature_lower == "logging":
                config.add_plugin("http-log", {
                    "http_endpoint": "http://logger:3000/log",
                    "method": "POST",
                    "timeout": 10000,
                    "keepalive": 60000
                })
                
            # CORS
            elif feature_lower == "cors":
                config.add_plugin("cors", {
                    "origins": ["*"],
                    "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                    "headers": ["Content-Type", "Authorization"],
                    "exposed_headers": ["X-Auth-Token"],
                    "max_age": 3600
                })
                
            # Caching
            elif feature_lower == "proxy-cache" or feature_lower == "cache":
                config.add_plugin("proxy-cache", {
                    "strategy": "memory",
                    "content_type": ["application/json", "application/xml"],
                    "cache_ttl": 300,
                    "cache_control": True
                })
                
            # IP restriction
            elif feature_lower == "ip-restriction":
                config.add_plugin("ip-restriction", {
                    "allow": ["127.0.0.1/32"]
                })
                
            # Request size limiting
            elif feature_lower == "request-size-limiting":
                config.add_plugin("request-size-limiting", {
                    "allowed_payload_size": 10
                })
                
            # Request termination (for testing)
            elif feature_lower == "request-termination":
                # Add only on a test route, not globally
                if config.config["routes"]:
                    test_route = config.config["routes"][-1]["name"]
                    # Adding to specific route is complex, would need route ID
                    # For now just note this in config
                    config.config["termination_note"] = f"request-termination should be applied to route: {test_route}" 