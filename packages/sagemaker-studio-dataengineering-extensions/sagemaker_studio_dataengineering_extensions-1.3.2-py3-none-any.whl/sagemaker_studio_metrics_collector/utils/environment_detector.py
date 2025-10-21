from enum import Enum
import os
import subprocess

class JupyterLabEnvironment(Enum):
    SAGEMAKER_STUDIO = "SageMakerStudio"
    SAGEMAKER_JUPYTERLAB = "SageMakerJupyterLab"
    SAGEMAKER_UNIFIED_STUDIO = "SageMakerUnifiedStudio"
    VANILLA_JUPYTERLAB = "VanillaJupyterLab"

class JupyterLabEnvironmentDetector:
    SAGEMAKER_JUPYTERLAB_APP_TYPE_ENVIRON = "JupyterLab"
    SAGEMAKER_STUDIO_UI_EXTENSION_NAME = "@amzn/sagemaker-ui"

    def __init__(self):
        self.current_environment = self._detect_environment()

    def _get_installed_extensions(self):
        try:
            result = subprocess.run(
                ["jupyter", "labextension", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            return result.stderr if result.returncode == 0 else ""
        except subprocess.CalledProcessError:
            return ""

    def _detect_environment(self):
        if (os.environ.get("SAGEMAKER_APP_TYPE") ==
            self.SAGEMAKER_JUPYTERLAB_APP_TYPE_ENVIRON):
            return JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB
        if self.SAGEMAKER_STUDIO_UI_EXTENSION_NAME in self._get_installed_extensions():
            return JupyterLabEnvironment.SAGEMAKER_STUDIO
        return JupyterLabEnvironment.VANILLA_JUPYTERLAB


