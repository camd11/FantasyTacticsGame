# Development Environment Setup

This guide will help you set up your development environment for the Fantasy Tactics Game project.

## System Requirements

- Python 3.10 or higher
- Git
- Operating Systems:
  - Windows 10/11
  - macOS 10.15+
  - Linux (Ubuntu 20.04+ or similar)

## Quick Setup

For a quick setup, use the provided scripts:

### Windows

```bash
setup_venv.bat
```

### macOS/Linux

```bash
./setup_venv.sh
```

## Manual Setup

If the quick setup doesn't work for your environment, follow these steps:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd FantasyTacticsGame-1
```

### 2. Create and Activate a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Project Structure

The project is organized as follows:

- `assets/` - Game assets (sprites, sounds, tiles, UI)
- `data/` - Game data files (chapters, scenarios)
- `docs/` - Project documentation
- `logs/` - Log files
- `src/` - Source code
- `tests/` - Test files
- `tools/` - Utility scripts

## Running the Game

To run the game:

```bash
python src/main.py
```

Or use the provided launch script:

#### Windows

```bash
Launch.bat
```

#### macOS/Linux

```bash
./launch.sh
```

## Command Line Arguments

The game supports several command line arguments:

```bash
python src/main.py [options]
```

Options:
- `--no-audio`: Disable audio
- `--debug`: Enable debug mode
- `--scenario <path>`: Load a specific scenario
- `--ai-vs-ai`: Run the game in AI vs AI mode for testing

For a complete list of command line arguments, see [Technical Documentation](technical.md).

## Editor Setup

### Visual Studio Code

1. Install the Python extension
2. Set the Python interpreter to your virtual environment
3. Install the Pylint extension for linting
4. Configure workspace settings:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false
}
```

## Common Issues

### Pygame Installation

If you encounter issues installing Pygame:

#### Windows

```bash
pip install pygame --pre
```

#### macOS

```bash
pip install pygame==2.1.2
```

### Path Issues

If you encounter path-related errors, ensure that:

1. You are running commands from the project root directory
2. Your virtual environment is activated
3. The `PYTHONPATH` includes the project root:

#### Windows

```bash
set PYTHONPATH=%PYTHONPATH%;.
```

#### macOS/Linux

```bash
export PYTHONPATH=$PYTHONPATH:.
```

## Next Steps

After completing the setup:

1. Read the [Project Status](status.md) to understand the current state
2. Check out the [Testing Guide](testing.md) to learn how to run tests
3. Review the [Technical Documentation](technical.md) for detailed information

## Troubleshooting

If you encounter issues with the setup:

1. Verify you have the correct Python version installed
2. Check that all dependencies are correctly installed
3. Look for error messages in the console
4. Check log files in the `logs/` directory
5. Clear cache files with `tools/cleanup_cache.py` if needed

For more help, consult the project documentation or reach out to the development team. 