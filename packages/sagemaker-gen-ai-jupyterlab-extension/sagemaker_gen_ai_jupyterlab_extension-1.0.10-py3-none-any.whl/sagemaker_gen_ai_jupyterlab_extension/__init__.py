"""
SMUS Flare JupyterLab extension for AWS Q integration
"""
try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings
    warnings.warn("Importing 'SageMakerGenAIJupyterLabExtension' outside a proper installation.")
    __version__ = "dev"
from .handlers import setup_handlers
from .request_logger import init_api_operation_logger
import logging
import os
from .lsp_server_connection import LspServerConnection
from .extract_utils import extract_q_customization_arn, extract_q_settings, extract_auth_mode
from .q_customization import QCustomization
from .credential_manager import CredentialManager
from .constants import SMD_LSP_SERVER_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SageMakerGenAIJupyterLabExtension')

if os.getenv('JUPYTER_LOG_LEVEL') == 'DEBUG':
    logger.setLevel(logging.DEBUG)

NODE_PATH = "/opt/conda/bin/node"
WORKSPACE_FOLDER = "file:///home/sagemaker-user"

# Global variable to store the LSP connection
lsp_connection = None

# Global variable to store the credential manager
credential_manager = None

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "sagemaker_gen_ai_jupyterlab_extension"
    }]

__version__ = '1.0.10'

def get_lsp_connection():
    """
    Returns the initialized LSP connection.
    """
    global lsp_connection
    return lsp_connection

def get_credential_manager():
    """
    Returns the initialized credential manager.
    """
    global credential_manager
    return credential_manager

def chat_with_prompt(prompt):
    """
    Frontend-facing function that only requires a prompt.
    Uses the pre-initialized LSP connection from __init__.py.
    
    Args:
        prompt (str): The chat prompt from the user
        
    Returns:
        dict: The response from the LSP server
    """
    lsp_connection = get_lsp_connection()
    return lsp_connection.get_chat_response(prompt)

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "sagemaker_gen_ai_jupyterlab_extension"
    }]

q_customization = None

def initialize_lsp_server():
    """Initialize LSP server with SageMaker Distribution artifacts"""
    
    # TODO: Recommended: Create ExtensionState class to encapsulate all state management instead of using global variables
    global lsp_connection, credential_manager, q_customization

    logger.info("Initializing Amazon Q LSP server")
    
    if not os.path.exists(SMD_LSP_SERVER_PATH):
        logger.error(f"LSP server not found at {SMD_LSP_SERVER_PATH}. Ensure SageMaker Distribution environment.")
        return None

    # Initialize the LSP connection when the extension loads
    logger.info(f"Starting LSP server with executable {SMD_LSP_SERVER_PATH}")
    auth_mode = extract_auth_mode()
    lsp_connection = LspServerConnection()
    lsp_connection.start_lsp_server(NODE_PATH, SMD_LSP_SERVER_PATH, auth_mode)
    lsp_connection.initialize(WORKSPACE_FOLDER)
    
    # Initialize credential manager and setup credentials
    credential_manager = CredentialManager(lsp_connection, auth_mode)
    credential_manager.initialize_credentials()
    
    # Update Q profile and customization (only for paid tier)
    from .extract_utils import AuthMode
    if auth_mode == AuthMode.IDC.value:
        # Initialize customization ARN and start file watcher
        customization_arn = extract_q_customization_arn()
        q_customization = QCustomization(lsp_connection)
        q_customization.start_customization_file_watcher()
        q_settings = extract_q_settings()
        if q_settings:
            lsp_connection.update_q_profile(q_settings)
        
        if customization_arn:
            lsp_connection.update_q_customization(customization_arn)
    logger.info("LSP server successfully initialized")
    return lsp_connection
    

def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    try:
        setup_handlers(server_app.web_app)
        init_api_operation_logger(server_app.log)
        initialize_lsp_server()
        name = "sagemaker_gen_ai_jupyterlab_extension"
        server_app.log.info(f"Registered {name} server extension")
    except Exception as e:
        import traceback
        error_msg = f"Failed to load Amazon Q extension: {e}"
        stack_trace = traceback.format_exc()
        
        logger.error(f"Failed to load Amazon Q extension: {e}", exc_info=True)
        return

def _unload_jupyter_server_extension(server_app):
    """Unload the extension and stop the LSP server."""
    logger.info("In unload method")
    
    global lsp_connection, credential_manager, q_customization
    try:
        if credential_manager:
            credential_manager.cleanup()
            credential_manager = None
    except Exception as e:
        logger.error(f"Error cleaning up credential manager: {e}", exc_info=True)

    try:
        if q_customization:
            q_customization.stop_watcher_for_customization_file()
    except Exception as e:
        logger.error(f"Error stopping customization file watcher: {e}", exc_info=True)
