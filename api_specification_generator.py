#!/usr/bin/env python3
"""
API Specification Generator for Kong Demo Generator

This module uses AI to generate API specifications based on business type and Kong features.
"""

import json
from typing import Dict, List, Any, Optional
from ai_model_client import AiModelClient, GroqAiModelClient

class ApiSpecificationGenerator:
    """Generates API specifications based on business type and Kong features"""
    
    def __init__(self, ai_client: Optional[AiModelClient] = None):
        """Initialize the API specification generator with an AI client"""
        self.ai_client = ai_client
        
    def generate_api_specification(self, business_type: str, features: List[str]) -> Dict[str, Any]:
        """
        Generate an API specification based on business type and features
        
        Args:
            business_type: The type of business (e.g., insurance, ecommerce)
            features: List of Kong features to include (e.g., auth, rate-limiting)
            
        Returns:
            Dictionary containing the API specification
        """
        if self.ai_client:
            # Use AI to generate the specification
            specification = self._generate_with_ai(business_type, features)
        else:
            # Fallback to a template-based approach
            specification = self._generate_from_templates(business_type, features)
            
        return specification
    
    def _generate_with_ai(self, business_type: str, features: List[str]) -> Dict[str, Any]:
        """
        Generate an API specification using AI
        
        Args:
            business_type: The type of business
            features: List of Kong features to include
            
        Returns:
            Dictionary containing the API specification
        """
        prompt = self._create_ai_prompt(business_type, features)
        
        # Generate specification using the AI model
        try:
            response = self.ai_client.generate_code(prompt)
            specification = self._extract_json_from_response(response, business_type)
            return specification
        except Exception as e:
            print(f"Error generating specification with AI: {str(e)}")
            return self._generate_from_templates(business_type, features)
    
    def _create_ai_prompt(self, business_type: str, features: List[str]) -> str:
        """Create a prompt for the AI model"""
        return f"""Generate a complete API specification for a {business_type} service that will be configured with Kong Gateway.

The specification should include the following components:
1. Services (backend APIs)
2. Routes (URL paths to the services)
3. Endpoints (HTTP methods and paths within each route)

The Kong Gateway will include these features: {', '.join(features)}

Return ONLY a valid JSON object with this structure:
{{
  "services": [
    {{
      "name": "service_name",
      "description": "Description of the service",
      "url": "http://service-name:8080",
      "routes": [
        {{
          "name": "route_name",
          "path": "/path",
          "endpoints": [
            {{
              "path": "/specific-resource",
              "method": "GET",
              "description": "Description of endpoint",
              "request_params": {{ ... }},
              "response_example": {{ ... }}
            }}
          ]
        }}
      ]
    }}
  ]
}}

Make sure the specification is practical and realistic for the {business_type} domain, with appropriate endpoints and data structures. Include at least 2-3 services with multiple endpoints for each. Ensure all JSON is properly formatted.
"""
    
    def _extract_json_from_response(self, response: str, business_type: str) -> Dict[str, Any]:
        """
        Extract JSON from the AI model response
        
        Args:
            response: The raw response from the AI model
            
        Returns:
            Parsed JSON data
        """
        # Try to extract a JSON object from the response
        try:
            # First, see if the entire response is valid JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Look for JSON within code blocks
            import re
            
            # Look for JSON within code blocks (```json ... ```)
            json_matches = re.findall(r'```(?:json)?\s*(.*?)```', response, re.DOTALL)
            
            if json_matches:
                # Try each match until we find valid JSON
                for match in json_matches:
                    try:
                        return json.loads(match.strip())
                    except json.JSONDecodeError:
                        continue
            
            # Look for any object-like structures with braces
            brace_matches = re.findall(r'(\{.*\})', response, re.DOTALL)
            
            if brace_matches:
                # Try each match until we find valid JSON
                for match in brace_matches:
                    try:
                        return json.loads(match.strip())
                    except json.JSONDecodeError:
                        continue
            
            # If we can't extract valid JSON, return a basic template
            print("Could not extract valid JSON from AI response. Using fallback template.")
            return self._generate_from_templates(business_type, ["basic"])
    
    def _generate_from_templates(self, business_type: str, features: List[str]) -> Dict[str, Any]:
        """
        Generate an API specification using predefined templates
        
        Args:
            business_type: The type of business
            features: List of Kong features to include
            
        Returns:
            Dictionary containing the API specification
        """
        # Basic template for different business types
        if "insurance" in business_type:
            return self._insurance_template(features)
        elif "ecommerce" in business_type:
            return self._ecommerce_template(features)
        else:
            return self._generic_template(features)
    
    def _generic_template(self, features: List[str]) -> Dict[str, Any]:
        """Generate a generic API template"""
        return {
            "services": [
                {
                    "name": "api_service",
                    "description": "Generic API Service",
                    "url": "http://api-service:8080",
                    "routes": [
                        {
                            "name": "api_route",
                            "path": "/api",
                            "endpoints": [
                                {
                                    "path": "/items",
                                    "method": "GET",
                                    "description": "List all items",
                                    "request_params": {},
                                    "response_example": {"items": [{"id": 1, "name": "Item 1"}]}
                                },
                                {
                                    "path": "/items/{id}",
                                    "method": "GET",
                                    "description": "Get a specific item",
                                    "request_params": {"id": "integer"},
                                    "response_example": {"id": 1, "name": "Item 1", "description": "Description"}
                                },
                                {
                                    "path": "/items",
                                    "method": "POST",
                                    "description": "Create a new item",
                                    "request_params": {"name": "string", "description": "string"},
                                    "response_example": {"id": 2, "name": "New Item", "description": "New Description"}
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    def _insurance_template(self, features: List[str]) -> Dict[str, Any]:
        """Generate an insurance API template"""
        return {
            "services": [
                {
                    "name": "policy_service",
                    "description": "Insurance Policy Service",
                    "url": "http://policy-service:8080",
                    "routes": [
                        {
                            "name": "policy_route",
                            "path": "/policies",
                            "endpoints": [
                                {
                                    "path": "/",
                                    "method": "GET",
                                    "description": "List all policies",
                                    "request_params": {},
                                    "response_example": {"policies": [{"id": "POL-001", "type": "auto", "status": "active"}]}
                                },
                                {
                                    "path": "/{id}",
                                    "method": "GET",
                                    "description": "Get a specific policy",
                                    "request_params": {"id": "string"},
                                    "response_example": {
                                        "id": "POL-001",
                                        "type": "auto",
                                        "status": "active",
                                        "customer_id": "CUS-123",
                                        "vehicle": {"make": "Toyota", "model": "Camry", "year": 2020}
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "claims_service",
                    "description": "Insurance Claims Service",
                    "url": "http://claims-service:8080",
                    "routes": [
                        {
                            "name": "claims_route",
                            "path": "/claims",
                            "endpoints": [
                                {
                                    "path": "/",
                                    "method": "GET",
                                    "description": "List all claims",
                                    "request_params": {"policy_id": "string (optional)"},
                                    "response_example": {"claims": [{"id": "CLM-001", "policy_id": "POL-001", "status": "pending"}]}
                                },
                                {
                                    "path": "/{id}",
                                    "method": "GET",
                                    "description": "Get a specific claim",
                                    "request_params": {"id": "string"},
                                    "response_example": {
                                        "id": "CLM-001",
                                        "policy_id": "POL-001",
                                        "status": "pending",
                                        "incident_date": "2023-06-15",
                                        "description": "Vehicle damage due to accident"
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    def _ecommerce_template(self, features: List[str]) -> Dict[str, Any]:
        """Generate an ecommerce API template"""
        return {
            "services": [
                {
                    "name": "product_service",
                    "description": "Product Catalog Service",
                    "url": "http://product-service:8080",
                    "routes": [
                        {
                            "name": "product_route",
                            "path": "/products",
                            "endpoints": [
                                {
                                    "path": "/",
                                    "method": "GET",
                                    "description": "List all products",
                                    "request_params": {"category": "string (optional)", "limit": "integer (optional)"},
                                    "response_example": {"products": [{"id": 1, "name": "Product 1", "price": 29.99}]}
                                },
                                {
                                    "path": "/{id}",
                                    "method": "GET",
                                    "description": "Get a specific product",
                                    "request_params": {"id": "integer"},
                                    "response_example": {
                                        "id": 1,
                                        "name": "Product 1",
                                        "price": 29.99,
                                        "description": "Product description",
                                        "category": "electronics",
                                        "stock": 100
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "order_service",
                    "description": "Order Management Service",
                    "url": "http://order-service:8080",
                    "routes": [
                        {
                            "name": "order_route",
                            "path": "/orders",
                            "endpoints": [
                                {
                                    "path": "/",
                                    "method": "GET",
                                    "description": "List all orders",
                                    "request_params": {"customer_id": "string (optional)"},
                                    "response_example": {"orders": [{"id": "ORD-001", "status": "shipped", "total": 59.98}]}
                                },
                                {
                                    "path": "/{id}",
                                    "method": "GET",
                                    "description": "Get a specific order",
                                    "request_params": {"id": "string"},
                                    "response_example": {
                                        "id": "ORD-001",
                                        "customer_id": "CUS-123",
                                        "status": "shipped",
                                        "total": 59.98,
                                        "items": [
                                            {"product_id": 1, "quantity": 2, "price": 29.99}
                                        ],
                                        "shipping_address": {
                                            "street": "123 Main St",
                                            "city": "Anytown",
                                            "zip": "12345"
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        } 