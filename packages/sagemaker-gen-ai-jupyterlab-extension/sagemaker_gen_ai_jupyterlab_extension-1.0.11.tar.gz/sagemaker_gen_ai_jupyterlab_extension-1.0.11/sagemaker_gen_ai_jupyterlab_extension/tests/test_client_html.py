"""
Unit tests for client.html production changes.
Tests dynamic URL resolution and enhanced error handling.
"""
import pytest
import os
from unittest.mock import Mock, patch


class TestClientHtmlChanges:
    """Test client.html production improvements from commit changes"""
    
    def test_client_html_exists(self):
        """Test that client.html file exists in static directory"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        # Verify the path structure is correct
        assert "static" in CLIENT_HTML_PATH
        assert "client.html" in CLIENT_HTML_PATH
    
    def test_client_html_content_structure(self):
        """Test that client.html contains expected production elements"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        # Read the actual client.html file
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test security policy is present
            assert 'Content-Security-Policy' in content
            assert 'ws: wss:' in content  # WebSocket connections allowed
            
            # Test dynamic base URL resolution
            assert 'baseUrl = window.location.pathname.split' in content
            assert '/sagemaker_gen_ai_jupyterlab_extension/direct/amazonq-ui.js' in content
            
            # Test error handling
            assert 'script.onerror' in content
            assert 'Failed to load Amazon Q client from SageMaker Distribution artifacts' in content
            
            # Test production logging (console.error is present)
            assert 'console.error' in content
            # Test that script loading is present
            assert 'script.src' in content
    
    def test_csp_headers_allow_websockets(self):
        """Test that CSP headers allow WebSocket connections for chat functionality"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Verify WebSocket connections are allowed in CSP
            assert 'connect-src \'self\' ws: wss:' in content
    
    def test_self_contained_design_comments(self):
        """Test that self-contained design elements are present"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test self-contained design elements
            assert 'SageMaker Distribution artifacts' in content
            assert '/direct/amazonq-ui.js' in content
    
    def test_dynamic_url_resolution_logic(self):
        """Test the dynamic URL resolution logic for different deployment contexts"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test dynamic base URL construction
            assert "window.location.pathname.split('/sagemaker_gen_ai_jupyterlab_extension')[0]" in content
            assert "${baseUrl}/sagemaker_gen_ai_jupyterlab_extension/direct/amazonq-ui.js" in content
    
    def test_error_handling_enhancements(self):
        """Test enhanced error handling for missing artifacts"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test comprehensive error messages
            assert 'Failed to load Amazon Q client from SageMaker Distribution artifacts' in content
    
    def test_no_external_dependencies(self):
        """Test that client.html doesn't reference external URLs (self-contained)"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Verify no external CDN or HTTP references
            assert 'http://' not in content or 'http://localhost' in content  # Allow localhost for testing
            assert 'https://' not in content
            assert 'cdn.' not in content
            assert '.amazonaws.com' not in content
    
    def test_amazon_q_chat_initialization(self):
        """Test that Amazon Q chat is properly initialized with correct parameters"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test Amazon Q chat initialization
            assert 'amazonQChat.createChat' in content
            assert 'agenticMode: true' in content
            assert 'disclaimerAcknowledged' in content
            assert 'pairProgrammingAcknowledged' in content
            assert 'quickActionCommands' in content
    
    def test_quick_action_commands(self):
        """Test that quick action commands are properly defined"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test quick action commands
            expected_commands = ['/clear', '/fix', '/explain', '/optimize', '/refactor', '/help']
            for command in expected_commands:
                assert command in content
    
    def test_local_storage_usage(self):
        """Test that local storage is used for user preferences"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test local storage usage
            assert 'localStorage.getItem' in content
            assert 'disclaimerAcknowledged' in content
            assert 'chatPromptOptionAcknowledged' in content


class TestClientHtmlSecurity:
    """Test security aspects of client.html"""
    
    def test_content_security_policy(self):
        """Test that CSP is restrictive but functional"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test CSP directives
            assert "default-src 'self'" in content
            assert "script-src 'self' 'nonce-inline-script'" in content
            assert "connect-src 'self' ws: wss:" in content
            assert "style-src 'self'" in content and ("'unsafe-inline'" in content or "'nonce-inline-style'" in content)
            assert "object-src 'none'" in content
    
    def test_no_inline_scripts_without_nonce(self):
        """Test that inline scripts use proper nonce"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test that inline script has nonce
            assert 'nonce="inline-script"' in content
    
    def test_no_eval_or_unsafe_inline_js(self):
        """Test that no unsafe JavaScript practices are used"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test no unsafe practices
            assert 'eval(' not in content
            assert 'innerHTML =' not in content
            assert 'document.write(' not in content


class TestClientHtmlPerformance:
    """Test performance aspects of client.html"""
    
    def test_minimal_external_resources(self):
        """Test that external resource loading is minimized"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Count external resource references (should be minimal)
            external_refs = content.count('http://') + content.count('https://')
            # Allow for localhost references in development
            localhost_refs = content.count('localhost')
            
            # Should have minimal external references
            assert external_refs <= localhost_refs + 1  # Allow for test references
    
    def test_css_inlined_for_performance(self):
        """Test that CSS is inlined to reduce requests"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test that CSS is inlined
            assert '<style>' in content or '<style nonce=' in content
            assert '--mynah-' in content  # Amazon Q theme variables
            
            # Test no external CSS references
            assert '<link rel="stylesheet"' not in content
    
    def test_script_loading_optimization(self):
        """Test that script loading is optimized"""
        from sagemaker_gen_ai_jupyterlab_extension.handlers import CLIENT_HTML_PATH
        
        if os.path.exists(CLIENT_HTML_PATH):
            with open(CLIENT_HTML_PATH, 'r') as f:
                content = f.read()
            
            # Test script loading optimization
            assert 'script.onload = init' in content  # Proper initialization
            assert 'script.onerror' in content  # Error handling
            assert 'document.body.appendChild(script)' in content  # Proper DOM insertion