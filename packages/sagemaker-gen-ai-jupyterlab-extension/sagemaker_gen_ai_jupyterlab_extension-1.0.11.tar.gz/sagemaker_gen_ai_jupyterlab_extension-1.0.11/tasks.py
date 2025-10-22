 import os
 import platform
 import tempfile
 import shutil
  
 from invoke import task
  
 """
 The methods in this file are invoked by the peru-build process and implement the logic for 
 what happens when each of the build methods are called by invoking the idiomatic tool
 """
  
  
 PIPX_HOME = os.path.join(os.getcwd(), ".pipx", "local")
 PIPX_ENV = os.path.join(PIPX_HOME, "venvs", "pipx")
  
  
 @task
 def pipx(context):
     if not os.path.exists(PIPX_HOME):
         os.makedirs(PIPX_HOME)
         context.run(f"python -m venv {PIPX_ENV}")
         context.run(f"{PIPX_ENV}/bin/pip install pipx")
  
  
  
 @task(pipx)
 def format(context):
     """
     Runs black and isort against the code
     """
     context.run(f"PIPX_HOME={PIPX_HOME} {PIPX_ENV}/bin/pipx install black")
     context.run(f"PIPX_HOME={PIPX_HOME} {PIPX_ENV}/bin/pipx install isort")
     context.run(f"{PIPX_HOME}/venvs/black/bin/black src -l 100")
     context.run(f"{PIPX_HOME}/venvs/isort/bin/isort src --profile black")
  
  
 @task(pipx)
 def check(context):
     """
     Checks formatting and type-safety of code using black, isort, flake8 and mypy
     """
     context.run("echo 'Running source code checks...'")
     context.run(f"PIPX_HOME={PIPX_HOME} {PIPX_ENV}/bin/pipx install mypy")
     context.run(f"PIPX_HOME={PIPX_HOME} {PIPX_ENV}/bin/pipx install flake8")
     context.run(f"PIPX_HOME={PIPX_HOME} {PIPX_ENV}/bin/pipx install black")
     context.run(f"PIPX_HOME={PIPX_HOME} {PIPX_ENV}/bin/pipx install isort")
     context.run(f"{PIPX_HOME}/venvs/mypy/bin/mypy src/sagemaker_gen_ai_jupyterlab_extension")
     context.run(f"{PIPX_HOME}/venvs/flake8/bin/flake8 src --ignore=E501,W503,E203 --max-line-length=100")
     context.run(f"{PIPX_HOME}/venvs/black/bin/black src --check -l 100")
     context.run(f"{PIPX_HOME}/venvs/isort/bin/isort src --check --profile black")
  
 @task
 def test(context):
     """
     Runs pytest with coverage
     """
     context.run("pip install pytest pytest-cov")
     context.run("pytest")
  
 @task
 def copy_bats_publisher_configuration(context):
     """Copy the BATS publisher configuration to output directory.
  
     This function assumes that the configuration is located under configuration/Packaging
     of the package source.
     """
     context.run(f"cp -a configuration/Packaging build")
  
  
 @task(pre=[check, test])
 def prerelease(context):
     """
     Runs check and test
     """
     pass