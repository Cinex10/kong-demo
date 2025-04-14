#!/usr/bin/env python3
"""
Test script for the enhanced Mock API Generator
"""

import os
import json
from ai_model_client import GroqAiModelClient
from mock_api_generator import BasicMockApiGenerator, EcommerceMockApiGenerator

def main():
    """Test the mock API generator enhancements"""
    print("Testing Mock API Generator enhancements...")
    
    # Create a basic mock API generator
    ai_client = GroqAiModelClient()
    generator = EcommerceMockApiGenerator(ai_client)
    
    # Generate a mock API
    service_name = "test-store"
    business_type = "ecommerce"
    params = {
        "features": ["basic", "inventory-management"]
    }
    
    # Generate the API files
    api_files = generator.generate_mock_api(service_name, business_type, params)
    
    # Create output directory
    os.makedirs("test_output", exist_ok=True)
    
    # Write the files to test_output directory
    for filename, content in api_files.items():
        filepath = os.path.join("test_output", filename)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Generated {filepath}")
    
    # Print the file sizes to verify they're reasonable
    for filename in api_files.keys():
        filepath = os.path.join("test_output", filename)
        size = os.path.getsize(filepath)
        print(f"File: {filename}, Size: {size} bytes")
    
    print("Test completed successfully!")

if __name__ == "__main__":
    main() 