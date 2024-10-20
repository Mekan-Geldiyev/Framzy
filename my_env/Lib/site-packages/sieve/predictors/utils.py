from .predictors import SievePredictor, TemporalPredictor, ObjectPredictor, LinearPredictor
from typing import Any, Callable, Dict, List, Type
from cog.errors import ConfigDoesNotExist, PredictorNotSet
import yaml
import importlib.util
import inspect
import os.path
from pathlib import Path

#TODO: attribute validation?

def load_predictor(config: Dict[str, Any]) -> SievePredictor:
    """
    Constructs an instance of the user-defined SievePredictor class from a config.
    """

    if "predict" not in config:
        raise PredictorNotSet(
            "Can't run predictions: 'predict' option not found in cog.yaml"
        )

    predict_string = config["predict"]
    module_path, class_name = predict_string.split(":", 1)
    module_name = os.path.basename(module_path).split(".py", 1)[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    predictor_class = getattr(module, class_name)
    predictor = predictor_class()
    if "artifacts_directory" in config:
        artifacts_directory = config["artifacts_directory"]
        predictor.artifacts_directory = artifacts_directory
    return predictor

# TODO: make config a TypedDict
def load_config() -> Dict[str, Any]:
    """
    Reads cog.yaml and returns it as a dict.
    """
    # Assumes the working directory is /src

    config_path = os.path.abspath("cog.yaml")
    try:
        with open(config_path) as fh:
            config = yaml.safe_load(fh)
    except FileNotFoundError:
        try:
            config_path = os.path.abspath("sieve.yaml")
            with open(config_path) as fh:
                config = yaml.safe_load(fh)
        except FileNotFoundError:
            raise ConfigDoesNotExist(
                f"Could not find {config_path}",
            )
    return config

def run_prediction(
    predictor: SievePredictor, inputs: Dict[Any, Any], cleanup_functions: List[Callable]
) -> Any:
    """
    Run the predictor on the inputs, and append resulting paths
    to cleanup functions for removal.
    """
    result = predictor.predict(**inputs)
    if isinstance(result, Path):
        cleanup_functions.append(result.unlink)
    return result

def get_inputs(predictor: SievePredictor) -> Dict[str, Any]:
    """
    Validate and return predictor inputs from the arguments of a Predictor's predict() method.
    """

    signature = inspect.signature(predictor.predict)
    # Check if predictor is TemporalPredictor, ObjectPredictor, or LinearPredictor
    allowed_input_types = []
    if isinstance(predictor, TemporalPredictor):
        allowed_input_types = TemporalPredictor.ALLOWED_INPUT_TYPES
    elif isinstance(predictor, ObjectPredictor):
        allowed_input_types = ObjectPredictor.ALLOWED_INPUT_TYPES
    elif isinstance(predictor, LinearPredictor):
        allowed_input_types = LinearPredictor.ALLOWED_INPUT_TYPES
    else:
        raise Exception("Predictor type not supported, must be derived from TemporalPredictor, ObjectPredictor, or LinearPredictor")
    #Get all the input arg names and types
    input_args = {}
    for name, parameter in signature.parameters.items():
        input_args[name] = parameter.annotation
    return input_args

def get_output_type(predictor: SievePredictor):
    """
    Validate and return predictor output type from the return type of a Predictor's predict() method.
    """
    signature = inspect.signature(predictor.predict)
    if signature.return_annotation is inspect.Signature.empty:
        raise TypeError("You must set a valid return type")
    if isinstance(predictor, TemporalPredictor):
        allowed_output_types = TemporalPredictor.ALLOWED_OUTPUT_TYPES
    elif isinstance(predictor, ObjectPredictor):
        allowed_output_types = ObjectPredictor.ALLOWED_OUTPUT_TYPES
    elif isinstance(predictor, LinearPredictor):
        allowed_output_types = LinearPredictor.ALLOWED_OUTPUT_TYPES
    else:
        raise Exception("Predictor type not supported, must be derived from TemporalPredictor, ObjectPredictor, or LinearPredictor")
    #Get output arg type
    output_type = signature.return_annotation
    return output_type

def is_trainable(predictor: SievePredictor) -> bool:
    """
    Return whether the predictor is trainable by seeing if it has a train() method.
    """
    return hasattr(predictor, "train")

def human_readable_type_name(t: Type) -> str:
    """
    Generates a useful-for-humans label for a type. For builtin types, it's just the class name (eg "str" or "int"). For other types, it includes the module (eg "pathlib.Path" or "cog.File").

    The special case for Sieve modules is because the type lives in `sieve.types` internally, but just `sieve` when included as a dependency.
    """
    module = t.__module__
    if module == "builtins":
        return t.__qualname__
    elif module.split(".")[0] == "cog":
        module = "cog"

    try:
        return module + "." + t.__qualname__
    except AttributeError:
        return str(t)

def readable_types_list(type_list: List[Type]) -> str:
    return ", ".join(human_readable_type_name(t) for t in type_list)
