#!/usr/bin/env python3
"""
Local test script for DirectFileHandler
"""
import os
import tempfile
import requests
from tornado.web import Application
from tornado.ioloop import IOLoop
from sagemaker_gen_ai_jupyterlab_extension.handlers import DirectFileHandler

def create_test_js_file():
    """Create a test JS file"""
    test_dir = tempfile.mkdtemp()
    js_file = os.path.join(test_dir, "amazonq-ui.js")
    
    with open(js_file, 'w') as f:
        f.write("""
// Test Amazon Q UI JavaScript
console.log('Amazon Q UI loaded successfully');
window.amazonQChat = {
    createChat: function(api, options) {
        console.log('Amazon Q Chat created', options);
    }
};
""")
    
    return test_dir, js_file

def test_handler():
    """Test the DirectFileHandler locally"""
    # Create test file
    test_dir, js_file = create_test_js_file()
    print(f"Created test file: {js_file}")
    
    # Create Tornado app with DirectFileHandler
    app = Application([
        (r"/direct/(.*)", DirectFileHandler, {"path": test_dir}),
    ])
    
    # Start server on port 8888
    app.listen(8888)
    print("Test server started on http://localhost:8888")
    print("Test URL: http://localhost:8888/direct/amazonq-ui.js")
    
    # Test the handler
    try:
        response = requests.get("http://localhost:8888/direct/amazonq-ui.js")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content length: {len(response.text)}")
        print(f"Content preview: {response.text[:100]}...")
        
        if response.headers.get('Content-Type') == 'text/javascript; charset=utf-8':
            print("✅ MIME type is correct!")
        else:
            print("❌ MIME type is incorrect!")
            
    except Exception as e:
        print(f"Error testing: {e}")
    
    # Keep server running
    print("\nPress Ctrl+C to stop the server")
    try:
        IOLoop.current().start()
    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        # Cleanup
        os.unlink(js_file)
        os.rmdir(test_dir)

if __name__ == "__main__":
    test_handler()