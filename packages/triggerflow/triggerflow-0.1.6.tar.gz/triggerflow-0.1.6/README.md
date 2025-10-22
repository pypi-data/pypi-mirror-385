# Machine Learning for Hardware Triggers

`triggerflow` provides a set of utilities for Machine Learning models targeting FPGA deployment. 
The `TriggerModel` class consolidates several Machine Learning frontends and compiler backends to construct a "trigger model". MLflow utilities are for logging, versioning, and loading of trigger models.

## Installation

```bash
pip install triggerflow
```

## Usage

```python

from triggerflow.core import TriggerModel 

trigger_model = TriggerModel(name="my-trigger-model", ml_backend="Keras", compiler="hls4ml", model, compiler_config or None)
trigger_model() # call the constructor

# then:
output_software = trigger_model.software_predict(input_data)
output_firmware = trigger_model.firmware_predict(input_data)
output_qonnx = trigger_model.qonnx_predict(input_data)

# save and load trigger models:
trigger_model.save("trigger_model.tar.xz")

# in a separate session:
from trigger_model.core import TriggerModel 
trigger_model = TriggerModel.load("trigger_model.tar.xz")
```

## Logging with MLflow

```python
# logging with MLFlow:
import mlflow
from trigger_model.mlflow_wrapper import log_model

mlflow.set_tracking_uri("https://ngt.cern.ch/models")
experiment_id = mlflow.create_experiment("example-experiment")

with mlflow.start_run(run_name="trial-v1", experiment_id=experiment_id):
    log_model(trigger_model, registered_model_name="TriggerModel")
```

### Note: This package doesn't install dependencies so it won't disrupt specific training environments or custom compilers. For a reference environment, see `environment.yml`.


