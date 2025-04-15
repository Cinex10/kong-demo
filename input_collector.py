#!/usr/bin/env python3
"""
User Input Collector for Kong Demo Generator

This module handles the interactive collection of user inputs for Kong configuration.
"""

from typing import Tuple, List, Dict, Any, Optional, Union
from config_manager import ConfigurationManager

class UserInputCollector:
    """Collects user input for Kong configuration setup"""
    
    # Available business types for mock APIs
    BUSINESS_TYPES = {
        "1": "generic",
        "2": "insurance",
        "3": "insurance-policy",
        "4": "insurance-claims",
        "5": "ecommerce",
        "6": "ecommerce-product",
        "7": "ecommerce-order",
        "8": "health-insurance",
        "9": "auto-insurance"
    }
    
    # Available Kong features
    KONG_FEATURES = [
        "key-auth",
        "jwt",
        "oauth2",
        "basic-auth",
        "rate-limiting",
        "response-transformer",
        "request-transformer",
        "http-log",
        "cors",
        "proxy-cache",
        "ip-restriction",
        "request-size-limiting",
        "acl",
        "bot-detection"
    ]
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None) -> None:
        """Initialize the input collector with a configuration manager"""
        self.config_manager = config_manager or ConfigurationManager()
        self.business_type = "generic"
        self.business_params = {}
        self.kong_features = []
        self.api_specification = None
        
    def collect_project_info(self) -> str:
        """Collect basic project information"""
        print("Kong Demo Generator - Interactive Setup")
        print("=======================================")
        
        project_name = input("Project name: ")
        return project_name
    
    def collect_business_info(self) -> Tuple[str, Dict[str, Any]]:
        """Collect business domain information"""
        print("\nBusiness Domain Selection")
        print("-------------------------")
        print("Select a business domain for your API:")
        
        for key, value in self.BUSINESS_TYPES.items():
            print(f"{key}. {value}")
            
        while True:
            choice = input("Choose a business domain (default: 1): ") or "1"
            if choice in self.BUSINESS_TYPES:
                business_type = self.BUSINESS_TYPES[choice]
                break
            print("Invalid choice. Please try again.")
        
        business_params: Dict[str, Any] = {}
        
        # Collect additional parameters based on business type
        if "insurance" in business_type:
            # Insurance-specific parameters
            policy_types = ["auto", "health", "home", "life", "travel"]
            print("\nSelect insurance policy type:")
            for i, policy_type in enumerate(policy_types, 1):
                print(f"{i}. {policy_type}")
                
            policy_choice = self._get_int_input("Choose a policy type (1-5, default: 1): ", 1)
            business_params["policy_type"] = policy_types[policy_choice - 1]
            
        elif "ecommerce" in business_type:
            # E-commerce-specific parameters
            if "product" in business_type:
                product_types = ["electronics", "clothing", "groceries", "furniture", "books"]
                print("\nSelect product type:")
                for i, product_type in enumerate(product_types, 1):
                    print(f"{i}. {product_type}")
                    
                product_choice = self._get_int_input("Choose a product type (1-5, default: 1): ", 1)
                business_params["product_type"] = product_types[product_choice - 1]
        
        self.business_type = business_type
        self.business_params = business_params
        
        return business_type, business_params
    
    def collect_kong_features(self) -> List[str]:
        """Collect Kong features to include"""
        print("\nKong Features Selection")
        print("----------------------")
        print("Select Kong Gateway features to include:")
        
        for i, feature in enumerate(self.KONG_FEATURES, 1):
            print(f"{i}. {feature}")
            
        selected_features = self._collect_multiple_choice(
            "Select features to include (comma-separated numbers):",
            self.KONG_FEATURES
        )
        
        self.kong_features = selected_features
        
        return selected_features
    
    def collect_services(self) -> None:
        """Collect information about backend services - now uses pre-generated API spec"""
        print("\nServices are being configured based on API specification")
        print("--------------------------------------------------------")
        
        # Store service names to avoid duplicates
        added_services = set()
        
        # If API specification is available, use it
        if self.api_specification and "services" in self.api_specification:
            for service_spec in self.api_specification["services"]:
                service_name = service_spec.get("name", "")
                
                # Skip if service already added
                if service_name in added_services:
                    continue
                    
                service_url = service_spec.get("url", f"http://{service_name}:8080")
                
                print(f"Adding service: {service_name} ({service_url})")
                
                # Add service to configuration
                service_name = self.config_manager.add_service(service_name, service_url)
                added_services.add(service_name)
                
                # Store business type in service metadata
                service = next((s for s in self.config_manager.config["services"] if s["name"] == service_name), None)
                if service:
                    if "metadata" not in service:
                        service["metadata"] = {}
                    service["metadata"]["business_type"] = self.business_type
                    service["metadata"]["business_params"] = self.business_params
                    service["metadata"]["specification"] = service_spec
                
                # Add routes for this service
                if "routes" in service_spec:
                    for route_spec in service_spec["routes"]:
                        route_path = route_spec.get("path", f"/{service_name}")
                        route_name = route_spec.get("name", f"{service_name}-route")
                        
                        print(f"  Adding route: {route_path} ({route_name})")
                        
                        # Add route to configuration
                        self.config_manager.add_route(service_name, [route_path], route_name)
        else:
            # Fallback to manual entry if no API specification
            print("No API specification available. Falling back to manual configuration.")
            self._collect_services_manually()
    
    def _collect_services_manually(self) -> None:
        """Legacy method to collect services manually"""
        num_services = self._get_int_input("Number of backend services to configure: ", 1)
        
        for i in range(num_services):
            print(f"\nService {i+1}:")
            
            # Get service name and URL
            service_name = input("Service name: ")
            service_url = input("Service URL (e.g., http://my-api:8080): ")
            
            if not service_name:
                service_name = f"service_{i+1}"
                print(f"Using default service name: {service_name}")
            
            # Add service to configuration
            service_name = self.config_manager.add_service(service_name, service_url)
            
            # Store business type in service metadata
            service = next((s for s in self.config_manager.config["services"] if s["name"] == service_name), None)
            if service:
                if "metadata" not in service:
                    service["metadata"] = {}
                service["metadata"]["business_type"] = self.business_type
                service["metadata"]["business_params"] = self.business_params
            
            # Collect routes for this service
            self._collect_routes_for_service(service_name)
    
    def collect_plugins(self) -> None:
        """Configure plugins based on selected features"""
        print("\nConfiguring Kong Plugins")
        print("----------------------")
        
        # Add plugins based on selected features
        for feature in self.kong_features:
            feature_lower = feature.lower()
            
            # Authentication plugins
            if feature_lower in ["key-auth", "jwt", "oauth2", "basic-auth"]:
                print(f"Adding authentication plugin: {feature_lower}")
                self.config_manager.add_plugin(feature_lower)
                
                # Add a demo consumer with this auth type
                username = "demo-user"
                self.config_manager.add_consumer(username, feature_lower)
                
            # Rate limiting
            elif feature_lower == "rate-limiting":
                limit_per_minute = self._get_int_input("Requests per minute (default: 60): ", 60)
                
                print(f"Adding rate limiting plugin: {limit_per_minute} requests per minute")
                self.config_manager.add_plugin("rate-limiting", {
                    "minute": limit_per_minute,
                    "policy": "local"
                })
                
            # Response transformations
            elif feature_lower == "response-transformer":
                print("Adding response transformer plugin")
                self.config_manager.add_plugin("response-transformer", {
                    "add": {
                        "headers": ["x-kong-gateway: true"]
                    }
                })
                
            # Request transformations
            elif feature_lower == "request-transformer":
                print("Adding request transformer plugin")
                self.config_manager.add_plugin("request-transformer", {
                    "add": {
                        "headers": ["x-kong-request: true"]
                    }
                })
                
            # Logging
            elif feature_lower == "http-log":
                log_endpoint = input("Log endpoint URL (default: http://logger:3000/log): ") or "http://logger:3000/log"
                
                print(f"Adding HTTP logging plugin to endpoint: {log_endpoint}")
                self.config_manager.add_plugin("http-log", {
                    "http_endpoint": log_endpoint,
                    "method": "POST",
                    "timeout": 10000,
                    "keepalive": 60000
                })
                
            # CORS
            elif feature_lower == "cors":
                print("Adding CORS plugin")
                self.config_manager.add_plugin("cors", {
                    "origins": ["*"],
                    "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                    "headers": ["Content-Type", "Authorization"],
                    "exposed_headers": ["X-Auth-Token"],
                    "max_age": 3600
                })
    
    def _collect_multiple_choice(self, prompt: str, options: List[str]) -> List[str]:
        """Collect multiple choice options from a list"""
        print("\n" + prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
            
        choice = input("Enter comma-separated numbers (default: 1): ") or "1"
        selected_indices = []
        
        try:
            selected_indices = [int(idx.strip()) for idx in choice.split(",")]
            # Validate indices
            selected_indices = [idx for idx in selected_indices if 1 <= idx <= len(options)]
            if not selected_indices:
                selected_indices = [1]  # Default to first option
        except ValueError:
            print("Invalid input, using default selection.")
            selected_indices = [1]
            
        return [options[idx - 1] for idx in selected_indices]
                
    def _collect_routes_for_service(self, service_name: str) -> None:
        """Collect route information for a specific service"""
        num_routes = self._get_int_input(f"Number of routes for {service_name}: ", 1)
        
        for j in range(num_routes):
            route_path = input(f"Route {j+1} path (e.g., /api/users): ")
            
            if not route_path:
                route_path = f"/{service_name}"
                print(f"Using default route path: {route_path}")
                
            # Add route to configuration
            self.config_manager.add_route(service_name, [route_path])
    
    def _get_int_input(self, prompt: str, default: Optional[int] = None) -> int:
        """Get integer input from user with validation"""
        while True:
            try:
                value = input(prompt)
                if not value and default is not None:
                    return default
                return int(value)
            except ValueError:
                print("Please enter a valid number.")
    
    def set_api_specification(self, specification: Dict[str, Any]) -> None:
        """Set the API specification to use for service configuration"""
        self.api_specification = specification
    
    def collect_all(self) -> Tuple[str, ConfigurationManager]:
        """Collect all user input and return the final configuration"""
        # First collect project name
        project_name = self.collect_project_info()
        
        # Then collect business domain info
        self.collect_business_info()
        
        # Collect Kong features
        self.collect_kong_features()
        
        # At this point, we would generate API specification
        # This will be done in the DemoProjectGenerator class
        
        # Collect services (using API spec if available)
        self.collect_services()
        
        # Collect plugins based on features
        self.collect_plugins()
        
        # Return the project name and config manager
        return project_name, self.config_manager 