#!/usr/bin/env python3
"""
Kong Admin API Client for Kong Demo Generator

This module handles all interactions with the Kong Admin API.
"""

import requests
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod

from config_manager import ConfigurationManager

class KongAdminInterface(ABC):
    """Abstract interface for Kong Admin API operations"""
    
    @abstractmethod
    def create_service(self, name: str, url: str) -> Dict[str, Any]:
        """Create a service in Kong"""
        pass
    
    @abstractmethod
    def create_route(self, service_name: str, paths: List[str], name: Optional[str] = None) -> Dict[str, Any]:
        """Create a route for a service in Kong"""
        pass
    
    @abstractmethod
    def create_plugin(self, name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a plugin in Kong"""
        pass
    
    @abstractmethod
    def create_consumer(self, username: str) -> Dict[str, Any]:
        """Create a consumer in Kong"""
        pass
    
    @abstractmethod
    def add_consumer_auth(self, username: str, auth_type: str, credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add authentication credentials for a consumer"""
        pass
    
class KongAdminClient(KongAdminInterface):
    """Client for interacting with the Kong Admin API"""
    
    def __init__(self, admin_url: str) -> None:
        """Initialize with the Kong Admin API URL"""
        self.admin_url: str = admin_url.rstrip('/')
        
    def create_service(self, name: str, url: str) -> Dict[str, Any]:
        """Create a service in Kong"""
        response = requests.post(
            f"{self.admin_url}/services",
            data={"name": name, "url": url}
        )
        
        if response.status_code not in (200, 201):
            raise Exception(f"Failed to create service: {response.text}")
            
        return response.json()
    
    def create_route(self, service_name: str, paths: List[str], name: Optional[str] = None) -> Dict[str, Any]:
        """Create a route for a service in Kong"""
        data: Dict[str, Any] = {"paths": paths}
        if name:
            data["name"] = name
            
        response = requests.post(
            f"{self.admin_url}/services/{service_name}/routes",
            json=data
        )
        
        if response.status_code not in (200, 201):
            raise Exception(f"Failed to create route: {response.text}")
            
        return response.json()
    
    def create_plugin(self, name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a plugin in Kong"""
        data: Dict[str, Any] = {"name": name}
        if config:
            data["config"] = config
            
        response = requests.post(
            f"{self.admin_url}/plugins",
            json=data
        )
        
        if response.status_code not in (200, 201):
            raise Exception(f"Failed to create plugin: {response.text}")
            
        return response.json()
    
    def create_consumer(self, username: str) -> Dict[str, Any]:
        """Create a consumer in Kong"""
        response = requests.post(
            f"{self.admin_url}/consumers",
            data={"username": username}
        )
        
        if response.status_code not in (200, 201):
            raise Exception(f"Failed to create consumer: {response.text}")
            
        return response.json()
    
    def add_consumer_auth(self, username: str, auth_type: str, credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add authentication credentials for a consumer"""
        if auth_type == "key-auth":
            response = requests.post(
                f"{self.admin_url}/consumers/{username}/key-auth",
                data=credentials or {"key": f"demo-key-{username}"}
            )
            
            if response.status_code not in (200, 201):
                raise Exception(f"Failed to add consumer auth: {response.text}")
                
            return response.json()
        elif auth_type == "jwt":
            # Implement JWT auth if needed
            pass
        else:
            raise ValueError(f"Unsupported auth type: {auth_type}")
    
    def deploy_configuration(self, config: ConfigurationManager) -> Dict[str, List[Dict[str, Any]]]:
        """Deploy a complete configuration to Kong"""
        results: Dict[str, List[Dict[str, Any]]] = {
            "services": [],
            "routes": [],
            "plugins": [],
            "consumers": []
        }
        
        # Create services
        for service in config.config["services"]:
            result = self.create_service(service["name"], service["url"])
            results["services"].append(result)
            
        # Create routes
        for route in config.config["routes"]:
            result = self.create_route(
                route["service_name"], 
                route["paths"],
                route.get("name")
            )
            results["routes"].append(result)
            
        # Create plugins
        for plugin in config.config["plugins"]:
            result = self.create_plugin(
                plugin["name"],
                plugin.get("config")
            )
            results["plugins"].append(result)
            
        # Create consumers and their auth
        for consumer in config.config["consumers"]:
            result = self.create_consumer(consumer["username"])
            results["consumers"].append(result)
            
            # Add authentication if needed
            if "auth_type" in consumer and consumer["auth_type"] != "none":
                self.add_consumer_auth(
                    consumer["username"],
                    consumer["auth_type"]
                )
                
        return results

class MockKongAdminClient(KongAdminInterface):
    """Mock implementation of Kong Admin client for testing"""
    
    def __init__(self) -> None:
        """Initialize the mock client"""
        self.services: List[Dict[str, Any]] = []
        self.routes: List[Dict[str, Any]] = []
        self.plugins: List[Dict[str, Any]] = []
        self.consumers: List[Dict[str, Any]] = []
        self.consumer_auths: List[Dict[str, Any]] = []
        
    def create_service(self, name: str, url: str) -> Dict[str, Any]:
        """Create a service in the mock database"""
        service: Dict[str, Any] = {"name": name, "url": url, "id": f"service-{len(self.services)+1}"}
        self.services.append(service)
        return service
    
    def create_route(self, service_name: str, paths: List[str], name: Optional[str] = None) -> Dict[str, Any]:
        """Create a route in the mock database"""
        route: Dict[str, Any] = {
            "service": {"name": service_name},
            "paths": paths,
            "id": f"route-{len(self.routes)+1}"
        }
        if name:
            route["name"] = name
            
        self.routes.append(route)
        return route
    
    def create_plugin(self, name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a plugin in the mock database"""
        plugin: Dict[str, Any] = {"name": name, "id": f"plugin-{len(self.plugins)+1}"}
        if config:
            plugin["config"] = config
            
        self.plugins.append(plugin)
        return plugin
    
    def create_consumer(self, username: str) -> Dict[str, Any]:
        """Create a consumer in the mock database"""
        consumer: Dict[str, Any] = {"username": username, "id": f"consumer-{len(self.consumers)+1}"}
        self.consumers.append(consumer)
        return consumer
    
    def add_consumer_auth(self, username: str, auth_type: str, credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add authentication credentials for a consumer in the mock database"""
        auth: Dict[str, Any] = {
            "consumer": {"username": username},
            "type": auth_type,
            "id": f"auth-{len(self.consumer_auths)+1}"
        }
        
        if credentials:
            auth["credentials"] = credentials
        elif auth_type == "key-auth":
            auth["credentials"] = {"key": f"demo-key-{username}"}
            
        self.consumer_auths.append(auth)
        return auth 