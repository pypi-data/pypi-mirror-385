"""
Unit tests for Amazon Q offline-first architecture production changes.
Tests enhanced error handling, logging, and DirectFileHandler improvements for SageMaker Distribution.
"""
import pytest
import os
import logging
from unittest.mock import Mock, patch, MagicMock, call
from tornado.web import StaticFileHandler

# Mock watchdog before importing modules
with patch.dict('sys.modules', {
    'watchdog': Mock(),
    'watchdog.observers': Mock(),
    'watchdog.events': Mock()
}):
    import sagemaker_gen_ai_jupyterlab_extension as init_module
    from sagemaker_gen_ai_jupyterlab_extension.handlers import DirectFileHandler, setup_handlers


class TestAmazonQEnhancedErrorHandling:
    """Test enhanced error handling in Amazon Q extension loading"""
    
    def test_load_extension_with_structured_logging(self):
        """Test that Amazon Q extension errors are logged with proper structure and levels"""
        mock_server_app = Mock()
        mock_server_app.web_app = Mock()
        mock_server_app.log = Mock()
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.setup_handlers') as mock_setup:
            with patch('sagemaker_gen_ai_jupyterlab_extension.logger') as mock_logger:
                # Simulate Amazon Q LSP server initialization failure
                test_error = RuntimeError("Amazon Q LSP server initialization failed")
                mock_setup.side_effect = test_error
                
                # Call the function
                init_module._load_jupyter_server_extension(mock_server_app)
                
                # Verify Amazon Q extension logger (actual implementation)
                mock_logger.error.assert_called_with("Failed to load Amazon Q extension: Amazon Q LSP server initialization failed", exc_info=True)
    
    def test_graceful_degradation_on_amazon_q_error(self):
        """Test that Amazon Q extension errors don't crash JupyterLab"""
        mock_server_app = Mock()
        mock_server_app.web_app = Mock()
        mock_server_app.log = Mock()
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.setup_handlers') as mock_setup:
            mock_setup.side_effect = Exception("Amazon Q critical error")
            
            # Should not raise exception - graceful degradation
            result = init_module._load_jupyter_server_extension(mock_server_app)
            
            # Should return None for graceful degradation
            assert result is None


class TestAmazonQDirectFileHandler:
    """Test Amazon Q DirectFileHandler for SageMaker Distribution artifacts"""
    
    def test_inherits_from_static_file_handler(self):
        """Test that DirectFileHandler properly inherits from StaticFileHandler"""
        assert issubclass(DirectFileHandler, StaticFileHandler)
    
    def test_javascript_mime_type_override_for_amazonq_files(self):
        """Test that Amazon Q JavaScript files get correct MIME type"""
        mock_app = Mock()
        mock_app.ui_methods = {}
        mock_request = Mock()
        
        handler = DirectFileHandler(mock_app, mock_request, path="/test/path")
        handler.path = "amazonq-ui.js"
        
        content_type = handler.get_content_type()
        assert content_type == 'text/javascript; charset=utf-8'
    
    def test_cors_headers_for_amazonq_artifacts(self):
        """Test that CORS headers are properly set for Amazon Q artifacts"""
        mock_app = Mock()
        mock_app.ui_methods = {}
        mock_request = Mock()
        
        handler = DirectFileHandler(mock_app, mock_request, path="/test/path")
        handler.set_header = Mock()
        
        with patch.object(StaticFileHandler, 'set_extra_headers'):
            handler.set_extra_headers("amazonq/path")
            
            # Verify CORS headers for Amazon Q
            handler.set_header.assert_any_call("Access-Control-Allow-Origin", "*")
            handler.set_header.assert_any_call("Cache-Control", "no-cache")


class TestAmazonQArtifactValidation:
    """Test Amazon Q SageMaker Distribution artifact validation"""
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.os.path.exists')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.logger')
    def test_amazonq_artifact_validation_success(self, mock_logger, mock_exists):
        """Test successful Amazon Q artifact validation logging"""
        mock_web_app = Mock()
        mock_web_app.settings = {"base_url": "/"}
        mock_web_app.add_handlers = Mock()
        
        # Mock Amazon Q artifact existence
        def exists_side_effect(path):
            return True  # All Amazon Q paths exist
        mock_exists.side_effect = exists_side_effect
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager'):
            with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop'):
                setup_handlers(mock_web_app)
                
                # Verify Amazon Q success logging
                mock_logger.info.assert_any_call("Amazon Q client artifacts verified")
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.os.path.exists')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.logger')
    def test_amazonq_artifact_validation_missing_directory(self, mock_logger, mock_exists):
        """Test Amazon Q artifact validation when SageMaker Distribution directory is missing"""
        mock_web_app = Mock()
        mock_web_app.settings = {"base_url": "/"}
        mock_web_app.add_handlers = Mock()
        
        # Mock Amazon Q directory doesn't exist
        mock_exists.return_value = False
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager'):
            with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop'):
                setup_handlers(mock_web_app)
                
                # Verify Amazon Q error logging
                error_calls = [call for call in mock_logger.error.call_args_list 
                              if 'SMD clients directory not found' in str(call)]
                assert len(error_calls) > 0


class TestAmazonQProductionLogging:
    """Test Amazon Q production-ready logging configuration"""
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.logger')
    def test_amazonq_handler_setup_logging(self, mock_logger):
        """Test that Amazon Q handler setup is properly logged"""
        mock_web_app = Mock()
        mock_web_app.settings = {"base_url": "/amazonq"}
        mock_web_app.add_handlers = Mock()
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager'):
            with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop'):
                with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.os.path.exists', return_value=True):
                    setup_handlers(mock_web_app)
                    
                    # Verify Amazon Q configuration logging
                    mock_logger.info.assert_any_call("Amazon Q client artifacts verified")
                    mock_logger.info.assert_any_call("Amazon Q handlers registered")


class TestAmazonQLSPInitializationLogging:
    """Test Amazon Q LSP server initialization logging improvements"""
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.os.path.exists')
    @patch('sagemaker_gen_ai_jupyterlab_extension.logger')
    def test_amazonq_lsp_initialization_success_logging(self, mock_logger, mock_exists):
        """Test successful Amazon Q LSP initialization logging"""
        mock_exists.return_value = True
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.LspServerConnection'):
            with patch('sagemaker_gen_ai_jupyterlab_extension.CredentialManager'):
                with patch('sagemaker_gen_ai_jupyterlab_extension.extract_auth_mode', return_value='test'):
                    init_module.initialize_lsp_server()
                    
                    # Verify Amazon Q initialization logging
                    mock_logger.info.assert_any_call("Initializing Amazon Q LSP server")
                    mock_logger.info.assert_any_call("LSP server successfully initialized")
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.os.path.exists')
    @patch('sagemaker_gen_ai_jupyterlab_extension.logger')
    def test_amazonq_lsp_initialization_missing_artifacts_logging(self, mock_logger, mock_exists):
        """Test Amazon Q LSP initialization logging when SageMaker Distribution artifacts are unavailable"""
        mock_exists.return_value = False
        
        result = init_module.initialize_lsp_server()
        
        assert result is None
        
        # Verify Amazon Q error messages
        mock_logger.error.assert_any_call("LSP server not found at /etc/amazon-q-agentic-chat/artifacts/jupyterlab/servers/aws-lsp-codewhisperer.js. Ensure SageMaker Distribution environment.")


class TestAmazonQOfflineFirstDesign:
    """Test Amazon Q offline-first design validation"""
    
    def test_amazonq_no_external_dependencies(self):
        """Test that Amazon Q handlers don't reference external URLs"""
        from sagemaker_gen_ai_jupyterlab_extension.constants import SMD_CLIENTS_DIR, SMD_LSP_SERVER_PATH
        
        # Verify Amazon Q paths are local SageMaker Distribution paths
        assert SMD_CLIENTS_DIR.startswith('/etc/amazon-q-agentic-chat/')
        assert SMD_LSP_SERVER_PATH.startswith('/etc/amazon-q-agentic-chat/')
        assert 'http' not in SMD_CLIENTS_DIR
        assert 'http' not in SMD_LSP_SERVER_PATH
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.logger')
    def test_amazonq_offline_operation_messaging(self, mock_logger):
        """Test that Amazon Q offline operation is properly communicated in logs"""
        mock_web_app = Mock()
        mock_web_app.settings = {"base_url": "/"}
        mock_web_app.add_handlers = Mock()
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.os.path.exists', return_value=False):
            with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager'):
                with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop'):
                    setup_handlers(mock_web_app)
                    
                    # Verify Amazon Q error logging when artifacts missing
                    error_calls = [call for call in mock_logger.error.call_args_list 
                                 if 'SMD clients directory not found' in str(call)]
                    assert len(error_calls) > 0