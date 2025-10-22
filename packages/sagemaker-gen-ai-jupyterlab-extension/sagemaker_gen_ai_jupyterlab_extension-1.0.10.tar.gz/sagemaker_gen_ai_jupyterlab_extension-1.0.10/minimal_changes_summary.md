# Minimal Changes Required for Local LSP Artifacts

## Core Changes (Essential)

### 1. constants.py - Add artifact paths
```python
# SageMaker Distribution artifact paths
LSP_SERVER_FILENAME = "aws-lsp-codewhisperer.js"
SMD_LSP_SERVER_PATH = f"/etc/amazon-q-agentic-chat/artifacts/jupyterlab/servers/{LSP_SERVER_FILENAME}"
SMD_CLIENTS_DIR = "/etc/amazon-q-agentic-chat/artifacts/jupyterlab/clients"
```

### 2. __init__.py - Replace download logic with local path
- Remove: `download_and_extract_lsp_server()` function
- Remove: All download-related imports (requests, zipfile, tempfile, pathlib)
- Remove: `LSP_EXECUTABLE_PATH` global variable
- Add: Check for `SMD_LSP_SERVER_PATH` existence
- Update: Use `SMD_LSP_SERVER_PATH` in LSP server initialization

### 3. handlers.py - Add client file handler
- Add: `DirectFileHandler` class
- Add: Route for `/direct/` pattern
- Import: `SMD_CLIENTS_DIR` from constants

### 4. client.html - Use local client
- Remove: JSZip and external download logic
- Replace: External client loading with local `/direct/amazonq-ui.js`
- Update: CSP to remove external domains

### 5. credential_manager.py - Update import
- Replace: Import of global `LSP_EXECUTABLE_PATH`
- Add: Import of `SMD_LSP_SERVER_PATH` from constants

## Removable Changes (Non-essential)

- All README.md documentation additions
- Version number changes
- All test file modifications
- CHANGELOG.md and RELEASE.md updates
- Enhanced error handling (basic error handling sufficient)
- Extensive logging improvements

## Result
With just these 5 core changes, the extension will work with local LSP artifacts without any external dependencies.