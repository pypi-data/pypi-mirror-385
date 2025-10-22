#!/usr/bin/env python3
"""
Test runner for Amazon Q self-contained architecture production changes.
Runs tests for enhanced error handling, artifact validation, and DirectFileHandler improvements.
"""
import sys
import subprocess
import os


def run_tests():
    """Run production-related unit tests"""
    
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("🧪 Running Amazon Q Production Changes Unit Tests")
    print("=" * 50)
    
    # Test files to run
    test_files = [
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_amazon_q_production_changes.py",
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_amazon_q_client_html.py",
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_init.py::TestAmazonQInitModule::test_load_jupyter_server_extension_with_enhanced_error_handling",
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_init.py::TestAmazonQInitModule::test_load_jupyter_server_extension_graceful_degradation",
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_init.py::TestAmazonQInitModule::test_initialize_amazon_q_lsp_server_missing_artifacts_enhanced_logging",
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_init.py::TestAmazonQInitModule::test_initialize_amazon_q_lsp_server_with_enhanced_logging",
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_handlers.py::TestAmazonQDirectFileHandler",
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_handlers.py::TestAmazonQSetupHandlers::test_setup_handlers_success_with_artifact_validation",
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_handlers.py::TestAmazonQSetupHandlers::test_setup_handlers_exception_with_enhanced_logging",
        "sagemaker_gen_ai_jupyterlab_extension/tests/test_handlers.py::TestAmazonQSetupHandlers::test_artifact_validation_logging",
    ]
    
    success_count = 0
    failure_count = 0
    
    for test_file in test_files:
        print(f"\n📋 Running: {test_file}")
        print("-" * 40)
        
        try:
            # Run pytest with verbose output
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--no-header"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ PASSED")
                success_count += 1
                if result.stdout:
                    # Show only the test results, not the full output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if '::' in line and ('PASSED' in line or 'FAILED' in line):
                            print(f"   {line}")
            else:
                print("❌ FAILED")
                failure_count += 1
                if result.stdout:
                    print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                if result.stderr:
                    print("STDERR:", result.stderr[-500:])  # Last 500 chars
                    
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT")
            failure_count += 1
        except Exception as e:
            print(f"💥 ERROR: {e}")
            failure_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {success_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"📈 Total:  {success_count + failure_count}")
    
    if failure_count == 0:
        print("\n🎉 All production tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failure_count} test(s) failed. Please review the output above.")
        return 1


def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest is not installed. Please run: pip install pytest")
        return False
    
    return True


if __name__ == "__main__":
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    exit_code = run_tests()
    sys.exit(exit_code)