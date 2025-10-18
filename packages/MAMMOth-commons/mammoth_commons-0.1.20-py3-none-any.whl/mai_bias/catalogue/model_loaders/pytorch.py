import os
from mammoth_commons.models.pytorch import Pytorch
from mammoth_commons.integration import loader
from mammoth_commons.externals import safeexec


@loader(
    namespace="mammotheu",
    version="v0049",
    python="3.13",
    packages=("numpy", "torch", "torchvision"),
)
def model_torch(
    state_path: str = "",
    model_path: str = "",
    model_name: str = "model",
    safe_libraries: str = "numpy, torch, torchvision, PIL, io, requests",
    multiclass_threshold: float = 0,
) -> Pytorch:
    """
    <img src="https://github.com/pytorch/pytorch/raw/main/docs/source/_static/img/pytorch-logo-dark.png"
    alt="Based on PyTorch" style="float: left; margin-right: 5px; margin-bottom: 5px; margin-top: 10px; height: 30px;"/>

    Loads a <a href="https://pytorch.org/">pytorch</a> model that comprises a Python code initializing the
    architecture and a file of trained parameters. For safety, the architecture's
    definition is allowed to directly import only specified libraries.

    Args:
        state_path: The path in which the architecture's state is stored.
        model_path: The path in which the architecture's initialization script resides. Alternatively, you may also just paste the initialization code in this field.
        model_name: The variable in the model path's script to which the architecture is assigned.
        safe_libraries: A comma-separated list of libraries that can be imported.
        multiclass_threshold: A decision threshold that treats outputs as separate classes. If this is set to zero (default), a softmax is applied to outputs. For binary classification, this is equivalent to setting the decision threshold at 0.5. Otherwise, each output is thresholded separately.
    """
    import torch

    multiclass_threshold = float(multiclass_threshold)
    model = safeexec(
        model_path,
        out=model_name,
        whitelist=[lib.strip() for lib in safe_libraries.split(",")],
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(state_path, map_location=device))
    return Pytorch(model, threshold=multiclass_threshold)
