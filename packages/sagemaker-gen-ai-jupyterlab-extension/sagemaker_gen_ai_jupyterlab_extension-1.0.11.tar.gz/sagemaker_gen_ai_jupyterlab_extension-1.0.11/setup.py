"""
SageMakerGenAIJupyterLabExtension packaging setup.

For more details on how to operate this file, check
https://w.amazon.com/index.php/Python/Brazil
"""

from setuptools import find_packages, setup

setup(
    name="sagemaker_gen_ai_jupyterlab_extension",
    version="1.0.0",
    author="Amazon Web Services",
    description="An extension supporting SageMaker's GenAI capabilities in JupyterLab",
    packages=find_packages(),
    package_data={
        "sagemaker_gen_ai_jupyterlab_extension": ["static/*", "labextension/**/*"],
    },
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "jupyter-docprovider>=1,<3",
        "jupyter-server-ydoc>=1,<3",
        "requests>=2.25.0",
        "watchdog>=2.1.0",
        "aws_embedded_metrics",
        "sagemaker-jupyterlab-extension-common",
        "pydantic>=2.11.0"
    ],
)