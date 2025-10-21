# trigger_mlflow.py
import mlflow
import mlflow.pyfunc
import tempfile
from pathlib import Path
from typing import Dict, Any
from mlflow.tracking import MlflowClient
from core import TriggerModel


class MLflowWrapper(mlflow.pyfunc.PythonModel):
    """PyFunc wrapper for TriggerModel; backend can be set at runtime."""
    def load_context(self, context):
        archive_path = Path(context.artifacts["trigger_model"])
        self.model = TriggerModel.load(archive_path)
        self.backend = "software" 

    def predict(self, context, model_input):
        if self.backend == "software":
            return self.model.software_predict(model_input)
        elif self.backend == "qonnx":
            if self.model.model_qonnx is None:
                raise RuntimeError("QONNX model not available.")
            return self.model.qonnx_predict(model_input)
        elif self.backend == "firmware":
            if self.model.firmware_model is None:
                raise RuntimeError("Firmware model not available.")
            return self.model.firmware_predict(model_input)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def get_model_info(self):
        if hasattr(self.model, "get_model_info"):
            return self.model.get_model_info()
        return {"error": "Model info not available"}


def _get_pip_requirements(trigger_model: TriggerModel) -> list:
    requirements = ["numpy"]
    if trigger_model.ml_backend == "keras":
        requirements.extend(["tensorflow", "keras"])
    elif trigger_model.ml_backend == "xgboost":
        requirements.append("xgboost")
    if trigger_model.compiler == "hls4ml":
        requirements.append("hls4ml")
    elif trigger_model.compiler == "conifer":
        requirements.append("conifer")
    if hasattr(trigger_model, "model_qonnx") and trigger_model.model_qonnx is not None:
        requirements.append("qonnx")
    return requirements


def log_model(trigger_model: TriggerModel, registered_model_name: str, artifact_path: str = "TriggerModel"):
    """Log a TriggerModel as a PyFunc model and register it in the Model Registry."""
    if not registered_model_name:
        raise ValueError("registered_model_name must be provided and non-empty")

    if mlflow.active_run() is None:
        raise RuntimeError("No active MLflow run. Start a run before logging.")

    run = mlflow.active_run()
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / "triggermodel.tar.xz"
        trigger_model.save(archive_path)

        mlflow.pyfunc.log_model(
            artifact_path=artifact_path,
            python_model=MLflowWrapper(),
            artifacts={"trigger_model": str(archive_path)},
            pip_requirements=_get_pip_requirements(trigger_model)
        )

        # register model (always required)
        client = MlflowClient()
        model_uri = f"runs:/{run.info.run_id}/{artifact_path}"
        try:
            client.get_registered_model(registered_model_name)
        except mlflow.exceptions.RestException:
            client.create_registered_model(registered_model_name)
        client.create_model_version(
            name=registered_model_name,
            source=model_uri,
            run_id=run.info.run_id
        )

def load_model(model_uri: str) -> mlflow.pyfunc.PyFuncModel:
    return mlflow.pyfunc.load_model(model_uri)


def load_full_model(model_uri: str) -> TriggerModel:
    local_path = mlflow.artifacts.download_artifacts(model_uri)
    archive_path = Path(local_path) / "trigger_model" / "triggermodel.tar.xz"
    return TriggerModel.load(archive_path)


def get_model_info(model_uri: str) -> Dict[str, Any]:
    model = mlflow.pyfunc.load_model(model_uri)
    if hasattr(model._model_impl, "get_model_info"):
        return model._model_impl.get_model_info()
    return {"error": "Model info not available"}
