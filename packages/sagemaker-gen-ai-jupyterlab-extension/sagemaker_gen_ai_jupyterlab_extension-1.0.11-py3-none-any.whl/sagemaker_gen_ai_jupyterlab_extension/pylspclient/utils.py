import subprocess
import logging
import os

def get_shell_env_var(var_name):
    """Get environment variable sourced from shell profile"""
    try:
        result = subprocess.run(['bash', '-c', f'source ~/.bashrc && echo ${var_name}'], 
                              capture_output=True, text=True, timeout=5)
        value = result.stdout.strip()
        return value if value else None
    except:
        return None

def get_user():
    """Get the current user from LOGNAME environment variable sourced from .bashrc"""
    return get_shell_env_var('LOGNAME')

def get_domain_mode():
    """Get DOMAIN_MODE environment variable"""
    return get_shell_env_var('DOMAIN_MODE')

def get_sagemaker_app_type():
    """Get SAGEMAKER_APP_TYPE_LOWERCASE environment variable"""
    return os.getenv('SAGEMAKER_APP_TYPE_LOWERCASE')

def log_pylspclient_action(action, **kwargs):
    """Logging callback for pylsp client actions with consistent formatting"""
    user = get_user()
    
    # Skip logging kwargs for sensitive credential methods
    method = kwargs.get('method')
    if method in ['aws/credentials/iam/update', 'aws/credentials/token/update']:
        logging.info(f"{action}: method={method}, user: {user}")
    else:
        params_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        logging.info(f"{action}: {params_str}, user: {user}")