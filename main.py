#!/usr/bin/env python3
"""
Kong Demo Generator

This script creates customized Kong API Gateway configurations for demonstration purposes.
It generates all necessary configuration files and setup instructions based on user input.
"""

import argparse
import pdb
import sys
from typing import Optional, Dict, List, Any, Union, NoReturn

from ai_model_client import GroqAiModelClient
from demo_generator import DemoProjectGenerator
from fs_manager import FileSystemManager
from template_renderer import TemplateRenderer

def main() -> int:
    """Main entry point for the Kong Demo Generator"""
    parser = argparse.ArgumentParser(description='Kong Demo Generator')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--deploy', help='Deploy to Kong Admin URL')
    parser.add_argument('--project', help='Project name for deployment')
    parser.add_argument('--output-dir', help='Output directory for generated files', default='output')
    
    args = parser.parse_args()
    
    # pdb.set_trace()
    
    # Create the generator with custom output directory if provided
    fs_manager = FileSystemManager(args.output_dir)
    template_renderer = TemplateRenderer(ai_client=GroqAiModelClient())
    generator = DemoProjectGenerator(fs_manager=fs_manager, template_renderer=template_renderer)
    
    try:
        # Generate from config file or interactive input
        if args.config:
            project_name = generator.generate_from_config_file(args.config, args.project)
        else:
            project_name = generator.generate_from_interactive_input()
            
        # Deploy to Kong if requested
        if args.deploy:
            generator.deploy_to_kong(args.deploy, project_name)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
