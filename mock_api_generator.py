#!/usr/bin/env python3
"""
Mock API Generator for Kong Demo Generator

This module provides a strategy pattern for generating mock APIs with business-specific logic using AI.

Architecture Overview:
---------------------
1. MockApiGenerator - Abstract base class defining the generator interface
   |
   ├── BasicMockApiGenerator - Concrete generator that creates simple CRUD APIs without AI
   |
   └── AiMockApiGenerator - Abstract base for AI-powered generators
       |
       ├── InsuranceMockApiGenerator - Insurance-specific AI generator
       └── EcommerceMockApiGenerator - E-commerce-specific AI generator

2. MockApiGeneratorFactory - Factory pattern for creating appropriate generators

This architecture separates concerns between:
- Business logic (specific domain generators)
- AI model interaction (model clients)
- Generator selection (factory)

This allows for easy extension with new business domains or AI providers.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from ai_model_client import AiModelClient

class MockApiGenerator(ABC):
    """Base interface for all mock API generators"""
    
    @abstractmethod
    def generate_mock_api(self, service_name: str, business_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate mock API files with business-specific logic
        
        Args:
            service_name: Name of the service
            business_type: Type of business logic to generate
            params: Additional parameters for customization
            
        Returns:
            Dictionary of filenames to file contents
        """
        pass
    
    @abstractmethod
    def get_supported_business_types(self) -> List[str]:
        """
        Get list of business types supported by this generator
        
        Returns:
            List of supported business type names
        """
        pass


class BasicMockApiGenerator(MockApiGenerator):
    """Basic mock API generator that creates simple CRUD endpoints"""
    
    def generate_mock_api(self, service_name: str, business_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate a basic mock API with CRUD operations"""
        params = params or {}
        
        server_js = self._generate_server_js(service_name, business_type, params)
        package_json = self._generate_package_json(service_name)
        dockerfile = self._generate_dockerfile()
        
        return {
            "server.js": server_js,
            "package.json": package_json,
            "Dockerfile": dockerfile
        }
    
    def get_supported_business_types(self) -> List[str]:
        """Get list of business types supported by this generator"""
        return ["generic"]
    
    def _generate_server_js(self, service_name: str, business_type: str, params: Dict[str, Any]) -> str:
        """Generate server.js file with business logic"""
        return f"""const express = require('express');
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
    description: 'Mock API for ' + serviceName
  }});
}});

// Echo endpoint
app.all('/echo', (req, res) => {{
  res.status(200).json({{
    method: req.method,
    url: req.url,
    headers: req.headers,
    query: req.query,
    body: req.body
  }});
}});

// Generic CRUD endpoints
const items = [
  {{ id: 1, name: 'Item 1', description: 'This is item 1' }},
  {{ id: 2, name: 'Item 2', description: 'This is item 2' }}
];

// List items
app.get('/items', (req, res) => {{
  res.status(200).json(items);
}});

// Get a specific item
app.get('/items/:id', (req, res) => {{
  const item = items.find(i => i.id === parseInt(req.params.id));
  if (item) {{
    res.status(200).json(item);
  }} else {{
    res.status(404).json({{ error: 'Item not found' }});
  }}
}});

// Create an item
app.post('/items', (req, res) => {{
  const newId = items.length > 0 ? Math.max(...items.map(i => i.id)) + 1 : 1;
  const newItem = {{ id: newId, ...req.body }};
  items.push(newItem);
  res.status(201).json(newItem);
}});

// Update an item
app.put('/items/:id', (req, res) => {{
  const itemIndex = items.findIndex(i => i.id === parseInt(req.params.id));
  if (itemIndex >= 0) {{
    items[itemIndex] = {{ ...items[itemIndex], ...req.body }};
    res.status(200).json(items[itemIndex]);
  }} else {{
    res.status(404).json({{ error: 'Item not found' }});
  }}
}});

// Delete an item
app.delete('/items/:id', (req, res) => {{
  const itemIndex = items.findIndex(i => i.id === parseInt(req.params.id));
  if (itemIndex >= 0) {{
    const deleted = items.splice(itemIndex, 1);
    res.status(200).json(deleted[0]);
  }} else {{
    res.status(404).json({{ error: 'Item not found' }});
  }}
}});

// Start the server
app.listen(port, () => {{
  console.log(`${{serviceName}} mock API listening at http://localhost:${{port}}`);
}});
"""
    
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


class AiMockApiGenerator(MockApiGenerator):
    """Base class for AI-powered mock API generators"""
    
    def __init__(self, ai_client: AiModelClient = None):
        """Initialize the AI-powered generator"""
        self.ai_client = ai_client
    
    @abstractmethod
    def get_prompt_for_business_type(self, service_name: str, business_type: str, params: Dict[str, Any]) -> str:
        """
        Get the AI prompt for the specific business type
        
        Args:
            service_name: Name of the service
            business_type: Type of business logic to generate
            params: Additional parameters for customization
            
        Returns:
            AI prompt string
        """
        pass
    
    def extract_code_from_response(self, response: str) -> str:
        """
        Extract only the JavaScript code from the AI model response
        
        Args:
            response: The raw response from the AI model
            
        Returns:
            Clean JavaScript code
        """
        # Check if the response contains markdown code blocks with language specifier
        if "```javascript" in response or "```js" in response:
            # Extract code between markdown code blocks
            import re
            code_blocks = re.findall(r'```(?:javascript|js)(.*?)```', response, re.DOTALL)
            if code_blocks:
                return code_blocks[0].strip()
        
        # Check if the response contains generic markdown code blocks
        if "```" in response:
            import re
            # Look for code blocks without language specifier
            code_blocks = re.findall(r'```(.*?)```', response, re.DOTALL)
            if code_blocks:
                # Verify if it looks like JavaScript code
                potential_code = code_blocks[0].strip()
                if any(potential_code.startswith(pattern) for pattern in ["const ", "import ", "// ", "let ", "var ", "function "]):
                    return potential_code
                
        # Check if the response starts with common JavaScript patterns
        js_patterns = ["const ", "import ", "// ", "let ", "var ", "function ", "'use strict';"]
        lines = response.strip().split('\n')
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if any(stripped_line.startswith(pattern) for pattern in js_patterns):
                # Found the start of the code, now find where it ends
                # This is a heuristic - we assume the code continues until the end
                # or until we find a line that looks like a markdown separator or explanation
                end_marker_patterns = ["## ", "# ", "---", "===", "In conclusion", "This code", "The above"]
                for j in range(len(lines) - 1, i, -1):
                    if any(lines[j].strip().startswith(pattern) for pattern in end_marker_patterns):
                        return '\n'.join(lines[i:j]).strip()
                return '\n'.join(lines[i:]).strip()
                
        # If no JavaScript code pattern was found, return the whole response
        return response.strip()
    
    def generate_mock_api(self, service_name: str, business_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate AI-powered mock API with business-specific logic"""
        params = params or {}
        
        # Generate business-specific logic using AI
        prompt = self.get_prompt_for_business_type(service_name, business_type, params)
        
        try:
            raw_response = self.ai_client.generate_code(prompt)
            # Extract only the code from the response
            business_logic = self.extract_code_from_response(raw_response)
        except Exception as e:
            # Fallback to basic generator on error
            print(f"AI generation failed: {str(e)}. Falling back to basic generator.")
            basic_generator = BasicMockApiGenerator()
            business_logic = basic_generator._generate_server_js(service_name, business_type, params)
        
        # Add common files
        package_json = self._generate_package_json(service_name, business_type, params)
        dockerfile = self._generate_dockerfile(business_type, params)
        
        return {
            "server.js": business_logic,
            "package.json": package_json,
            "Dockerfile": dockerfile
        }
    
    def _generate_package_json(self, service_name: str, business_type: str, params: Dict[str, Any]) -> str:
        """Generate package.json with appropriate dependencies"""
        return f"""{{
  "name": "{service_name}-mock",
  "version": "1.0.0",
  "description": "AI-generated mock API for {service_name} ({business_type})",
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
    
    def _generate_dockerfile(self, business_type: str, params: Dict[str, Any]) -> str:
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


class InsuranceMockApiGenerator(AiMockApiGenerator):
    """Generates mock APIs with insurance-specific business logic"""
    
    def get_supported_business_types(self) -> List[str]:
        """Returns the business types supported by this generator"""
        return ["insurance", "insurance-policy", "insurance-claims", "health-insurance", "auto-insurance"]
    
    def get_prompt_for_business_type(self, service_name: str, business_type: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate AI prompt for insurance business type"""
        policy_type = params.get("policy_type", "auto") if params else "auto"
        features = params.get("features", ["basic"]) if params else ["basic"]
        
        prompt = f"""
Create a simple Node.js Express API for an insurance {policy_type} service called '{service_name}'.
The API should include realistic endpoints for a {business_type} service with the following features:
- {', '.join(features)}

IMPORTANT REQUIREMENTS:
1. Use ONLY Express.js with minimal dependencies (express, cors, morgan)
2. Use hardcoded example data arrays for all data storage (NO databases, NO MongoDB, NO Mongoose)
3. Include realistic but FAKE data for insurance entities (policies, claims, customers)
4. Implement proper RESTful routes with basic validation
5. Include basic error handling middleware
6. Add meaningful comments explaining the business logic

Example structure:
```javascript
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const app = express();
const port = 8080;

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// Hardcoded data
const policies = [
  // Example policies
];

// Routes
// GET /policies
// GET /policies/:id
// etc.

app.listen(port, () => {{
  console.log(`Server listening at http://localhost:${{port}}`);
}});
```

Return ONLY the JavaScript code for server.js with no explanations or markdown formatting.
"""
        
        return prompt.strip()


class EcommerceMockApiGenerator(AiMockApiGenerator):
    """Generates mock APIs with e-commerce business logic"""
    
    def get_supported_business_types(self) -> List[str]:
        """Returns the business types supported by this generator"""
        return ["ecommerce", "ecommerce-product", "ecommerce-order"]
    
    def get_prompt_for_business_type(self, service_name: str, business_type: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate AI prompt for e-commerce business type"""
        product_type = params.get("product_type", "electronics") if params else "electronics"
        features = params.get("features", ["basic"]) if params else ["basic"]
        
        is_product_api = "product" in business_type
        is_order_api = "order" in business_type
        
        if is_product_api:
            focus = f"product catalog for {product_type}"
        elif is_order_api:
            focus = "order processing and fulfillment"
        else:
            focus = f"general e-commerce platform selling {product_type}"
            
        prompt = f"""
Create a simple Node.js Express API for an e-commerce service called '{service_name}' focused on {focus}.
The API should include realistic endpoints with the following features:
- {', '.join(features)}

IMPORTANT REQUIREMENTS:
1. Use ONLY Express.js with minimal dependencies (express, cors, morgan)
2. Use hardcoded example data arrays for all data storage (NO databases, NO MongoDB, NO Mongoose)
3. Include realistic but FAKE data for products, orders, users, etc.
4. Implement proper RESTful routes with basic validation
5. Include basic error handling middleware
6. Add meaningful comments explaining the business logic

Example structure:
```javascript
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const app = express();
const port = 8080;

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// Hardcoded data
const products = [
  // Example products
];

// Routes
// GET /products
// GET /products/:id
// etc.

app.listen(port, () => {{
  console.log(`Server listening at http://localhost:${{port}}`);
}});
```

Return ONLY the JavaScript code for server.js with no explanations or markdown formatting.
"""
        
        return prompt.strip()


class MockApiGeneratorFactory:
    """Factory for creating appropriate MockApiGenerator instances"""
    
    @staticmethod
    def create_generator(business_type: str, ai_client: AiModelClient = None) -> MockApiGenerator:
        """
        Create a mock API generator for the specified business type
        
        Args:
            business_type: The type of business logic to generate
            ai_client: Optional AI model client instance
            
        Returns:
            An appropriate MockApiGenerator instance
        """
        # Define the mapping of business types to generator classes
        generators = {
            # Basic generator for generic APIs
            "generic": BasicMockApiGenerator,
            
            # Insurance domain generators
            "insurance": InsuranceMockApiGenerator,
            "insurance-policy": InsuranceMockApiGenerator,
            "insurance-claims": InsuranceMockApiGenerator,
            "health-insurance": InsuranceMockApiGenerator,
            "auto-insurance": InsuranceMockApiGenerator,
            
            # E-commerce domain generators
            "ecommerce": EcommerceMockApiGenerator,
            "ecommerce-product": EcommerceMockApiGenerator,
            "ecommerce-order": EcommerceMockApiGenerator,
        }
        
        # Get the appropriate generator class, defaulting to BasicMockApiGenerator
        generator_class = generators.get(business_type, BasicMockApiGenerator)
        
        # Create and return the generator instance
        if generator_class == BasicMockApiGenerator:
            return generator_class()
        else:
            # For AI-powered generators, pass the AI client or API key
            return generator_class(ai_client=ai_client) 