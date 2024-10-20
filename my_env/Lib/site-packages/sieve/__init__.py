from .types.base import Struct
from .types.file import File, Image, Video, Audio, Array
from .types.metadata import Metadata
from .functions.function import function, Model, Env, gpu
from .api.common import upload, get, logs, whoami, write_key
from .api import secrets
from .server.handling.cost_handling import bill, view_bill
from .server.grpc.runner import FatalException


def workflow(*_args, **_kwargs):
    import warnings

    warnings.warn(
        "Workflow decorator is deprecated and the workflow will not be deployed, please use @sieve.function instead.",
        UserWarning,
        stacklevel=2,
    )

    def __do_nothing(*_args, **_kwargs):
        pass

    return __do_nothing
