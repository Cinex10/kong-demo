#!/usr/bin/env python3
"""
Template Renderer for Kong Demo Generator

This module handles the rendering of templates for the Kong demo.
"""

import os
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader

from mock_api_generator import MockApiGeneratorFactory, MockApiGenerator
from ai_model_client import GroqAiModelClient

class TemplateRenderer:
    """Renders templates for Kong demo files"""
    
    def __init__(self, template_dir: Optional[str] = None, 
                 mock_api_generator: Optional[MockApiGenerator] = None,
                 ai_client: Optional[GroqAiModelClient] = None,
                 config_manager = None) -> None:
        """
        Initialize the template renderer with a template directory
        
        Args:
            template_dir: Directory containing Jinja2 templates
            mock_api_generator: Optional custom mock API generator
            ai_client: Optional AI model client for code generation
            config_manager: Optional configuration manager with service data
        """
        if template_dir is None:
            # Default to the templates directory relative to this file
            template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

        self.template_dir: str = template_dir
        self.env: Environment = Environment(loader=FileSystemLoader(template_dir))
        self.ai_client: Optional[GroqAiModelClient] = ai_client
        self.mock_api_generator: Optional[MockApiGenerator] = mock_api_generator
        self.config_manager = config_manager
        
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context"""
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_docker_compose(self, project_name: str, config: Dict[str, Any]) -> str:
        """Render the Docker Compose template"""
        return self.render_template("docker-compose.yaml.j2", {
            "project_name": project_name,
            "config": config
        })
    
    def render_setup_script(self, project_name: str, config: Dict[str, Any]) -> str:
        """Render the setup script template"""
        return self.render_template("setup.sh.j2", {
            "project_name": project_name,
            "config": config
        })
    
    def render_readme(self, project_name: str, config: Dict[str, Any]) -> str:
        """Render the README template"""
        return self.render_template("README.md.j2", {
            "project_name": project_name,
            "config": config
        })
    
    def render_test_script(self, project_name: str, config: Dict[str, Any]) -> str:
        """Render the test API script template"""
        return self.render_template("test-api.sh.j2", {
            "project_name": project_name,
            "config": config
        })
    
    def render_mock_api(self, service_name: str, business_type: str = "generic", 
                        params: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate mock API code for a service with business-specific logic
        
        Args:
            service_name: Name of the service
            business_type: Type of business logic to generate (e.g., insurance, ecommerce)
            params: Additional parameters for customization
            
        Returns:
            Dictionary of filenames to file contents
        """
        params = params or {}
        
        # Use provided generator or create one using the factory
        generator = self.mock_api_generator
        if generator is None:
            try:
                # Create AI client if one was provided
                ai_client = self.ai_client
                
                # Create appropriate generator with AI client
                generator = MockApiGeneratorFactory.create_generator(
                    business_type, 
                    ai_client=ai_client
                )
            except Exception as e:
                print(f"Failed to create business-specific generator: {str(e)}. Using generic generator.")
                from mock_api_generator import BasicMockApiGenerator
                generator = BasicMockApiGenerator()
        
        return generator.generate_mock_api(service_name, business_type, params)
    
    def register_template(self, name: str, path: str) -> None:
        """Register a custom template"""
        # This would allow extension with custom templates
        loader = self.env.loader
        if isinstance(loader, FileSystemLoader):
            # Add the directory containing the template to the loader
            template_dir = os.path.dirname(path)
            
            # Create a new loader with both the original and new directories
            new_loader = FileSystemLoader([loader.searchpath[0], template_dir])
            self.env.loader = new_loader 