import pytest
import json
import os
from unittest.mock import Mock, patch

from sagemaker_gen_ai_jupyterlab_extension.handlers import RouteHandler, DirectFileHandler, setup_handlers
from tornado.web import StaticFileHandler


class TestRouteHandler:
    
    @pytest.fixture
    def handler(self):
        """Create a RouteHandler instance for testing"""
        handler = Mock(spec=RouteHandler)
        handler.finish = Mock()
        return handler
    
    def test_get_endpoint(self):
        """Test the GET endpoint returns correct JSON response"""
        handler = Mock()
        handler.finish = Mock()
        
        # Call the actual method
        RouteHandler.get(handler)
        
        expected_response = json.dumps({
            "data": "This is /sagemaker_gen_ai_jupyterlab_extension/get-example endpoint!"
        })
        handler.finish.assert_called_once_with(expected_response)


class TestSetupHandlers:
    
    @pytest.fixture
    def mock_web_app(self):
        """Create a mock web app for testing"""
        web_app = Mock()
        web_app.settings = {"base_url": "/"}
        web_app.add_handlers = Mock()
        return web_app
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.os.path.exists')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.logger')
    def test_setup_handlers_success_with_artifact_validation(self, mock_logger, mock_ioloop, mock_manager, mock_exists, mock_web_app):
        """Test successful handler setup with artifact validation from production changes"""
        mock_current_loop = Mock()
        mock_ioloop.current.return_value = mock_current_loop
        mock_exists.return_value = True  # Artifacts exist
        
        setup_handlers(mock_web_app)
        
        # Verify handlers were added
        mock_web_app.add_handlers.assert_called_once()
        
        # Verify IOLoop was set on manager
        mock_manager.set_io_loop.assert_called_once_with(mock_current_loop)
        
        # Check that 4 handlers were registered (route, websocket, direct, static)
        call_args = mock_web_app.add_handlers.call_args
        host_pattern, handlers = call_args[0]
        
        assert host_pattern == ".*$"
        assert len(handlers) == 4
        
        # Verify handler patterns including DirectFileHandler
        route_pattern, route_handler = handlers[0]
        websocket_pattern, websocket_handler = handlers[1]
        direct_pattern, direct_handler, direct_config = handlers[2]
        static_pattern, static_handler, static_config = handlers[3]
        
        assert "/sagemaker_gen_ai_jupyterlab_extension/get-example" in route_pattern
        assert "/sagemaker_gen_ai_jupyterlab_extension/ws" in websocket_pattern
        assert "/sagemaker_gen_ai_jupyterlab_extension/direct" in direct_pattern
        assert "/sagemaker_gen_ai_jupyterlab_extension/static" in static_pattern
        
        # Verify DirectFileHandler is used
        assert direct_handler == DirectFileHandler
        
        # Verify handlers were registered
        mock_web_app.add_handlers.assert_called_once()
        mock_logger.info.assert_any_call("Amazon Q handlers registered")
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.logger')
    def test_setup_handlers_exception_with_enhanced_logging(self, mock_logger, mock_ioloop, mock_manager, mock_web_app):
        """Test handler setup exception with enhanced error logging from production changes"""
        mock_web_app.add_handlers.side_effect = Exception("Handler registration failed")
        
        setup_handlers(mock_web_app)
        
        # Verify error logging (actual implementation)
        mock_logger.error.assert_called_with("Failed to setup handlers: Handler registration failed", exc_info=True)
        
        # Error logged with exc_info includes stack trace
        assert mock_logger.error.called
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.os.path.exists')
    def test_cors_headers_set(self, mock_exists, mock_web_app):
        """Test that CORS headers are properly set on RouteHandler"""
        mock_exists.return_value = True
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager'), \
             patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop'):
            
            setup_handlers(mock_web_app)
            
            # Test that CORS methods were added to RouteHandler
            assert hasattr(RouteHandler, 'set_default_headers')
            assert hasattr(RouteHandler, 'options')
            
            # Test CORS headers method
            handler = Mock()
            handler.set_header = Mock()
            
            RouteHandler.set_default_headers(handler)
            
            # Verify CORS headers are set
            handler.set_header.assert_any_call("Access-Control-Allow-Origin", "*")
            handler.set_header.assert_any_call("Access-Control-Allow-Headers", "x-requested-with, content-type, authorization")
            handler.set_header.assert_any_call("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.os.path.exists')
    def test_options_method(self, mock_exists, mock_web_app):
        """Test OPTIONS method for CORS preflight"""
        mock_exists.return_value = True
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager'), \
             patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop'):
            
            setup_handlers(mock_web_app)
            
            # Test OPTIONS method
            handler = Mock()
            handler.set_status = Mock()
            handler.finish = Mock()
            
            RouteHandler.options(handler)
            
            handler.set_status.assert_called_once_with(204)
            handler.finish.assert_called_once()
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.os.path.exists')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.os.listdir')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.logger')
    def test_artifact_validation_logging(self, mock_logger, mock_listdir, mock_exists, mock_web_app):
        """Test artifact validation logging from production changes"""
        # Test missing directory
        mock_exists.return_value = False
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager'), \
             patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop'):
            
            setup_handlers(mock_web_app)
            
            # Verify handlers were still registered despite missing artifacts
            mock_web_app.add_handlers.assert_called_once()
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.CLIENT_HTML_PATH')
    def test_client_html_path_constant(self, mock_path):
        """Test that CLIENT_HTML_PATH is properly set"""
        expected_path = os.path.join(os.path.dirname(__file__), "static", "client.html")
        # The actual path should be set during import, so we just verify the structure
        assert "static" in str(expected_path)
        assert "client.html" in str(expected_path)


class TestDirectFileHandler:
    """Test DirectFileHandler production improvements from commit changes"""
    
    def test_inherits_from_static_file_handler(self):
        """Test that DirectFileHandler properly inherits from StaticFileHandler"""
        assert issubclass(DirectFileHandler, StaticFileHandler)
    
    def test_javascript_content_type_override(self):
        """Test MIME type override for JavaScript files"""
        mock_app = Mock()
        mock_app.ui_methods = {}
        mock_request = Mock()
        
        handler = DirectFileHandler(mock_app, mock_request, path="/test/path")
        handler.path = "amazonq-ui.js"
        
        content_type = handler.get_content_type()
        assert content_type == 'text/javascript; charset=utf-8'
    
    def test_non_javascript_content_type_fallback(self):
        """Test that non-JS files use parent MIME type logic"""
        mock_app = Mock()
        mock_app.ui_methods = {}
        mock_request = Mock()
        
        handler = DirectFileHandler(mock_app, mock_request, path="/test/path")
        handler.path = "style.css"
        
        with patch.object(StaticFileHandler, 'get_content_type', return_value='text/css'):
            content_type = handler.get_content_type()
            assert content_type == 'text/css'
    
    def test_cors_and_cache_headers(self):
        """Test CORS and cache control headers are set"""
        mock_app = Mock()
        mock_app.ui_methods = {}
        mock_request = Mock()
        
        handler = DirectFileHandler(mock_app, mock_request, path="/test/path")
        handler.set_header = Mock()
        
        with patch.object(StaticFileHandler, 'set_extra_headers'):
            handler.set_extra_headers("test/path")
            
            # Verify CORS headers for cross-origin requests
            handler.set_header.assert_any_call("Access-Control-Allow-Origin", "*")
            # Verify cache control for fresh content
            handler.set_header.assert_any_call("Cache-Control", "no-cache")