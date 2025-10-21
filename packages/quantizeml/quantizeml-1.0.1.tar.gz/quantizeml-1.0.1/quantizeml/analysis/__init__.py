try:
    from .kernel_distribution import *
    from .quantization_error_api import *
except ImportError as e:
    raise ImportError(
        "The 'analysis' submodule requires additional dependencies. "
        "Install it using: pip install quantizeml[analysis]"
    ) from e
