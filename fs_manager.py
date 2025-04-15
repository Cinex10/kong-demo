#!/usr/bin/env python3
"""
File System Manager for Kong Demo Generator

This module handles all file system operations for the Kong demo generator.
"""

import os
import json
import yaml
import stat
from typing import Dict, Any, Optional, Union

from config_manager import ConfigurationManager
from template_renderer import TemplateRenderer

class FileSystemManager:
    """Manages file system operations for the Kong demo generator"""
    
    def __init__(self, output_dir: str = "output") -> None:
        """Initialize with the base output directory"""
        self.output_dir: str = output_dir
        
    def ensure_directory(self, path: str) -> None:
        """Ensure that a directory exists, creating it if necessary"""
        os.makedirs(path, exist_ok=True)
        
    def write_file(self, path: str, content: str, executable: bool = False) -> None:
        """Write content to a file, optionally making it executable"""
        with open(path, 'w') as f:
            f.write(content)
            
        if executable:
            # Make the file executable (chmod +x)
            os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
    def write_json(self, path: str, data: Any) -> None:
        """Write JSON data to a file"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def write_yaml(self, path: str, data: Any) -> None:
        """Write YAML data to a file"""
        with open(path, 'w') as f:
            yaml.dump(data, f)
            
    def setup_project_directory(self, project_name: str) -> str:
        """Set up the basic directory structure for a project"""
        project_dir = os.path.join(self.output_dir, project_name)
        self.ensure_directory(project_dir)
        return project_dir
        
    def setup_mock_api_directory(self, project_name: str, service_name: str) -> str:
        """Set up directory for a mock API service"""
        mock_dir = os.path.join(self.output_dir, project_name, "mock-apis", service_name)
        self.ensure_directory(mock_dir)
        return mock_dir
        
    def create_project_files(self, project_name: str, config: ConfigurationManager, renderer: TemplateRenderer, assume_kong_running: bool = False) -> None:
        """Create all project files using the provided configuration and renderer"""
        # Set up base project directory
        project_dir = self.setup_project_directory(project_name)
        
        # Save configuration files
        self.write_json(
            os.path.join(project_dir, "kong-config.json"), 
            config.config
        )
        
        self.write_yaml(
            os.path.join(project_dir, "kong-config.yaml"), 
            config.config
        )
        
        # Save Kong declarative config
        self.write_yaml(
            os.path.join(project_dir, "kong.yaml"), 
            config.to_declarative_config()
        )
        
        # Create Docker Compose file with or without Kong based on assume_kong_running
        docker_compose = renderer.render_docker_compose(project_name, config.config, assume_kong_running)
        self.write_file(
            os.path.join(project_dir, "docker-compose.yaml"), 
            docker_compose
        )
        
        # Create setup script with or without Kong setup based on assume_kong_running
        setup_script = renderer.render_setup_script(project_name, config.config, assume_kong_running)
        self.write_file(
            os.path.join(project_dir, "setup.sh"), 
            setup_script,
            executable=True
        )
        
        # Create README
        readme = renderer.render_readme(project_name, config.config, assume_kong_running)
        self.write_file(
            os.path.join(project_dir, "README.md"), 
            readme
        )
        
        # Create test API script
        test_script = renderer.render_test_script(project_name, config.config)
        self.write_file(
            os.path.join(project_dir, "test-api.sh"), 
            test_script,
            executable=True
        )
        
        # If Kong is already running, create a deployment script
        if assume_kong_running:
            deploy_script = renderer.render_deploy_script(project_name, config.config)
            self.write_file(
                os.path.join(project_dir, "deploy-to-kong.sh"), 
                deploy_script,
                executable=True
            )
        
        # Create mock API implementations
        for service in config.config["services"]:
            self.create_mock_api_with_metadata(project_name, service, renderer)
            
    def create_mock_api_with_metadata(self, project_name: str, service: Dict[str, Any], renderer: TemplateRenderer) -> None:
        """Create files for a mock API service using its metadata"""
        service_name = service["name"]
        mock_dir = self.setup_mock_api_directory(project_name, service_name)
        
        # Extract business type and parameters directly from service
        business_type = "generic"
        business_params = {}
        
        if "metadata" in service:
            metadata = service.get("metadata", {})
            business_type = metadata.get("business_type", "generic")
            business_params = metadata.get("business_params", {})
            
        print(f"Generating mock API for {service_name} with business type: {business_type}")
        
        # Generate mock API files with business type and parameters
        mock_files = renderer.render_mock_api(service_name, business_type, business_params)
        
        # Write each file
        for filename, content in mock_files.items():
            self.write_file(
                os.path.join(mock_dir, filename),
                content
            )

    def create_mock_api(self, project_name: str, service_name: str, renderer: TemplateRenderer) -> None:
        """Create files for a mock API service (legacy method for backward compatibility)"""
        # Find the service data in the configuration if possible
        service_data = {"name": service_name}
        
        # Try to get configuration file to extract metadata
        try:
            config_file = os.path.join(self.output_dir, project_name, "kong-config.json")
            if os.path.exists(config_file):
                from config_manager import ConfigurationManager
                config_manager = ConfigurationManager()
                config_manager.load_from_file(config_file)
                
                # Find the service with the given name
                for svc in config_manager.config["services"]:
                    if svc["name"] == service_name:
                        service_data = svc
                        break
        except Exception:
            # If we fail to load metadata, just use the service name
            pass
            
        # Call the new method
        self.create_mock_api_with_metadata(project_name, service_data, renderer) 