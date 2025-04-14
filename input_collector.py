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
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None) -> None:
        """Initialize the input collector with a configuration manager"""
        self.config_manager = config_manager or ConfigurationManager()
        
    def collect_project_info(self) -> str:
        """Collect basic project information"""
        print("Kong Demo Generator - Interactive Setup")
        print("=======================================")
        
        project_name = input("Project name: ")
        return project_name
    
    def collect_services(self) -> None:
        """Collect information about backend services"""
        print("\nBackend Services Configuration")
        print("------------------------------")
        
        num_services = self._get_int_input("Number of backend services to configure: ", 1)
        
        for i in range(num_services):
            print(f"\nService {i+1}:")
            
            # Get service name and URL
            service_name = input("Service name: ")
            service_url = input("Service URL (e.g., http://my-api:8080): ")
            
            if not service_name:
                service_name = f"service_{i+1}"
                print(f"Using default service name: {service_name}")
            
            # Collect business type for mock API generation
            business_type, business_params = self._collect_business_type(service_name)
            
            # Add service to configuration
            service_name = self.config_manager.add_service(service_name, service_url)
            
            # Store business type and parameters in service metadata
            service = next((s for s in self.config_manager.config["services"] if s["name"] == service_name), None)
            if service:
                if "metadata" not in service:
                    service["metadata"] = {}
                service["metadata"]["business_type"] = business_type
                service["metadata"]["business_params"] = business_params
            
            # Collect routes for this service
            self._collect_routes_for_service(service_name)
    
    def _collect_business_type(self, service_name: str) -> Tuple[str, Dict[str, Any]]:
        """Collect business type and parameters for mock API generation"""
        print("\nBusiness Logic Type for Mock API Generation")
        print("------------------------------------------")
        print("Select a business type for the mock API:")
        
        for key, value in self.BUSINESS_TYPES.items():
            print(f"{key}. {value}")
            
        while True:
            choice = input("Choose a business type (default: 1): ") or "1"
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
            
            # Select features
            features = ["basic", "premium-calculation", "risk-assessment", "document-management", "claims-integration"]
            selected_features = self._collect_multiple_choice(
                "Select features to include (comma-separated numbers):",
                features
            )
            business_params["features"] = selected_features
            
        elif "ecommerce" in business_type:
            # E-commerce-specific parameters
            if "product" in business_type:
                product_types = ["electronics", "clothing", "groceries", "furniture", "books"]
                print("\nSelect product type:")
                for i, product_type in enumerate(product_types, 1):
                    print(f"{i}. {product_type}")
                    
                product_choice = self._get_int_input("Choose a product type (1-5, default: 1): ", 1)
                business_params["product_type"] = product_types[product_choice - 1]
            
            # Select features
            features = ["basic", "search", "recommendations", "inventory-management", "user-accounts", "reviews", "ratings"]
            selected_features = self._collect_multiple_choice(
                "Select features to include (comma-separated numbers):",
                features
            )
            business_params["features"] = selected_features
        else:
            # Generic business types
            # Select generic features
            features = ["basic", "advanced-validation", "authentication", "pagination", "filtering", "sorting", "caching"]
            selected_features = self._collect_multiple_choice(
                "Select features to include (comma-separated numbers):",
                features
            )
            business_params["features"] = selected_features
        
        return business_type, business_params
    
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
    
    def collect_plugins(self) -> None:
        """Collect information about plugins and security settings"""
        print("\nSecurity and Plugins")
        print("-------------------")
        
        # Authentication
        auth_plugin = self._collect_auth_plugin()
        
        # Rate limiting
        self._collect_rate_limiting()
        
        # Logging
        self._collect_logging()
        
        # CORS
        self._collect_cors()
        
    def _collect_auth_plugin(self) -> Optional[Dict[str, Any]]:
        """Collect authentication plugin configuration"""
        auth_types: Dict[str, str] = {
            "1": "key-auth",
            "2": "jwt",
            "3": "oauth2",
            "4": "basic-auth",
            "5": "none"
        }
        
        print("Authentication type:")
        for k, v in auth_types.items():
            print(f"{k}. {v}")
        
        while True:
            auth_choice = input("Choose authentication (1-5): ")
            if auth_choice in auth_types:
                break
            print("Invalid choice. Please choose a number between 1 and 5.")
            
        auth_type = auth_types[auth_choice]
        
        if auth_type != "none":
            auth_plugin = self.config_manager.add_plugin(auth_type)
            
            # Create a demo consumer with this auth type
            username = input("Consumer username (default: demo-user): ") or "demo-user"
            self.config_manager.add_consumer(username, auth_type)
            
            return auth_plugin
        
        return None
    
    def _collect_rate_limiting(self) -> None:
        """Collect rate limiting configuration"""
        rate_limit = input("Enable rate limiting? (y/n): ")
        
        if rate_limit.lower() == 'y':
            limit_per_minute = self._get_int_input("Requests per minute (default: 60): ", 60)
            
            self.config_manager.add_plugin("rate-limiting", {
                "minute": limit_per_minute,
                "policy": "local"
            })
    
    def _collect_logging(self) -> None:
        """Collect logging configuration"""
        logging = input("Enable request/response logging? (y/n): ")
        
        if logging.lower() == 'y':
            log_endpoint = input("Log endpoint URL (default: http://logger:3000/log): ") or "http://logger:3000/log"
            
            self.config_manager.add_plugin("http-log", {
                "http_endpoint": log_endpoint,
                "method": "POST",
                "timeout": 10000,
                "keepalive": 60000
            })
    
    def _collect_cors(self) -> None:
        """Collect CORS configuration"""
        cors = input("Enable CORS? (y/n): ")
        
        if cors.lower() == 'y':
            origins = input("Allowed origins (comma-separated, default: *): ") or "*"
            origins_list = [origin.strip() for origin in origins.split(",")]
            
            self.config_manager.add_plugin("cors", {
                "origins": origins_list,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                "headers": ["Content-Type", "Authorization"],
                "exposed_headers": ["X-Auth-Token"],
                "max_age": 3600,
                "credentials": True
            })
    
    def _get_int_input(self, prompt: str, default: Optional[int] = None) -> int:
        """Get integer input with validation and default value"""
        while True:
            value = input(prompt)
            
            # Use default if empty
            if not value and default is not None:
                return default
                
            try:
                return int(value)
            except ValueError:
                print("Please enter a valid number.")
                
    def collect_all(self) -> Tuple[str, ConfigurationManager]:
        """Collect all configuration in one go"""
        project_name = self.collect_project_info()
        self.collect_services()
        self.collect_plugins()
        
        # Validate the final configuration
        self.config_manager.validate()
        
        return project_name, self.config_manager 