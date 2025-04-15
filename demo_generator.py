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
from api_specification_generator import ApiSpecificationGenerator
from mock_api_from_spec_generator import MockApiFromSpecGenerator
from kong_config_from_spec_generator import KongConfigFromSpecGenerator
from ai_model_client import GroqAiModelClient

class DemoProjectGenerator:
    """Orchestrates the Kong demo generation process"""
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None, 
                 input_collector: Optional[UserInputCollector] = None, 
                 template_renderer: Optional[TemplateRenderer] = None, 
                 fs_manager: Optional[FileSystemManager] = None,
                 api_spec_generator: Optional[ApiSpecificationGenerator] = None) -> None:
        """Initialize with optional components (for dependency injection)"""
        self.config_manager: ConfigurationManager = config_manager or ConfigurationManager()
        self.input_collector: UserInputCollector = input_collector or UserInputCollector(self.config_manager)
        self.template_renderer: TemplateRenderer = template_renderer or TemplateRenderer(config_manager=self.config_manager)
        self.fs_manager: FileSystemManager = fs_manager or FileSystemManager()
        
        # Create AI client for API specification generation
        try:
            import os
            self.ai_client = GroqAiModelClient()
            self.api_spec_generator = api_spec_generator or ApiSpecificationGenerator(self.ai_client)
        except (ImportError, ValueError) as e:
            print(f"AI client initialization failed: {str(e)}. Using template-based generation.")
            self.ai_client = None
            self.api_spec_generator = api_spec_generator or ApiSpecificationGenerator(None)
        
    def generate_from_interactive_input(self, assume_kong_running: bool = False) -> str:
        """Generate a demo project based on interactive user input"""
        
        # Collect project name and basic information
        project_name = self.input_collector.collect_project_info()
        
        # Collect business information
        business_type, business_params = self.input_collector.collect_business_info()
        
        # Collect Kong features
        kong_features = self.input_collector.collect_kong_features()
        
        # Generate API specification using AI
        print("\nGenerating API specification based on business domain and Kong features...")
        api_specification = self.api_spec_generator.generate_api_specification(business_type, kong_features)
        
        # Save API specification to the input collector
        self.input_collector.set_api_specification(api_specification)
        
        # Generate Kong configuration from specification
        if assume_kong_running:
            print("\nAssuming Kong is already running - generating configuration only...")
            kong_config_generator = KongConfigFromSpecGenerator(api_specification)
            self.config_manager = kong_config_generator.generate_kong_config(self.config_manager, kong_features)
        
        # Collect services based on the API specification
        self.input_collector.collect_services()
        
        # Collect plugins based on the Kong features
        self.input_collector.collect_plugins()
        
        # The config_manager will have been updated with user input
        self.config_manager = self.input_collector.config_manager
        
        # Generate the project files
        self._generate_project_files(project_name, api_specification, assume_kong_running)
        
        return project_name
    
    def generate_from_config_file(self, config_file: str, project_name: Optional[str] = None, assume_kong_running: bool = False) -> str:
        """Generate a demo project based on a configuration file"""
        # Load the configuration from file
        self.config_manager.load_from_file(config_file)
        
        # If project name is not provided, extract it from the config file name
        if not project_name:
            project_name = os.path.splitext(os.path.basename(config_file))[0]
        
        # Extract API specification from config, if available
        api_specification = None
        for service in self.config_manager.config["services"]:
            if "metadata" in service and "specification" in service["metadata"]:
                api_specification = {"services": [service["metadata"]["specification"]]}
                break
        
        # Generate the project files
        self._generate_project_files(project_name, api_specification, assume_kong_running)
        
        return project_name
    
    def _generate_project_files(self, project_name: str, api_specification: Optional[Dict[str, Any]] = None, assume_kong_running: bool = False) -> None:
        """Generate all the project files based on the configuration"""
        # Use the FileSystemManager to create all project files
        self.fs_manager.create_project_files(
            project_name, 
            self.config_manager, 
            self.template_renderer,
            assume_kong_running
        )
        
        # If we have an API specification, save it to a file
        if api_specification:
            import json
            api_spec_path = os.path.join(self.fs_manager.output_dir, project_name, "api-specification.json")
            with open(api_spec_path, 'w') as f:
                json.dump(api_specification, f, indent=2)
                
            print(f"Saved API specification to {api_spec_path}")
            
            # Create mock APIs using the specification
            self._generate_mock_apis_from_spec(project_name, api_specification)
        
        print(f"\nDemo project '{project_name}' has been generated.")
        print(f"You can find the files in: {self.fs_manager.output_dir}/{project_name}")
        
        if assume_kong_running:
            print("\nNote: The project has been configured assuming Kong is already running.")
            print("To deploy the configuration to Kong, run the deploy script:")
            print(f"  cd {self.fs_manager.output_dir}/{project_name} && ./deploy-to-kong.sh")
    
    def _generate_mock_apis_from_spec(self, project_name: str, api_specification: Dict[str, Any]) -> None:
        """Generate mock APIs based on the API specification"""
        if "services" not in api_specification:
            return
            
        for service_spec in api_specification["services"]:
            service_name = service_spec["name"]
            
            # Create a mock API generator with the specification
            mock_generator = MockApiFromSpecGenerator(api_specification)
            
            # Generate mock API files
            mock_files = mock_generator.generate_mock_api(service_name, "api-spec", {})
            
            # Set up directory for the mock API
            mock_dir = self.fs_manager.setup_mock_api_directory(project_name, service_name)
            
            # Write each file
            for filename, content in mock_files.items():
                file_path = os.path.join(mock_dir, filename)
                with open(file_path, 'w') as f:
                    f.write(content)
                    
                # Make server.js executable if needed
                if filename == 'server.js':
                    os.chmod(file_path, os.stat(file_path).st_mode | 0o111)
                    
            print(f"Generated mock API for {service_name} in {mock_dir}")
    
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
    parser.add_argument('--assume-kong-running', action='store_true', help='Assume Kong is already running')
    
    args = parser.parse_args()
    
    # Create the generator with custom output directory if provided
    fs_manager = FileSystemManager(args.output_dir)
    generator = DemoProjectGenerator(fs_manager=fs_manager)
    
    # Generate from config file or interactive input
    if args.config:
        project_name = generator.generate_from_config_file(args.config, args.project, args.assume_kong_running)
    else:
        project_name = generator.generate_from_interactive_input(args.assume_kong_running)
        
    # Deploy to Kong if requested
    if args.deploy:
        generator.deploy_to_kong(args.deploy, project_name)

if __name__ == "__main__":
    main() 