#!/usr/bin/env python3
"""
Configuration Manager for Kong Demo Generator

This module handles the storage, validation, and management of Kong configuration.
"""

import json
import yaml
import random
from typing import Dict, List, Any, Optional, Union

class ConfigurationManager:
    """Manages Kong configuration data including validation and storage"""
    
    def __init__(self) -> None:
        """Initialize an empty Kong configuration structure"""
        self.config: Dict[str, List[Dict[str, Any]]] = {
            "services": [],
            "routes": [],
            "plugins": [],
            "consumers": []
        }
        
    def add_service(self, name: str, url: Optional[str]) -> str:
        """Add a service to the configuration"""
        if not name:
            name = f"default_service_{random.randint(1000, 9999)}"
        
        # Ensure service name follows Kong naming conventions
        name = name.replace('-', '_').lower()
        
        self.config["services"].append({
            "name": name,
            "url": url or f"http://{name}:8080"
        })
        
        return name
    
    def add_route(self, service_name: str, paths: List[str], name: Optional[str] = None) -> str:
        """Add a route to the configuration"""
        if not service_name:
            # Find first available service
            if self.config["services"]:
                service_name = self.config["services"][0]["name"]
            else:
                service_name = f"default_service_{random.randint(1000, 9999)}"
                
        # Ensure service name follows Kong naming conventions
        service_name = service_name.replace('-', '_').lower()
        
        if not name:
            route_index = sum(1 for route in self.config["routes"] 
                             if route["service_name"] == service_name) + 1
            name = f"{service_name}-route-{route_index}"
            
        self.config["routes"].append({
            "service_name": service_name,
            "paths": paths,
            "name": name
        })
        
        return name
    
    def add_plugin(self, name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a plugin to the configuration"""
        plugin: Dict[str, Any] = {"name": name}
        if config:
            plugin["config"] = config
            
        self.config["plugins"].append(plugin)
        
        # Track authentication plugin separately for convenience
        if name in ["key-auth", "jwt", "oauth2", "basic-auth"]:
            self.config["auth_plugin"] = plugin
            
        return plugin
    
    def add_consumer(self, username: str, auth_type: Optional[str] = None) -> Dict[str, Any]:
        """Add a consumer to the configuration"""
        consumer: Dict[str, Any] = {"username": username}
        if auth_type:
            consumer["auth_type"] = auth_type
            
        self.config["consumers"].append(consumer)
        return consumer
    
    def validate(self) -> None:
        """Validate the configuration for consistency"""
        # Ensure all services have valid names
        for service in self.config["services"]:
            if not service["name"]:
                service["name"] = f"default_service_{random.randint(1000, 9999)}"
            service["name"] = service["name"].replace('-', '_').lower()
        
        # Ensure all routes reference valid services
        service_names = [s["name"] for s in self.config["services"]]
        for route in self.config["routes"]:
            if not route["service_name"] or route["service_name"] not in service_names:
                if service_names:
                    route["service_name"] = service_names[0]
                else:
                    # No services available, create a default one
                    default_name = f"default_service_{random.randint(1000, 9999)}"
                    self.add_service(default_name, None)
                    route["service_name"] = default_name
            
            route["service_name"] = route["service_name"].replace('-', '_').lower()
    
    def to_json(self) -> str:
        """Convert configuration to JSON string"""
        return json.dumps(self.config, indent=2)
    
    def to_yaml(self) -> str:
        """Convert configuration to YAML string"""
        return yaml.dump(self.config)
    
    def to_declarative_config(self) -> Dict[str, Any]:
        """Convert configuration to Kong declarative format"""
        declarative: Dict[str, Any] = {
            "_format_version": "3.0",
            "services": [],
            "routes": [],
            "plugins": [],
            "consumers": [],
            "consumer_groups": []
        }
        
        # Convert services
        for service in self.config["services"]:
            declarative["services"].append({
                "name": service["name"],
                "url": service["url"]
            })
            
        # Convert routes
        for route in self.config["routes"]:
            route_copy = route.copy()
            service_name = route_copy.pop("service_name")
            declarative["routes"].append({
                **route_copy,
                "service": {"name": service_name}
            })
            
        # Convert plugins
        for plugin in self.config["plugins"]:
            declarative["plugins"].append(plugin)
            
        # Convert consumers
        for consumer in self.config["consumers"]:
            consumer_copy = consumer.copy()
            auth_type = consumer_copy.pop("auth_type", None)
            declarative["consumers"].append({
                "username": consumer["username"]
            })
            
            # Add auth credentials if needed
            if auth_type == "key-auth":
                # In a real scenario, we'd generate secure random keys
                if "keyauth_credentials" not in declarative:
                    declarative["keyauth_credentials"] = []
                    
                declarative["keyauth_credentials"].append({
                    "consumer": {"username": consumer["username"]},
                    "key": f"demo-key-{consumer['username']}"
                })
                
        return declarative
    
    def load_from_json(self, json_string: str) -> None:
        """Load configuration from JSON string"""
        self.config = json.loads(json_string)
        self.validate()
        
    def load_from_yaml(self, yaml_string: str) -> None:
        """Load configuration from YAML string"""
        self.config = yaml.safe_load(yaml_string)
        self.validate()
        
    def load_from_file(self, file_path: str) -> None:
        """Load configuration from a file"""
        with open(file_path, 'r') as f:
            if file_path.endswith('.json'):
                self.config = json.load(f)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                self.config = yaml.safe_load(f)
            else:
                raise ValueError("Config file must be JSON or YAML")
        
        self.validate() 