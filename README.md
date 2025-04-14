# Kong Demo Generator (Refactored)

A tool that creates customized Kong API Gateway setups for demonstration purposes.

## Overview

This project has been refactored following SOLID principles to improve:
- Maintainability
- Testability
- Extensibility
- Reusability

## Architecture

The code has been divided into several components, each with a clear responsibility:

- **ConfigurationManager** - Handles storing, validating and managing Kong configuration data
- **UserInputCollector** - Interacts with the user to gather configuration details
- **TemplateRenderer** - Renders templates with provided data
- **FileSystemManager** - Manages all file operations and directory structure
- **KongAdminClient** - Handles interactions with the Kong Admin API
- **PluginStrategy** - Implements different strategies for Kong plugins
- **DemoProjectGenerator** - Orchestrates the overall process

## Usage
## 🚀 Getting Started

Follow these steps to set up and run your Groq-powered demo project.

---

### 1. Add Your Groq API Key

Create a `.env` file in the root of your project and add your Groq API key:

### 2. Run the Project
```env
GROQ_API_KEY=your_api_key_here

# Start an interactive demo setup
python main.py

# Generate a demo using a config file
python main.py --config my-config.json

# Deploy the generated demo to a running Kong instance
python main.py --deploy http://localhost:8001 --project my-demo
```

### 3. Navigate to Your Project Directory

```
cd output/<your-project-name>

```
## 4. Run the Setup Script

```
./setup.sh
```


## Features

- Interactive mode for creating custom Kong configurations
- Configuration file mode for reproducible demos
- Extensible plugin system
- Support for multiple authentication strategies
- Mock API implementations for testing
- Deployment to running Kong instances

## SOLID Principles Applied

The refactoring applies SOLID principles:

- **Single Responsibility Principle**: Each class has a single reason to change
- **Open/Closed Principle**: The system can be extended without modifying existing code (plugin strategies)
- **Liskov Substitution Principle**: Different implementations can substitute their base classes (KongAdminInterface)
- **Interface Segregation Principle**: Interfaces are focused and clients only depend on what they need
- **Dependency Inversion Principle**: High-level modules depend on abstractions, not implementations

## Extending the System

To add a new feature:

1. To add a new plugin type, extend the PluginStrategy class
2. To add a new authentication method, extend the AuthPluginStrategy class
3. To add a new deployment target, implement the KongAdminInterface 

## AI-Powered Mock API Architecture

The Kong Demo Generator now includes an improved architecture for generating domain-specific mock APIs using AI:

### Key Components

1. **MockApiGenerator** - Strategy pattern for different API generators
   - `BasicMockApiGenerator` - Simple CRUD APIs without AI
   - `AiMockApiGenerator` - Base class for AI-powered generators
     - Domain-specific implementations for insurance, e-commerce, etc.

2. **MockApiGeneratorFactory** - Factory pattern for creating the appropriate generator based on business type

### Extending with New Business Domains

To add support for a new business domain:

1. Create a new generator class that extends `AiMockApiGenerator`
2. Implement the `get_prompt_for_business_type` method
3. Add the new class to `MockApiGeneratorFactory.create_generator` 
