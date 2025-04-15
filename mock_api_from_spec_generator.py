#!/usr/bin/env python3
"""
Mock API Generator from Specification for Kong Demo Generator

This module generates mock API implementations based on an API specification.
"""

import json
from typing import Dict, List, Any, Optional
from mock_api_generator import MockApiGenerator

class MockApiFromSpecGenerator(MockApiGenerator):
    """Generates mock API implementations based on API specifications"""
    
    def __init__(self, specification: Optional[Dict[str, Any]] = None):
        """
        Initialize the generator with an API specification
        
        Args:
            specification: API specification dictionary
        """
        self.specification = specification or {}
        
    def generate_mock_api(self, service_name: str, business_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate mock API files for a service based on API specification
        
        Args:
            service_name: Name of the service
            business_type: Type of business logic (ignored if specification is provided)
            params: Additional parameters (ignored if specification is provided)
            
        Returns:
            Dictionary of filenames to file contents
        """
        # Get the service specification from the loaded specification
        service_spec = self._find_service_spec(service_name)
        
        # Generate the mock API files
        server_js = self._generate_server_js(service_name, service_spec)
        package_json = self._generate_package_json(service_name)
        dockerfile = self._generate_dockerfile()
        
        return {
            "server.js": server_js,
            "package.json": package_json,
            "Dockerfile": dockerfile
        }
    
    def get_supported_business_types(self) -> List[str]:
        """Get list of business types supported by this generator"""
        return ["api-spec"]  # This generator works with any business type as long as a spec is provided
    
    def _find_service_spec(self, service_name: str) -> Dict[str, Any]:
        """Find the service specification for the given service name"""
        if "services" not in self.specification:
            return {}
            
        # Find the service by name
        for service in self.specification["services"]:
            if service.get("name") == service_name:
                return service
                
        # If no matching service is found, use the first service if available
        if self.specification["services"]:
            return self.specification["services"][0]
            
        return {}
    
    def _generate_server_js(self, service_name: str, service_spec: Dict[str, Any]) -> str:
        """
        Generate server.js file based on API specification
        
        Args:
            service_name: Name of the service
            service_spec: Specification for the service
            
        Returns:
            server.js content
        """
        # Start with the basic Express.js setup
        code = f"""const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const app = express();
const port = 8080;
const serviceName = '{service_name}';

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// Health check endpoint
app.get('/health', (req, res) => {{
  res.status(200).json({{ status: 'healthy', service: serviceName }});
}});

// Information endpoint
app.get('/info', (req, res) => {{
  res.status(200).json({{
    name: serviceName,
    version: '1.0.0',
    description: '{service_spec.get("description", f"Mock API for {service_name}")}'
  }});
}});

// In-memory database
const db = {{}};

"""

        # Generate routes and endpoints based on the specification
        if service_spec and "routes" in service_spec:
            for route in service_spec["routes"]:
                route_path = route.get("path", "/api")
                route_name = route.get("name", "api_route")
                
                # Initialize in-memory collection for this route
                collection_name = route_name.replace("-", "_").replace("/", "_")
                code += f"""
// In-memory collection for {route_name}
db.{collection_name} = [
  {{ id: '1', createdAt: new Date().toISOString() }},
  {{ id: '2', createdAt: new Date().toISOString() }}
];

"""
                
                # Generate endpoints for this route
                if "endpoints" in route:
                    for endpoint in route["endpoints"]:
                        endpoint_path = endpoint.get("path", "/")
                        endpoint_method = endpoint.get("method", "GET").lower()
                        endpoint_desc = endpoint.get("description", "")
                        
                        # Create full path by combining route path and endpoint path
                        # Handle cases like /api + /items vs /api + /
                        full_path = route_path
                        if endpoint_path and endpoint_path != "/":
                            if not endpoint_path.startswith("/"):
                                full_path += "/"
                            full_path += endpoint_path
                            
                        # Generate handler based on HTTP method and path
                        code += f"""// {endpoint_desc}
app.{endpoint_method}('{full_path}', (req, res) => {{
"""
                        
                        if endpoint_method == "get" and "{id}" in full_path:
                            # GET by ID
                            code += f"""  const id = req.params.id;
  const item = db.{collection_name}.find(item => item.id === id);
  
  if (item) {{
    res.status(200).json(item);
  }} else {{
    res.status(404).json({{ error: 'Item not found' }});
  }}
}});

"""
                        elif endpoint_method == "get":
                            # GET list
                            code += f"""  res.status(200).json(db.{collection_name});
}});

"""
                        elif endpoint_method == "post":
                            # POST - create new
                            code += f"""  const newId = String(db.{collection_name}.length + 1);
  const newItem = {{ 
    id: newId, 
    createdAt: new Date().toISOString(),
    ...req.body 
  }};
  
  db.{collection_name}.push(newItem);
  res.status(201).json(newItem);
}});

"""
                        elif endpoint_method == "put" or endpoint_method == "patch":
                            # PUT/PATCH - update
                            code += f"""  const id = req.params.id;
  const itemIndex = db.{collection_name}.findIndex(item => item.id === id);
  
  if (itemIndex >= 0) {{
    db.{collection_name}[itemIndex] = {{ 
      ...db.{collection_name}[itemIndex],
      ...req.body,
      updatedAt: new Date().toISOString()
    }};
    res.status(200).json(db.{collection_name}[itemIndex]);
  }} else {{
    res.status(404).json({{ error: 'Item not found' }});
  }}
}});

"""
                        elif endpoint_method == "delete":
                            # DELETE
                            code += f"""  const id = req.params.id;
  const itemIndex = db.{collection_name}.findIndex(item => item.id === id);
  
  if (itemIndex >= 0) {{
    const deleted = db.{collection_name}.splice(itemIndex, 1);
    res.status(200).json({{ success: true, deleted: deleted[0] }});
  }} else {{
    res.status(404).json({{ error: 'Item not found' }});
  }}
}});

"""
                
        # Add a catch-all route for undefined endpoints
        code += """// Catch-all for undefined endpoints
app.all('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    method: req.method,
    url: req.url
  });
});

// Start the server
app.listen(port, () => {
  console.log(`${serviceName} mock API listening at http://localhost:${port}`);
});
"""
        
        return code
    
    def _generate_package_json(self, service_name: str) -> str:
        """Generate package.json file"""
        return f"""{{
  "name": "{service_name}-mock",
  "version": "1.0.0",
  "description": "Mock API for {service_name}",
  "main": "server.js",
  "scripts": {{
    "start": "node server.js"
  }},
  "dependencies": {{
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "morgan": "^1.10.0"
  }}
}}
"""
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile"""
        return """FROM node:18-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY server.js .

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD wget -qO- http://localhost:8080/health || exit 1

CMD ["npm", "start"]
""" 