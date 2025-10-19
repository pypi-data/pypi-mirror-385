# ruff: noqa: E402, F401, F821, SLF001
# isort:skip_file,
# ignore unused imports
# ignore use of _Simulation
# ignore use of functions starting with _

# Import the extension modules
import builtins
import contextlib

# Standard library imports
import hashlib
import importlib
import importlib.metadata
import logging
import pkgutil
import sys
import warnings
from pathlib import Path
from sysconfig import get_config_var

# Define __version__ attribute
try:
    __version__ = importlib.metadata.version("sund")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

logger = logging.getLogger(__name__)

# isort: off
from . import tools
from ._StringList import StringList  # import prior to _Activity
from ._Activity import Activity
from . import _Models
from ._Simulation import Simulation, TimeScales
from . import _debug
# isort: on

# Import model validation
from .model_validation import (
    ModelValidationError,
    print_validation_results,
    validate_model,
)

# Import utility functions
from .utils import test_distribution

##################################################################################################
# Handle debug mode
##################################################################################################


def debug(*, mode: bool) -> None:
    """Enables or disables debug mode for the SUND toolbox C++ components.

    Args:
        mode (bool): If True, enables debug mode. If False, disables debug mode.
    """
    if mode:
        _debug.enable_debug()
        _Simulation.enable_debug()
    else:
        _debug.disable_debug()
        _Simulation.disable_debug()


def is_debug() -> bool:
    """Checks if the SUND toolbox is in debug mode."""
    logger.info("_debug debug mode: %s", _debug.is_debug())
    logger.info("_Simulation debug mode: %s", _Simulation.is_debug())
    return _debug.is_debug()


##################################################################################################
# List all installed models
##################################################################################################


def import_model(model: str) -> object:
    """Imports the compiled class of an installed model.

    Args:
        model (str): Name of the model to import.

    Raises:
        ValueError: Cannot find an installed model with name: 'model'

    Returns:
        sund.Model class of the model.
    """
    try:
        module = importlib.import_module("sund.Models." + model)
        return getattr(module, model)
    except ModuleNotFoundError:
        msg = f"Cannot find an installed model with name: '{model}'"
        raise ValueError(msg) from None


def _is_model_content_string(model: str) -> bool:
    """Checks if the model is a text model.

    Args:
        model (string): Model name to be checked.

    Returns:
        bool: True if the model is a text model, False otherwise.
    """

    return bool(
        isinstance(model, str)
        and (
            "########## NAME" in model
            and "########## METADATA" in model
            and "########## MACROS" in model
            and "########## STATES" in model
            and "########## PARAMETERS" in model
            and "########## VARIABLES" in model
            and "########## FUNCTIONS" in model
            and "########## EVENTS" in model
            and "########## OUTPUTS" in model
            and "########## INPUTS" in model
            and "########## FEATURES" in model
        ),
    )


def _write_model_hash(hashfile: Path, content_hash: str):
    tmp = hashfile.with_suffix(hashfile.suffix + ".tmp")
    tmp.write_text("v1:" + content_hash)
    tmp.replace(hashfile)


def _read_model_hash(hashfile: Path):
    try:
        raw = hashfile.read_text().strip()
        if raw.startswith("v1:"):
            return raw.split(":", 1)[1]
        return raw
    except Exception:  # noqa: BLE001
        return None


def install_model(  # noqa: C901, PLR0912, PLR0915
    model: str | list[str],
    *,
    force: bool = False,
    save_compiled_model: bool = False,
):
    """Installs one or more models, making it available for import.

    Args:
        model (string | list[string]): Model content string or path to model file (str).
            Can also be a list of such strings. File names can be a regular expression to
            install multiple models at the same time.
        force (bool, optional): If True, will force reinstallation even if model is already
            installed. Defaults to False.
        save_compiled_model (bool, optional): If True, will not delete the generated c++-file.
            Defaults to False.

    Raises:
        ValueError: `Could not find file`, if the file is missing.
        ValueError: `Model *name* is already installed and up to date`, if an identical model
            is already installed.
        ValueError: `Model *name* has already been imported to memory, you will need to restart
            Python before re-installing the model`, if the model has already been imported.
        ValueError: `Error while installing`, an unknown error occurred while installing the model.
    """

    if type(model) is list:
        for m in model:
            install_model(m, force=force, save_compiled_model=save_compiled_model)
    else:
        # Check if input is a model string, or a model file
        if _is_model_content_string(model):
            models = [model]
        else:
            models = list(Path().glob(model))
            if len(models) == 0:
                msg = f'Could not find file "{model}"'
                raise ValueError(msg)
            models = [str(m.resolve()) for m in models]

        models_folder = Path(__file__).parent / "Models"

        for m in models:
            if _is_model_content_string(m):
                model_content = m
                path = Path.cwd()
            else:
                try:
                    model_path = Path(m)
                    model_content = model_path.read_text(encoding="utf-8")
                except Exception as e:
                    msg = f"Could not read model file '{m}'."
                    raise ValueError(msg) from e
                path = model_path.parent.resolve()

            model = tools._model_structure(model_content, file_path=str(path))

            logger.info("Installing model '%s'...", model["NAME"])

            # Determine module and hash file paths
            modulefile = models_folder / (model["NAME"] + get_config_var("EXT_SUFFIX"))
            hashfile = models_folder / (model["NAME"] + ".hash")

            # Calculate hash of the (new) model content
            current_hash = hashlib.sha256(model_content.encode("utf-8")).hexdigest()

            # Check if already installed and up to date
            if not force and model["NAME"] in installed_models() and modulefile.exists():
                existing_hash = _read_model_hash(hashfile) if hashfile.exists() else None

                if existing_hash == current_hash:
                    logger.info("Model '%s' is already installed and up to date.", model["NAME"])
                    continue

                if existing_hash is None:
                    logger.info(
                        "Model '%s' is missing content hash. Reinstalling model and creating hash sidecar.",  # noqa: E501
                        model["NAME"],
                    )
                else:
                    logger.info(
                        "Model '%s' content differs from installed version. Reinstalling.",
                        model["NAME"],
                    )

            # Check if imported
            if ("sund.Models." + model["NAME"]) in sys.modules:
                logger.warning(
                    "Model '%s' has already been imported into memory. Trying to unload the module, but you might need to restart Python before re-installing the model.",  # noqa: E501
                    model["NAME"],
                )

                sys.modules.pop("sund.Models." + model["NAME"])
            # Check if modulefile exist on file system and remove
            if modulefile.exists():
                try:
                    modulefile.unlink()
                except (OSError, PermissionError) as err:
                    msg = f"Model '{model['NAME']}' cannot be re-installed, probably because it is being used by another process. Try terminating any process that might use the model and try again."  # noqa: E501
                    raise ValueError(msg) from err
            if hashfile.exists():
                with contextlib.suppress(builtins.BaseException):
                    hashfile.unlink()

            # create C-file and module file
            logger.info("Compiling model '%s'...", model["NAME"])
            cfile = tools._model_cfile(model)
            tools._model_module_file(cfile)
            if not save_compiled_model:
                Path(cfile).unlink()
            logger.info("Model '%s' successfully installed.", model["NAME"])

            try:
                _write_model_hash(hashfile, current_hash)
            except Exception as e:  # noqa: BLE001
                warnings.warn(
                    f"Could not write hash file for model '{model['NAME']}': {e}",
                    stacklevel=2,
                )


def installed_models() -> list[str]:
    """Produces a list of the names of the installed models.

    Returns:
        A list of installed models
    """
    pkgpath = Path(__file__).parent / "Models"
    return [name for _, name, _ in pkgutil.iter_modules([str(pkgpath)])]


def load_model(model: str) -> object:
    """Imports the class of a model and returns an instance of that class.

    Equivalent to running:

    ```
    ModelClass = sund.import_model("model")
    model = ModelClass()
    ```

    Args:
        model (str): The name of the model

    Returns:
        sund.Model object: A model object of the loaded model
    """
    ModelClass = import_model(model)  # noqa: N806
    return ModelClass()


def uninstall_model(model=None, *, all: bool = False):  # noqa: C901, PLR0912, A002
    """Uninstall one or several models.

    Args:
        model (string, optional): Model name of the model to be uninstalled. Defaults to None.
        all (bool, optional): Option to uninstall *all* installed models. Should be called before
            uninstalling the sund package to make sure no files are left on the file system.
            Defaults to False.

    Raises:
        ValueError: `Model *name* has already been imported to memory, you will need to restart
            Python before uninstalling the model`, if the model has already been imported.
        ValueError: `Model file for model *name* not found`, the model files are missing and can
            thus not be uninstalled.
        ValueError: `Model *name* could not be uninstalled, probably because it is being used by
            another process. Try terminating any process that might use the model and try again,
            if the model cannot be uninstalled because it is being used.
    """

    if not all and model is None:
        msg = "'model' must be set if 'all' is False!"
        raise SyntaxError(msg)

    models_folder = Path(__file__).parent / "Models"
    if all:
        model_names = installed_models()
        for m in model_names:
            uninstall_model(model=m)

        # After uninstalling all known models, remove any leftover hash sidecar files (.hash)
        for orphan_hash in models_folder.glob("*.hash"):
            try:
                orphan_hash.unlink()
            except Exception:  # noqa: BLE001
                warnings.warn(
                    f"Could not remove orphan hash file '{orphan_hash.name}'.",
                    stacklevel=2,
                )
        logger.info("All models have been uninstalled.")
    elif isinstance(model, list):
        for m in model:
            uninstall_model(model=m)
    else:
        if ("sund.Models." + model) in sys.modules:
            msg = f"Model '{model}' has been imported into memory, you will need to restart Python before uninstalling the model."  # noqa: E501
            raise ValueError(msg)
        file = models_folder / (model + get_config_var("EXT_SUFFIX"))
        hashfile = models_folder / (model + ".hash")
        if not file.exists():
            warnings.warn(
                f"Model file for model '{model}' not found. Had the model been installed before?",
                stacklevel=2,
            )
        else:
            try:
                file.unlink()
                if hashfile.exists():
                    try:
                        hashfile.unlink()
                    except (OSError, PermissionError, FileNotFoundError):
                        warnings.warn(
                            f"Could not remove hash file for model '{model}'.",
                            stacklevel=2,
                        )
                logger.info("Model '%s' has been uninstalled.", model)
            except (OSError, PermissionError, FileNotFoundError) as e:
                msg = f"Model '{model}' could not be uninstalled, probably because it is being used by another process. Try terminating any process that might use the model and try again."  # noqa: E501
                raise ValueError(
                    msg,
                ) from e


def version() -> str:
    """Returns the version of the SUND toolbox.
    Returns:
        The version of the SUND toolbox.
    """

    return importlib.metadata.version("sund")


def save_model_template(
    file_name: str,
    *,
    model_name: str = "template",
    time_unit: str = "s",
    description: str | None = None,
    authors: str | None = None,
) -> None:
    """Saves a model template to a file.

    Args:
        file_name (string): Name of the file (can include path) to save the template to.
        model_name (string, optional): Name of the model.
        time_unit (string, optional): Time unit for the model. Defaults to 's'.
        description (string, optional): Description of the model.
        authors (string, optional): Author of the model.
    """

    model_content = f'''
########## NAME
{model_name}
########## METADATA
time_unit = {time_unit}
Description = """{description}"""
Authors =  """{authors}"""
########## MACROS
########## STATES
ddt_A = 1
A(0) = 0
########## PARAMETERS
########## VARIABLES
########## FUNCTIONS
########## EVENTS
########## OUTPUTS
########## INPUTS
########## FEATURES
A = A
'''
    Path(file_name).write_text(model_content, encoding="utf-8")


def validate_model_file(
    model_path_or_content: str | Path,
    *,
    raise_on_error: bool = False,
    raise_on_warning: bool = False,
    verbose: bool = True,
):
    """
    Validate a model file or content string for common errors and issues.

    This function checks for common model issues including:
    - Degradation reactions that don't depend on themselves (e.g., A -> B: v = k1 instead of v = k1*A)
    - Variables/reactions not being used
    - Inputs not being used
    - Parameters not being used
    - Features depending on undefined variables/states/parameters
    - Negative signs in variables/reactions (discouraged)
    - Circular dependencies
    - Naming conflicts

    Args:
        model_path_or_content (str | Path): File path (string or Path object) to model file, or model content string
        raise_on_error (bool): Whether to raise exceptions for validation errors. Defaults to False.
        raise_on_warning (bool): Whether to raise exceptions for validation warnings. Defaults to False.
        verbose (bool): Whether to print detailed validation results. Defaults to True.

    Returns:
        dict: Dictionary containing 'errors' and 'warnings' lists

    Raises:
        ModelValidationError: If validation fails and raise_on_error is True

    Example:
        results = sund.validate_model_file('my_model.txt')
    """  # noqa: E501
    results = validate_model(
        model_path_or_content,
        raise_on_error=raise_on_error,
        raise_on_warning=raise_on_warning,
    )

    if verbose:
        # Extract model name for display
        model_name = "model"
        model_content = str(model_path_or_content)

        # Check if it's model content (contains model markers)
        is_model_content = "########## NAME" in model_content

        if not is_model_content:
            # It's a file path
            try:
                path = Path(model_path_or_content)
                model_name = path.stem if path.exists() else str(model_path_or_content)
            except (OSError, TypeError):
                model_name = str(model_path_or_content)
        else:
            # It's model content - try to extract name
            try:
                lines = model_content.split("\n")
                for i, line in enumerate(lines):
                    if line.strip() == "########## NAME" and i + 1 < len(lines):
                        model_name = lines[i + 1].strip()
                        break
            except AttributeError:
                pass

        print_validation_results(results, model_name)

    return results
