# Terraform Module Generator

A tool to generate Terraform modules from documentation using AI, with both CLI and GUI interfaces.

## Installation

1. Clone the repository
2. Install the package:
```bash
cd tfgen
pip install -e .
```

## Usage

### GUI Interface

Run the GUI application using either:
```bash
tfgen-ui
```
or
```bash
python -m tfgen.ui
```

### Command Line Interface

Run the CLI tool:
```bash
tfgen --url <terraform-resource-url> [--generate]
```

## Features

- Generate Terraform modules from documentation
- Support for both regular Terraform resources and Azure REST API resources
- Modern GUI interface with real-time feedback
- Command-line interface for automation
- Progress tracking and status indicators

## Requirements

- Python 3.8 or higher
- Required packages (automatically installed):
  - playwright
  - beautifulsoup4
  - openai
  - python-dotenv
  - Pillow

## Environment Variables

Create a `.env` file with:
```
ENDPOINT_URL=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
``` 