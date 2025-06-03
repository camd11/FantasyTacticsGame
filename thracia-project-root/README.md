# Thracia-Mechanics Showcase

A project to showcase specific mechanics from Fire Emblem: Thracia 776 within the Lex Talionis engine.

## Environment Setup

Follow these steps to set up your local development environment.

### 1. Create a Python Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies. These instructions assume you are using Python 3.11.

Create a new virtual environment (e.g., named `.venv`):
```bash
python3.11 -m venv .venv
```

Activate the virtual environment:

*   On macOS and Linux:
    ```bash
    source .venv/bin/activate
    ```
*   On Windows:
    ```bash
    .\.venv\Scripts\activate
    ```
You should see the virtual environment name (e.g., `(.venv)`) in your terminal prompt.

### 2. Install Dependencies

Install the required dependencies from the Lex Talionis engine:
```bash
pip install -r ../lt-maker/requirements.txt
```
*(Note: The path to `requirements.txt` assumes `thracia-project-root` and `lt-maker` are sibling directories as per the typical project structure. Adjust the path if your directory layout is different.)*

### 3. Install Additional Packages (Optional)

As development progresses, other packages might be required. You can install them using pip. For example:

```bash
pip install numpy pytest
```
Replace `numpy` and `pytest` with the actual package names as needed.

## Documentation

For full documentation, see [docs/](docs/).

## License

[License Type Placeholder](LICENSE.md)