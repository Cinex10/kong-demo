#!/usr/bin/env python3
"""
Demo Project Generator for Kong Demo Generator

This module orchestrates the entire process of generating a Kong demo project.
"""

import os
from typing import Dict, List, Any, Optional, Union, Tuple

from config_manager import ConfigurationManager
from input_collector import UserInputCollector
from template_renderer import TemplateRenderer
from fs_manager import FileSystemManager
from kong_admin import KongAdminClient

class DemoProjectGenerator:
    """Orchestrates the Kong demo generation process"""
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None, 
                 input_collector: Optional[UserInputCollector] = None, 
                 template_renderer: Optional[TemplateRenderer] = None, 
                 fs_manager: Optional[FileSystemManager] = None) -> None:
        """Initialize with optional components (for dependency injection)"""
        self.config_manager: ConfigurationManager = config_manager or ConfigurationManager()
        self.input_collector: UserInputCollector = input_collector or UserInputCollector(self.config_manager)
        self.template_renderer: TemplateRenderer = template_renderer or TemplateRenderer(config_manager=self.config_manager)
        self.fs_manager: FileSystemManager = fs_manager or FileSystemManager()
        
    def generate_from_interactive_input(self) -> str:
        """Generate a demo project based on interactive user input"""
        # Collect all user input
        project_name, config_manager = self.input_collector.collect_all()
        
        # The config_manager will have been updated with user input
        self.config_manager = config_manager
        
        # Generate the project files
        self._generate_project_files(project_name)
        
        return project_name
    
    def generate_from_config_file(self, config_file: str, project_name: Optional[str] = None) -> str:
        """Generate a demo project based on a configuration file"""
        # Load the configuration from file
        self.config_manager.load_from_file(config_file)
        
        # If project name is not provided, extract it from the config file name
        if not project_name:
            project_name = os.path.splitext(os.path.basename(config_file))[0]
        
        # Generate the project files
        self._generate_project_files(project_name)
        
        return project_name
    
    def _generate_project_files(self, project_name: str) -> None:
        """Generate all the project files based on the configuration"""
        # Use the FileSystemManager to create all project files
        self.fs_manager.create_project_files(
            project_name, 
            self.config_manager, 
            self.template_renderer
        )
        
        print(f"\nDemo project '{project_name}' has been generated.")
        print(f"You can find the files in: {self.fs_manager.output_dir}/{project_name}")
    
    def deploy_to_kong(self, kong_admin_url: str, project_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Deploy the configuration to a running Kong instance"""
        # Create a Kong Admin client
        kong_client = KongAdminClient(kong_admin_url)
        
        # If a project name is provided, load the configuration from file
        if project_name:
            config_file = f"{self.fs_manager.output_dir}/{project_name}/kong-config.json"
            self.config_manager.load_from_file(config_file)
        
        # Deploy the configuration
        print(f"Deploying configuration to Kong at {kong_admin_url}")
        results = kong_client.deploy_configuration(self.config_manager)
        
        # Print results
        print("\nDeployment Results:")
        print(f"Services created: {len(results['services'])}")
        print(f"Routes created: {len(results['routes'])}")
        print(f"Plugins created: {len(results['plugins'])}")
        print(f"Consumers created: {len(results['consumers'])}")
        
        return results


def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kong Demo Generator')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--deploy', help='Deploy to Kong Admin URL')
    parser.add_argument('--project', help='Project name for deployment')
    parser.add_argument('--output-dir', help='Output directory for generated files', default='output')
    
    args = parser.parse_args()
    
    # Create the generator with custom output directory if provided
    fs_manager = FileSystemManager(args.output_dir)
    generator = DemoProjectGenerator(fs_manager=fs_manager)
    
    # Generate from config file or interactive input
    if args.config:
        project_name = generator.generate_from_config_file(args.config, args.project)
    else:
        project_name = generator.generate_from_interactive_input()
        
    # Deploy to Kong if requested
    if args.deploy:
        generator.deploy_to_kong(args.deploy, project_name)

if __name__ == "__main__":
    main() 