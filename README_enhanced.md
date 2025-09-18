# NodeBox Enhanced - Visual Automation Platform

**NodeBox Enhanced** is a powerful visual automation platform that combines the flexibility of Python with an intuitive drag-and-drop interface. Built for developers and automation enthusiasts who want to create complex workflows without compromising on functionality.

## Key Features

### Core Functionality
- **Visual Node Editor**: Drag, drop, and connect Python-powered nodes
- **Local AI Integration**: Deep integration with Ollama for local AI workflows
- **Python Native**: Each node is pure Python code with full flexibility
- **Cross-Platform**: Runs on Windows, macOS, and Linux

### Enhanced Features (New in v2.0)

#### Node Templates
- **Pre-built Templates**: Common automation patterns ready to use
- **Categories**: Organized by function (Data Processing, Web, Database, etc.)
- **Custom Templates**: Create and share your own node templates
- **Quick Start**: Get up and running with proven patterns

#### Workflow Scheduler
- **Built-in Scheduling**: Schedule automations to run automatically
- **Multiple Schedule Types**: One-time, interval, and cron-style scheduling
- **Visual Management**: Easy-to-use interface for managing schedules
- **Status Monitoring**: Track execution history and status

#### Debug Console
- **Real-time Logging**: Monitor node execution and workflow progress
- **Performance Metrics**: Track execution times and error rates
- **Filtered Views**: Filter logs by level, node, or time
- **Export Capabilities**: Export logs for analysis

#### Performance Monitor
- **System Metrics**: Real-time CPU, memory, and disk usage
- **NodeBox Metrics**: Track active nodes, execution times, and errors
- **Historical Data**: View performance trends over time
- **Resource Alerts**: Visual indicators for high resource usage

#### Export/Import System
- **Workflow Sharing**: Export and import complete workflows
- **Bundle Support**: Include models and data with workflows
- **Version Control**: Track workflow versions and changes
- **Team Collaboration**: Share automations with your team

## Installation

### Prerequisites
- Python 3.10 or higher
- Ollama (for AI features)
- Git

### Quick Start
```bash
# Clone the repository
git clone https://github.com/your-username/NodeBox.git
cd NodeBox

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Ollama (in a separate terminal)
ollama serve

# Run NodeBox Enhanced
python main.py
```

## Getting Started

### 1. Create Your First Automation
1. Launch NodeBox Enhanced
2. Click "Create New Automation"
3. Give your automation a name
4. Click "Edit" to open the visual editor

### 2. Add Nodes
1. Right-click on the canvas to add a node
2. Choose from templates or create custom nodes
3. Double-click nodes to edit their Python code
4. Connect nodes by dragging from output to input ports

### 3. Use Node Templates
1. Go to the "Node Templates" tab
2. Browse available templates by category
3. Select a template and click "Load"
4. Customize the generated code as needed

### 4. Schedule Your Workflow
1. Go to the "Scheduler" tab
2. Click "Add Schedule"
3. Select your automation and set timing
4. Enable the schedule to start automatic execution

### 5. Monitor Performance
1. Use the "Debug Console" to monitor execution
2. Check the "Performance" tab for system metrics
3. Export logs and metrics for analysis

## Node Templates

NodeBox Enhanced comes with pre-built templates for common tasks:

### Data Processing
- **Text Processor**: Transform and clean text data
- **Data Validator**: Validate and clean structured data
- **CSV Handler**: Read, write, and process CSV files

### Web & APIs
- **HTTP Request**: Make API calls and web requests
- **Web Scraper**: Extract data from websites
- **JSON Parser**: Process JSON data

### File Operations
- **File Watcher**: Monitor file system changes
- **File Organizer**: Automatically organize files
- **Backup Manager**: Create automated backups

### Database
- **Database Connector**: Connect to various databases
- **Query Executor**: Run database queries
- **Data Migrator**: Move data between systems

### Communication
- **Email Sender**: Send automated emails
- **Notification Manager**: Send system notifications
- **Slack Integration**: Post to Slack channels

## Advanced Features

### Custom Node Development
```python
def process(input_data):
    # Your custom logic here
    result = input_data.upper()
    return result
```

### Workflow Scheduling
- **Interval Scheduling**: Run every X minutes/hours
- **Cron-style Scheduling**: Complex time-based schedules
- **One-time Execution**: Run once at a specific time

### Performance Optimization
- **Resource Monitoring**: Track CPU, memory, and disk usage
- **Execution Profiling**: Identify performance bottlenecks
- **Error Tracking**: Monitor and analyze errors

### Team Collaboration
- **Workflow Export**: Share complete workflows
- **Version Control**: Track changes and versions
- **Documentation**: Built-in documentation system

## Use Cases

### Data Automation
- Process large datasets automatically
- Clean and validate data from multiple sources
- Generate reports and analytics

### Web Automation
- Monitor websites for changes
- Scrape data from multiple sources
- Automate form submissions

### System Administration
- Monitor system health and performance
- Automate backup and maintenance tasks
- Send alerts for critical events

### AI-Powered Workflows
- Process text with local AI models
- Generate content automatically
- Analyze data with machine learning

### Business Process Automation
- Automate repetitive business tasks
- Integrate different systems and APIs
- Create custom business logic

## Architecture

NodeBox Enhanced is built with a modular architecture:

- **Core Engine**: PyQt6-based visual editor
- **Node System**: Python-based node execution
- **Scheduler**: Built-in workflow scheduling
- **Monitoring**: Real-time performance tracking
- **Templates**: Extensible node template system

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Run linting
python -m flake8
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [nodeboxlab.web.app](https://nodeboxlab.web.app)
- **Issues**: [GitHub Issues](https://github.com/your-username/NodeBox/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/NodeBox/discussions)

## Changelog

### v2.0.0 (Enhanced)
- Added Node Templates system
- Implemented Workflow Scheduler
- Added Debug Console with real-time logging
- Created Performance Monitor
- Built Export/Import system
- Enhanced UI with tabbed interface
- Improved error handling and logging
- Added system resource monitoring

### v1.0.0 (Original)
- Basic visual node editor
- Ollama integration
- Python node execution
- Canvas-based workflow design

---

**NodeBox Enhanced** - Where Python meets visual automation.
