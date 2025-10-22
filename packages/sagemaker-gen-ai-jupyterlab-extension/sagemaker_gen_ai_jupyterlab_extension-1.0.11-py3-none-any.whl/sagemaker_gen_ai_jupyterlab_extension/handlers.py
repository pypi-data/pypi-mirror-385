import json
from tornado import ioloop
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from tornado.web import StaticFileHandler
from .websocket_manager import manager
from .websocket_handler import WebSocketHandler
from .constants import SMD_CLIENTS_DIR
import logging
import os

logger = logging.getLogger('SageMakerGenAIJupyterLabExtension')
CLIENT_HTML_PATH = str(os.path.join(os.path.dirname(__file__), "static", "client.html"))

logger.debug(f"Client HTML: {CLIENT_HTML_PATH}")
logger.debug(f"SMD clients dir: {SMD_CLIENTS_DIR}")

class RouteHandler(APIHandler):
    # Removed authentication requirement for development
    def get(self):
        self.finish(json.dumps({
            "data": "This is /sagemaker_gen_ai_jupyterlab_extension/get-example endpoint!"
        }))



class DirectFileHandler(StaticFileHandler):
    """Handler to serve files directly from SageMaker Distribution artifacts"""
    
    def initialize(self, path):
        super().initialize(path)
    
    def get_content_type(self):
        """Ensures JavaScript files are served with correct content type"""
        if self.path.endswith('.js'):
            return 'text/javascript; charset=utf-8'
        return super().get_content_type()
    
    def set_extra_headers(self, path):
        """Enable cross-origin requests and prevent stale content"""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Cache-Control", "no-cache")
        super().set_extra_headers(path)

def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    # Add CORS headers to allow requests from any origin
    def _set_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type, authorization")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        
    # Handle OPTIONS requests for CORS preflight
    def _options(self):
        self.set_status(204)
        self.finish()

    try:
        # Patch the handler classes to add CORS headers and OPTIONS method
        RouteHandler.set_default_headers = _set_headers
        RouteHandler.options = _options

        route_pattern = url_path_join(base_url,"sagemaker_gen_ai_jupyterlab_extension", "get-example")
        websocket_pattern = url_path_join(base_url,"sagemaker_gen_ai_jupyterlab_extension", "ws")
        static_pattern = url_path_join(base_url, "sagemaker_gen_ai_jupyterlab_extension", "static") + "/(.*)"
        direct_file_pattern = url_path_join(base_url, "sagemaker_gen_ai_jupyterlab_extension", "direct") + "/(.*)"
        
        logger.debug(f"Base URL: {base_url}")
        
        amazonq_file = os.path.join(SMD_CLIENTS_DIR, 'amazonq-ui.js')
        if os.path.exists(SMD_CLIENTS_DIR):
            if os.path.exists(amazonq_file):
                logger.info("Amazon Q client artifacts verified")
            else:
                logger.warning(f"Client file not found: {amazonq_file}")
        else:
            logger.error(f"SMD clients directory not found: {SMD_CLIENTS_DIR}")
        
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        
        handlers = [
            (route_pattern, RouteHandler),
            (websocket_pattern, WebSocketHandler),
            (direct_file_pattern, DirectFileHandler, {"path": SMD_CLIENTS_DIR}),
            (static_pattern, StaticFileHandler, {"path": static_dir}),
        ]
        web_app.add_handlers(host_pattern, handlers)
        
        logger.info("Amazon Q handlers registered")

        # Set the IOLoop reference
        manager.set_io_loop(ioloop.IOLoop.current())

    except Exception as e:
        import traceback
        error_msg = f"Failed to setup Amazon Q extension handlers: {e}"
        stack_trace = traceback.format_exc()
        
        logger.error(f"Failed to setup handlers: {e}", exc_info=True)
    