from unittest.mock import Mock, patch
from pathlib import Path

# Mock watchdog before importing the module
with patch.dict('sys.modules', {
    'watchdog': Mock(),
    'watchdog.observers': Mock(),
    'watchdog.events': Mock()
}):
    # Import the module under test
    import sagemaker_gen_ai_jupyterlab_extension as init_module
    from sagemaker_gen_ai_jupyterlab_extension.extract_utils import AuthMode
    from sagemaker_gen_ai_jupyterlab_extension.constants import SMD_LSP_SERVER_PATH


class TestInitModule:
    
    def test_version_exists(self):
        """Test that version is set"""
        assert hasattr(init_module, '__version__')
        assert init_module.__version__ is not None

    def test_constants(self):
        """Test module constants are properly set"""
        assert init_module.NODE_PATH == "/opt/conda/bin/node"
        assert init_module.WORKSPACE_FOLDER == "file:///home/sagemaker-user"
        # Check that global variables exist
        assert hasattr(init_module, 'lsp_connection')
        assert hasattr(init_module, 'credential_manager')

    # Token and settings extraction tests moved to test_extract_utils.py

    def test_jupyter_labextension_paths(self):
        """Test JupyterLab extension paths configuration"""
        paths = init_module._jupyter_labextension_paths()
        
        expected = [{
            "src": "labextension",
            "dest": "sagemaker_gen_ai_jupyterlab_extension"
        }]
        assert paths == expected

    def test_get_lsp_connection(self):
        """Test getting LSP connection"""
        # Mock the global lsp_connection
        mock_connection = Mock()
        with patch.object(init_module, 'lsp_connection', mock_connection):
            result = init_module.get_lsp_connection()
            assert result == mock_connection
    
    def test_get_credential_manager(self):
        """Test getting credential manager"""
        # Mock the global credential_manager
        mock_manager = Mock()
        with patch.object(init_module, 'credential_manager', mock_manager):
            result = init_module.get_credential_manager()
            assert result == mock_manager

    def test_chat_with_prompt(self):
        """Test chat with prompt function"""
        mock_connection = Mock()
        mock_connection.get_chat_response.return_value = {"response": "test"}
        
        with patch.object(init_module, 'get_lsp_connection', return_value=mock_connection):
            result = init_module.chat_with_prompt("test prompt")
            
            assert result == {"response": "test"}
            mock_connection.get_chat_response.assert_called_once_with("test prompt")

    
    def test_load_jupyter_server_extension_success(self):
        """Test successful loading of Jupyter server extension"""
        # Setup mocks
        mock_server_app = Mock()
        mock_server_app.web_app = Mock()
        mock_server_app.log = Mock()
        with patch('sagemaker_gen_ai_jupyterlab_extension.setup_handlers') as mock_setup:    
            # Call the function
            init_module._load_jupyter_server_extension(mock_server_app)
            # Verify calls
            mock_setup.assert_called_once_with(mock_server_app.web_app)
            

    def test_unload_jupyter_server_extension(self):
        """Test unloading Jupyter server extension"""
        # Create mocks
        mock_server_app = Mock()
        mock_cred_manager = Mock()
        mock_q_custom = Mock()
        
        with patch.object(init_module, 'credential_manager', mock_cred_manager):
            with patch.object(init_module, 'q_customization', mock_q_custom):
                # Call the function
                init_module._unload_jupyter_server_extension(mock_server_app)
                
                # Verify calls
                mock_cred_manager.cleanup.assert_called_once()
                mock_q_custom.stop_watcher_for_customization_file.assert_called_once()

    def test_unload_jupyter_server_extension_with_exception(self):
        """Test unloading Jupyter server extension with exception"""
        # Create mocks
        mock_server_app = Mock()
        mock_cred_manager = Mock()
        mock_cred_manager.cleanup.side_effect = Exception("Cleanup error")
        
        with patch.object(init_module, 'credential_manager', mock_cred_manager):
            with patch.object(init_module, 'logger') as mock_logger:
                # Call the function
                init_module._unload_jupyter_server_extension(mock_server_app)
                
                # Verify error was logged with exc_info
                mock_logger.error.assert_called_with("Error cleaning up credential manager: Cleanup error", exc_info=True)



    def test_load_jupyter_server_extension_with_enhanced_error_handling(self):
        """Test enhanced error handling with structured logging from production changes"""
        mock_server_app = Mock()
        mock_server_app.web_app = Mock()
        mock_server_app.log = Mock()
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.setup_handlers') as mock_setup:
            with patch('sagemaker_gen_ai_jupyterlab_extension.logger') as mock_logger:
                mock_setup.side_effect = RuntimeError("LSP server unavailable")
                
                init_module._load_jupyter_server_extension(mock_server_app)
                
                # Test structured logging - actual implementation doesn't use server_app.log
                mock_logger.error.assert_called_with("Failed to load Amazon Q extension: LSP server unavailable", exc_info=True)
                
                # Test that error was logged with exc_info (includes stack trace)
                assert mock_logger.error.called
    
    def test_load_jupyter_server_extension_graceful_degradation(self):
        """Test that extension failures don't crash JupyterLab"""
        mock_server_app = Mock()
        mock_server_app.web_app = Mock()
        mock_server_app.log = Mock()
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.setup_handlers') as mock_setup:
            mock_setup.side_effect = Exception("Critical failure")
            
            # Should not raise exception - graceful degradation
            result = init_module._load_jupyter_server_extension(mock_server_app)
            assert result is None



    @patch('sagemaker_gen_ai_jupyterlab_extension.os.path.exists')
    def test_initialize_lsp_server_with_enhanced_logging(self, mock_exists):
        """Test LSP server initialization with enhanced production logging"""
        mock_exists.return_value = True
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.LspServerConnection') as mock_lsp_class:
            with patch('sagemaker_gen_ai_jupyterlab_extension.CredentialManager'):
                with patch('sagemaker_gen_ai_jupyterlab_extension.QCustomization'):
                    with patch('sagemaker_gen_ai_jupyterlab_extension.extract_auth_mode') as mock_auth:
                        with patch('sagemaker_gen_ai_jupyterlab_extension.logger') as mock_logger:
                            mock_auth.return_value = "test_auth"
                            mock_lsp = Mock()
                            mock_lsp_class.return_value = mock_lsp
                            
                            init_module.initialize_lsp_server()
                            
                            # Test logging messages (actual implementation)
                            mock_logger.info.assert_any_call("Initializing Amazon Q LSP server")
                            mock_logger.info.assert_any_call("LSP server successfully initialized")
                            
                            mock_lsp.start_lsp_server.assert_called_once_with(
                                init_module.NODE_PATH,
                                SMD_LSP_SERVER_PATH,
                                "test_auth"
                            )

    @patch('sagemaker_gen_ai_jupyterlab_extension.os.path.exists')
    def test_initialize_lsp_server_missing_artifacts_enhanced_logging(self, mock_exists):
        """Test enhanced logging when SageMaker Distribution artifacts are unavailable"""
        mock_exists.return_value = False
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.logger') as mock_logger:
            result = init_module.initialize_lsp_server()
            
            assert result is None
            
            # Test error message (actual implementation)
            mock_logger.error.assert_any_call(f"LSP server not found at {SMD_LSP_SERVER_PATH}. Ensure SageMaker Distribution environment.")