from sagemaker_gen_ai_jupyterlab_extension.constants import SMUS_CLIENT_INFO
from .pylspclient import LspClient, JsonRpcEndpoint, LspEndpoint
import subprocess
import os
import logging
from .extract_utils import extract_q_customization_arn
from .telemetry_collector import TelemetryCollector

logger = logging.getLogger('SageMakerGenAIJupyterLabExtension')

class LspServerConnection:
    def __init__(self):
        self.lsp_endpoint = None
        self.lsp_client = None
        self.send_client_notification = None
        self.send_client_request = None
        self.progress_callbacks = {}
    
    def start_lsp_server(self, node_path, executable_path, auth_mode=None):
        if auth_mode == "IAM":
            env = os.environ.copy()
            env["USE_IAM_AUTH"] = "true"
            lsp_process = subprocess.Popen([node_path, executable_path, "--stdio", "--inspect=6012", "--nolazy"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, env=env)
        else:
            lsp_process = subprocess.Popen([node_path, executable_path, "--stdio", "--inspect=6012", "--nolazy"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        
        json_rpc_endpoint = JsonRpcEndpoint(lsp_process.stdin, lsp_process.stdout)
        
        def on_progress_handler(params):
            logger.debug(f"Progress: {params.get('token', 'unknown')}")
            
            token = params.get('token')
            value = params.get('value')
            if token and token in self.progress_callbacks:
                self.progress_callbacks[token](value)
        
        def send_context_commands_handler(params):
            logger.debug("Received sendContextCommands")
            message = {
                "command": 'aws/chat/sendContextCommands',
                "params": params
            }
            self.send_client_notification(message)

        def send_pinned_context_handler(params):
            logger.debug("Received sendPinnedContext")
            message = {
                "command": 'aws/chat/sendPinnedContext',
                "params": params
            }
            self.send_client_notification(message)
            
        def send_chat_update_handler(params):
            logger.debug("Received sendChatUpdate")
            message = {
                "command": 'aws/chat/sendChatUpdate',
                "params": params
            }
            self.send_client_notification(message)
            
        def chat_options_update_handler(params):
            logger.debug("Received chatOptionsUpdate")
            message = {
                "command": 'aws/chat/chatOptionsUpdate',
                "params": params
            }
            self.send_client_notification(message)

        def open_diff_handler(params):
            logger.debug("Received openFileDiff")
            message = {
                "command": 'aws/openFileDiff',
                "params": params
            }
            self.send_client_notification(message)
        
        def open_tab_handler(params, rpc_id):
            logger.debug("Received openTab")
            message = {
                "command": 'aws/chat/openTab',
                "params": params
            }
            self.send_client_request(message, self.get_response_callback(rpc_id))

        def telemetry_handler(params):
            logger.debug("Received telemetry event")
            TelemetryCollector.collect_telemetry(params)

        self.lsp_endpoint = LspEndpoint(json_rpc_endpoint, 
            notify_callbacks={
                "$/progress": on_progress_handler,
                "aws/chat/sendContextCommands": send_context_commands_handler,
                "aws/chat/sendPinnedContext": send_pinned_context_handler,
                "aws/openFileDiff": open_diff_handler,
                "telemetry/event": telemetry_handler,
                "aws/chat/sendChatUpdate": send_chat_update_handler,
                "aws/chat/chatOptionsUpdate": chat_options_update_handler 
            },
            method_callbacks={
                "workspace/configuration": self.handle_workspace_configuration,
                "aws/chat/openTab": open_tab_handler
            },
            timeout=5000
        )

        self.lsp_client = LspClient(self.lsp_endpoint)

        return self.lsp_endpoint

    def initialize(self, workspace_folder):        
        self.lsp_client.initialize(
            processId=os.getpid(),
            rootPath=workspace_folder,
            rootUri=workspace_folder,
            capabilities={},
            # client info is used in Flare to set the origin as MD_IDE
            # in SendMessageStreaming/GenerateAssistantResponse requests.
            # https://github.com/aws/language-servers/commit/a1c33d1d7e2bbea693a6d8a9885491c1815f7f62
            clientInfo={"name": SMUS_CLIENT_INFO},
            initializationOptions={
                "logLevel": "info",
                "aws.optOutTelemetry": True,
                "aws": {
                    "awsClientCapabilities": {
                        "q": {
                            "developerProfiles": True,
                            "pinnedContextEnabled": False,
                            "mcp": True
                        },
                        "window": {
                            "notifications": True,
                            "showSaveFileDialog": True
                        }
                    },
                    "contextConfiguration": {},
                },
                "credentials": {
                    "providesBearerToken": True
                },
            },
            trace="on",                 
            workspaceFolders= [
                {
                    "uri": workspace_folder,
                    "name": "home"
                }
            ]
        )
        self.lsp_client.initialized()
    
    def get_response_callback(self, rpc_id):
        def response_callback(response):
            params = response.get('params', None)
            result = params.get('result', None)
            error = params.get('error', None)
            self.lsp_endpoint.send_response(rpc_id, result, error)
        return response_callback

    def on_progress(self, token, callBackFn, cancellation_token=None):
        """
        Register a callback function for a specific progress token.
        
        Args:
            token: The progress token to listen for
            callBackFn: The callback function to call when progress with this token is received
            cancellation_token: Optional cancellation token to check before calling callback
            
        Returns:
            A function that when called will remove this callback
        """
        def wrapped_callback(value):
            if cancellation_token and cancellation_token.isCancellationRequested:
                logger.debug(f"Cancellation requested for token: {token}")
                if token in self.progress_callbacks:
                    del self.progress_callbacks[token]
                return
            callBackFn(value)
            
        self.progress_callbacks[token] = wrapped_callback
        
        def dispose():
            if token in self.progress_callbacks:
                del self.progress_callbacks[token]
                
        return dispose

    def call_method(self, command, params):
        """
        Function that only takes in a command and params and calls the method.
        Uses the class's lsp_endpoint.
        """
        return self.lsp_endpoint.call_method(command, **params)
    
    def send_notification(self, method, params):
        """
        Function that only takes in a method and params and sends a notification.
        Uses the class's lsp_endpoint.
        """
        self.lsp_endpoint.send_notification(method, **params)

    def set_send_client_notification(self, send_client_notification):
        self.send_client_notification = send_client_notification

    def set_send_client_request(self, send_client_request):
        self.send_client_request = send_client_request

    def update_access_token(self, access_token, start_url):
        self.lsp_endpoint.call_method(
                "aws/credentials/token/update", 
                data={"token": access_token},
                metadata={
                    "sso": {
                        "startUrl": start_url
                    }
                })
        
    def update_q_profile(self, profile_arn):
        self.lsp_endpoint.call_method(
                "aws/updateConfiguration", section="aws.q", settings={"profileArn": profile_arn})
    
    def update_iam_credentials(self, access_key_id, secret_access_key, session_token, expiration_time):
        data = {
            "accessKeyId": access_key_id,
            "secretAccessKey": secret_access_key,
            "sessionToken": session_token,
            "expireTime": expiration_time
        }
        
        self.lsp_endpoint.call_method(
            "aws/credentials/iam/update", 
            data=data
        )
        
    def update_q_customization(self, customization_arn):   
        if not customization_arn:
            logger.info("No customization ARN provided, skipping update")
            return
  
        logger.info(f"Setting Q customization ARN: {customization_arn}")
  
        try:
            self.lsp_endpoint.send_notification(
                "workspace/didChangeConfiguration",
            )
            logger.info("Sent customization notification")
        except Exception as e:
            logger.error(f"Error sending customization notification: {e}", exc_info=True)
  
    def get_q_customizations(self):
        """Get available Q customizations from the server"""
        logger.info("Requesting Q customizations from server...")
        try:
            logger.info("Trying aws.q.customizations endpoint")
            response = self.lsp_endpoint.call_method(
                "aws/getConfigurationFromServer", section="aws.q.customizations")
            logger.info(f"Customizations response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error getting Q customizations: {e}", exc_info=True)
  
    def handle_workspace_configuration(self, params, rpc_id):
        """Handle workspace/configuration requests from the server"""
        if not params or "items" not in params:
            return []
  
        result = []
        for item in params["items"]:
            section = item.get("section", "")
            if section == "aws.q":
                result.append({"customization": extract_q_customization_arn() or ""})
            if section == "aws.optOutTelemetry":
                result.append(not self.get_telemetry_settings().get("optInToQTelemetry"))
            else:
                result.append(None)

        response = {
            "command": "workspace/configuration",
            "params": {
                "success": True,
                "result": result
            }
        }
        
        response_callback = self.get_response_callback(rpc_id)
        response_callback(response)
    
    def get_chat_response(self, chat_prompt):
        response = self.lsp_endpoint.call_method("aws/chat/sendChatPrompt", prompt={
                "prompt": chat_prompt
            })
        return response
    
    def get_telemetry_settings(self):
        """Fetch telemetry settings from JupyterLab user settings"""
        try:
            from pathlib import Path
            import json
            
            settings_path = Path.home() / ".jupyter/lab/user-settings/@amzn/sagemaker_gen_ai_jupyterlab_extension/plugin.jupyterlab-settings"
            
            if settings_path.exists():
                logger.info(f"Telemetry settings found at {settings_path}")
                with open(settings_path, 'r') as f:
                    logger.info("Reading telemetry settings")
                    return json.load(f)
            else:
                logger.info(f"Telemetry settings not found at {settings_path}")
                return {"optInToQTelemetry": False}
        except Exception as e:
            logger.error(f"Error reading telemetry settings: {e}", exc_info=True)
            return {"optInToQTelemetry": False}
    
    def stop_lsp_server(self):
        """Stop the LSP server following LSP shutdown specification"""
        try:
            if self.lsp_client:
                logger.info("Sending shutdown request to LSP server")
                self.lsp_client.shutdown()
                logger.info("Sending exit notification to LSP server")
                self.lsp_client.exit()
                logger.info("LSP server stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping LSP server: {e}", exc_info=True)
    
    def restart_lsp_server(self, node_path, executable_path, auth_mode, workspace_folder):
        """Restart LSP server with new auth mode"""
        try:
            logger.info(f"Restarting LSP server with auth mode: {auth_mode}")
            self.stop_lsp_server()
            self.start_lsp_server(node_path, executable_path, auth_mode)
            self.initialize(workspace_folder)
            logger.info("LSP server restarted successfully")
        except Exception as e:
            logger.error(f"Error restarting LSP server: {e}", exc_info=True)
            try:
                self.initialize(workspace_folder)
            except Exception as init_e:
                logger.error(f"Error reinitializing LSP server: {init_e}", exc_info=True)