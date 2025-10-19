import importlib
import os
import re
import sys
import tempfile
import warnings
from contextlib import nullcontext, redirect_stderr, redirect_stdout
from pathlib import Path

import setuptools._distutils.ccompiler
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

from . import _debug

_sund_folder = Path(__file__).parent


class SundCompilerError(Exception):
    """Raised when the compiler is not compatible with the Sund Toolbox."""


class CustomBuildExt(build_ext):
    def build_extension(self, ext):
        compiler = setuptools._distutils.ccompiler.new_compiler()  # noqa: SLF001
        compiler_type = compiler.compiler_type

        if compiler_type == "msvc":
            ext.extra_compile_args = ["/std:c++20", "/utf-8"]
        elif compiler_type == "unix":
            ext.extra_compile_args = ["-std=c++20"]
        else:
            msg = "Compiler not compatible with Sund Toolbox."
            raise SundCompilerError(msg)

        super().build_extension(ext)


##################################################################################################
# Compile new model
##################################################################################################
def _model_structure(model_content, file_path="."):
    # Read in file and compile
    ##############################################################################################

    section_names = [
        "NAME",
        "METADATA",
        "MACROS",
        "STATES",
        "PARAMETERS",
        "VARIABLES",
        "FUNCTIONS",
        "EVENTS",
        "OUTPUTS",
        "INPUTS",
        "FEATURES",
    ]

    section_txt = _txt_parts(model_content, section_names)
    model_structure = dict.fromkeys(section_names, None)
    model_structure["FILEPATH"] = file_path
    model_structure["NAME"] = _remove_white_space(section_txt["NAME"])
    if not re.match(r"^[A-Za-z]\w*$", model_structure["NAME"]):
        msg = (
            f"Invalid model name: '{model_structure['NAME']}'. "
            "Must start with a letter and contain only letters, digits or underscores."
        )
        raise ValueError(
            msg,
        )

    model_structure["METADATA"] = _compile_metadata(section_txt["METADATA"])
    model_structure["MACROS"] = _compile_macros(section_txt["MACROS"])
    states, algequations = _compile_state_equations(section_txt["STATES"])
    model_structure["STATES"] = states
    model_structure["ALGEQUATIONS"] = algequations
    model_structure["PARAMETERS"] = _compile_parameters(section_txt["PARAMETERS"])
    model_structure["FUNCTIONS"] = _compile_functions(section_txt["FUNCTIONS"])
    model_structure["EVENTS"] = _compile_events(model_structure, section_txt["EVENTS"])
    model_structure["OUTPUTS"] = _compile_outputs(section_txt["OUTPUTS"])
    model_structure["INPUTS"] = _compile_inputs(section_txt["INPUTS"])
    model_structure["VARIABLES"] = _compile_variables(model_structure, section_txt["VARIABLES"])
    model_structure["FEATURES"] = _compile_features(section_txt["FEATURES"])

    return model_structure


def _model_cfile(model):
    # Create .c file
    ######################################################################################
    cfile = Path(model["FILEPATH"]) / (model["NAME"] + ".cpp")
    with cfile.open("w", encoding="utf-8") as c_file_handle:
        _print_model_to_file(c_file_handle, model)
    return str(cfile)


def _model_module_file(cfile):
    # Extract module name from file path
    cfile_path = Path(cfile)
    model_name = cfile_path.stem
    build_dir = _sund_folder.parent
    model_deps_dir = _sund_folder / "_model_deps"

    # Define extension
    model_ext = Extension(
        name="sund.Models." + model_name,
        sources=[cfile_path, model_deps_dir / "_src" / "mathaddon.cpp"],
        include_dirs=[model_deps_dir / "_include"],
    )

    # Setup temporary build directory
    with tempfile.TemporaryDirectory() as temp_dir:
        build_temp_target = Path(temp_dir) / "temp"

        # Check writability of the general temp directory
        try:
            with tempfile.NamedTemporaryFile(delete=True):
                pass
            build_temp_args = ["--build-temp", str(build_temp_target)]
        except OSError as e:
            warnings.warn(
                f"Cannot write to the temporary directory: {tempfile.gettempdir()}. Please check permissions or disk space. Using default 'build' directory. Original error: {e}",  # noqa: E501
                stacklevel=2,
            )
            build_temp_args = []

        if _debug:
            # Debug mode: show compilation output
            context = nullcontext()
        else:
            # Normal mode: hide compilation output using /dev/null
            devnull = Path.open(os.devnull, "w")
            context = redirect_stdout(devnull), redirect_stderr(devnull)

        with context:
            setup(
                name="sund.Models." + model_name,
                ext_modules=[model_ext],
                cmdclass={"build_ext": CustomBuildExt},
                script_args=["build_ext", "-b", str(build_dir), *build_temp_args],
                packages=[],
            )

        if not _debug:
            devnull.close()

    # Force reload the module if it exists
    if f"sund.Models.{model_name}" in sys.modules:
        importlib.reload(sys.modules[f"sund.Models.{model_name}"])


# Write model to .cpp file
##############################################################################################
def _write_initial_conditions(file, model):  # noqa: C901, PLR0912
    file.write("/* Function for initial condition definition */\n")
    file.write(
        f"static void {model['NAME']}_initialcondition(double *icvector, double *dericvector, double *parametervector, const std::vector<double>& inputs){{\n",  # noqa: E501
    )
    file.write("\t[[maybe_unused]] double time{0.0};\n")

    # Define parameters
    for i, name in enumerate(model["PARAMETERS"]):
        file.write(f"\t[[maybe_unused]] double {name}{{parametervector[{i}]}};\n")

    file.write("\n")

    # Define inputs
    for i, input_name in enumerate(model.get("INPUTS")):
        file.write(f"\t[[maybe_unused]] const double {input_name}{{inputs[{i}]}};\n")

    file.write("\n")

    # Define non-state-dependent variables
    for name, variable in model["VARIABLES"].items():
        if not variable["state_dependency"]:
            file.write(f"\t[[maybe_unused]] double {name}{{{variable['expression']}}};\n")

    file.write("\n")

    # States
    for _i, (name, itemdict) in enumerate(model["STATES"].items()):
        split_state_expression = re.split(r"\+|\*|/|-|\(|\)|,", itemdict.get("ic"))

        # Check if inital condition definition contains reference to mandatory input
        for reference in split_state_expression:
            for _j, inp in enumerate(model["INPUTS"]):
                if reference == inp and model["INPUTS"].get(reference).get("defaultvalue") is None:
                    # Raise exception if input has no default value (mandatory input)
                    msg = (
                        f"Error in definition of initial condition for state '{name}': Mandatory input '{reference}' is not allowed in state initial condition definition!",  # noqa: E501
                    )
                    raise ValueError(msg)
            if reference in model.get("VARIABLES"):
                if model.get("VARIABLES").get(reference).get("state_dependency"):
                    msg = (
                        f"Error in definition of initial condition for state '{name}': State dependent variable '{reference}' is not allowed in state initial condition definition!",  # noqa: E501
                    )
                    raise ValueError(msg)
                if model.get("VARIABLES").get(reference).get("mandatory_input_dependencies"):
                    msg = (
                        f"Error in definition of initial condition for state '{name}': Variable '{reference}' dependent on mandatory inputs is not allowed in state initial condition definition!",  # noqa: E501
                    )
                    raise ValueError(msg)

        file.write(f"\t[[maybe_unused]] const double {name}{{{itemdict['ic']}}};\n")

    file.write("\n")

    # Define remaining state-dependent variables
    for name, variable in model["VARIABLES"].items():
        if variable["state_dependency"]:
            file.write(f"\t[[maybe_unused]] double {name}{{{variable['expression']}}};\n")

    file.write("\n")

    for i, name in enumerate(model.get("STATES").keys()):
        file.write(f"\ticvector[{i}] = {name};\n")

    file.write("\n")

    # Derivatives
    for i, _ in enumerate(model["STATES"].items()):
        file.write(f"\tdericvector[{i}] = 0;\n")

    file.write("}\n\n")


def _strip_quotes(text):
    """Strip surrounding quotes from text.

    Handles triple quotes (\""" or ''') and single quotes (" or ').

    Args:
        text: String that might have surrounding quotes

    Returns:
        String with surrounding quotes removed
    """
    if not text:
        return text

    # Remove triple quotes if present
    if (text.startswith('"""') and text.endswith('"""')) or (
        text.startswith("'''") and text.endswith("'''")
    ):
        return text[3:-3]
    # Remove single quotes if present
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        return text[1:-1]

    return text


def _build_model_docstring(model):
    """Build a properly formatted and escaped docstring from model metadata."""
    # Get description
    if "description" in model["METADATA"]:
        description = _strip_quotes(model["METADATA"]["description"]).strip()
        description = description.replace("\\n", "\n")
        docstring = description
    else:
        docstring = f"{model['NAME']} model"

    # Add authors
    if "authors" in model["METADATA"]:
        authors_text = _strip_quotes(model["METADATA"]["authors"]).rstrip()
        authors_text = authors_text.replace("\\n", "\n")
        docstring += "\n\nAuthor(s): " + authors_text + "\n"
    else:
        docstring += "\n\nAuthor(s): unknown\n"

    # Escape the docstring for C string
    return docstring.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _print_model_to_file(file, model):  # noqa: C901, PLR0912, PLR0915
    file.write('#include "mathaddon.h"\n')
    file.write("#include <Models_M_API.h>\n")
    file.write('#include "sund_sundials_flags.h"\n\n')

    file.write("#include <Python.h>\n\n")
    file.write("#include <cmath>\n")
    file.write("#include <vector>\n\n")

    file.write("using namespace std;\n\n")

    for macro, itemdict in model["MACROS"].items():
        file.write(f"#define {macro} {itemdict['expression']}\n")

    file.write("\nstatic ModelFunction {}_modelfunction;\n".format(model["NAME"]))
    file.write("static ICFunction {}_initialcondition;\n".format(model["NAME"]))
    file.write(
        "static PyObject *{}_new(PyTypeObject *type, PyObject *args, PyObject *kwds);\n\n".format(
            model["NAME"],
        ),
    )

    # declare names
    file.write("// states, features, outputs, inputs, events, parameters\n")
    _list_declaration(
        file,
        model["NAME"] + "_numberof",
        [
            len(model["STATES"]),
            len(model["FEATURES"]),
            len(model["OUTPUTS"]),
            len(model["INPUTS"]),
            len(model["EVENTS"]),
            len(model["PARAMETERS"]),
        ],
        kind=1,
    )
    _list_declaration(file, model["NAME"] + "_statenames", list(model["STATES"].keys()), kind=0)
    _list_declaration(file, model["NAME"] + "_featurenames", list(model["FEATURES"].keys()), kind=0)
    _list_declaration(
        file,
        model["NAME"] + "_featureunits",
        [itemdict["unit"] for _, itemdict in model["FEATURES"].items()],
        kind=0,
    )
    _list_declaration(file, model["NAME"] + "_outputnames", list(model["OUTPUTS"].keys()), kind=0)
    _list_declaration(
        file,
        model["NAME"] + "_inputnames",
        [itemdict["externvariable"] for _, itemdict in model["INPUTS"].items()],
        kind=0,
    )
    _list_declaration(
        file,
        model["NAME"] + "_parameternames",
        list(model["PARAMETERS"].keys()),
        kind=0,
    )
    _list_declaration(file, model["NAME"] + "_eventnames", list(model["EVENTS"].keys()), kind=0)

    # decalare mandatory inputs, i.e. inputs without default value
    file.write("\n// {0 = mandatory, 1 = non-mandatory, 2 = non-mandatory - zero default value}\n")
    mandatoryinputs = [0] * len(
        model["INPUTS"],
    )  # 0 mandatory, 1 non-mandatory, 2 non-mandatory - default value 0
    for i, itemdict in enumerate(model["INPUTS"].values()):
        if itemdict["defaultvalue"]:
            if float(itemdict["defaultvalue"]) == 0.0:
                mandatoryinputs[i] = 2
            else:
                mandatoryinputs[i] = 1
    _list_declaration(file, model["NAME"] + "_mandatoryinputs", mandatoryinputs, kind=1)

    # default values for input
    file.write(f"\nconst std::vector<double> {model['NAME']}_defaultInputs{{")
    for i, inp in enumerate(model["INPUTS"].keys()):
        default_input_value = model["INPUTS"].get(inp).get("defaultvalue")
        if default_input_value is None:
            default_input_value = 0.0
        file.write(f"{default_input_value}")
        if i < len(model["INPUTS"].keys()) - 1:
            file.write(", ")
    file.write("};\n")

    # declare algebraic states, i.e. a state whose derivative does not appear in state expressions
    file.write("// {#nrdifferentialstates,<differentialstate index>}\n")
    differentialstates = [
        i for i, state in enumerate(model["STATES"].values()) if not state["isalgebraic"]
    ]
    _list_declaration(
        file,
        model["NAME"] + "_differentialstates",
        [len(differentialstates), *differentialstates],
        kind=1,
    )

    # declare dependency on input, i.e. which inputs are needed to compute outputs
    file.write("// {#depency,<input numbers>}\n")
    inputdependencies = _get_input_dependencies(model)
    _list_declaration(
        file,
        model["NAME"] + "_inputdependency",
        [len(inputdependencies), *inputdependencies],
        kind=1,
    )

    # default parameters
    _list_declaration(
        file,
        model["NAME"] + "_defaultparameters",
        [itemdict["expression"] for _, itemdict in model["PARAMETERS"].items()],
        kind=2,
    )
    file.write(
        'const char {}_timeunit[] = "{}";\n\n'.format(
            model["NAME"],
            model["METADATA"]["time_unit"],
        ),
    )

    for funcname, itemdict in model["FUNCTIONS"].items():
        file.write(f"static double {funcname}(")
        args = itemdict["args"]
        for i in range(len(args)):
            if i < len(args) - 1:
                file.write(f"double {args[i]},")
            else:
                file.write(f"double {args[i]}")
        file.write("){{\n\treturn {};\n".format(itemdict["expression"]))
        file.write("}\n\n")

    # Model functionZERO
    file.write(
        "static void {}_modelfunction(double time, double timescale, double *statevector, double *derivativevector, double *RESvector, double *parametervector, double *featurevector, double *outputvector, double **inputvector, double *eventvector, int *eventstatus, int DOflag){{\n".format(  # noqa: E501
            model["NAME"],
        ),
    )
    _variable_declaration(file, list(model["STATES"].keys()))
    if model["ALGEQUATIONS"]:
        # model is a DAE, derivatives can be used as any other variable, defined as ddt_state
        file.write(
            "\t[[maybe_unused]] double timescale_inv = 1 / timescale;\n",
        )  # needed to convert to local derivativevector
        _variable_declaration(
            file,
            ["ddt_" + name for name, state in model["STATES"].items() if not state["isalgebraic"]],
        )
    _variable_declaration(file, list(model["PARAMETERS"].keys()))
    _variable_declaration(file, list(model["INPUTS"].keys()), is_input=True)
    _variable_declaration(file, list(model["VARIABLES"].keys()))
    file.write("\n")

    # states
    for i, name in enumerate(model["STATES"]):
        file.write(f"\t{name} = statevector[{i}];\n")
    # derivatives
    if model["ALGEQUATIONS"]:
        for i, (name, state) in enumerate(model["STATES"].items()):
            if not state["isalgebraic"]:  # No derivative for algebraic states
                file.write(
                    "\t{} = timescale_inv * derivativevector[{}];\n".format("ddt_" + name, i),
                )
    # parameters
    for i, name in enumerate(model["PARAMETERS"]):
        file.write(f"\t{name} = parametervector[{i}];\n")
    # inputs
    for i, (name, itemdict) in enumerate(model["INPUTS"].items()):
        expression = re.sub(
            r"\b[a-zA-Z_][a-zA-Z0-9_:]*\b(?!\()",
            f"(*inputvector[{i}])",
            itemdict["expression"],
        )

        # Trim leading colon if present
        if expression[0] == ":":
            expression = expression[1:]

        if itemdict["defaultvalue"] and itemdict["defaultvalue"] != "ZERO":
            file.write(
                f"\t{name} = (inputvector[{i}]) ? {expression} : {itemdict['defaultvalue']};\n",
            )  # non-mandatory inputs
        else:
            file.write(f"\t{name} = {expression};\n")  # mandatory inputs
    # variables
    for name, itemdict in model["VARIABLES"].items():
        file.write("\t{} = {};\n".format(name, itemdict["expression"]))

    # DDT
    file.write("\n\tif (DOflag == DOFLAG_DDT) {\n")
    # only for ODE
    if not model["ALGEQUATIONS"]:
        for i, (_, itemdict) in enumerate(model["STATES"].items()):
            file.write(
                "\t\tderivativevector[{}] = timescale * ({});\n".format(i, itemdict["expression"]),
            )
    file.write("\t}")

    # OUTPUT
    file.write(" else if (DOflag == DOFLAG_OUTPUT) {\n")
    for i, (_, itemdict) in enumerate(model["OUTPUTS"].items()):
        file.write("\t\toutputvector[{}] = {};\n".format(i, itemdict["expression"]))
    file.write("\t}")

    # FEATURE
    file.write(" else if (DOflag == DOFLAG_FEATURE) {\n")
    for i, (_, itemdict) in enumerate(model["FEATURES"].items()):
        file.write("\t\tfeaturevector[{}] = {};\n".format(i, itemdict["expression"]))
    file.write("\t}")

    # EVENT
    file.write(" else if (DOflag == DOFLAG_EVENT) {\n")
    for i, (_, itemdict) in enumerate(model["EVENTS"].items()):
        file.write("\t\teventvector[{}] = ({}) - 0.5;\n".format(i, itemdict["condition"]))
    file.write("\t}")

    # EVENTASSIGN
    file.write(" else if (DOflag == DOFLAG_EVENTASSIGN) {\n")
    for i, (_, itemdict) in enumerate(model["EVENTS"].items()):
        file.write(f"\t\tif(eventstatus[{i}] == 1){{\n")
        for assign in itemdict["assignments"]:
            if assign["vartype"] == 0:  # state
                file.write(f"\t\t\tstatevector[{assign['varindex']}] = {assign['expression']};\n")
            elif assign["vartype"] == 1:  # parameter
                file.write(
                    f"\t\t\tparametervector[{assign['varindex']}] = {assign['expression']};\n",
                )
        file.write("\t\t}\n")
    file.write("\t}")

    # RESIDUAL
    file.write(" else if (DOflag == DOFLAG_RESIDUAL) {\n")
    # ODEs
    ode_states = [
        (i, state) for i, state in enumerate(model["STATES"].values()) if "expression" in state
    ]
    for k in range(len(ode_states)):
        if (
            k != ode_states[k][0]
        ):  # here as a check, ODE states should be at the top of model["STATES"]
            msg = "Programming error...bug in code"
            raise ValueError(msg)
        file.write(
            "\t\tRESvector[{}] = timescale * ({}) - derivativevector[{}];\n".format(
                k,
                ode_states[k][1]["expression"],
                k,
            ),
        )
    # Algebraic
    k = len(ode_states)
    for alg in model["ALGEQUATIONS"]:
        file.write(f"\t\tRESvector[{k}] = timescale * ({alg});\n")
        k += 1
    file.write("\t}\n")

    file.write("}\n\n")

    ########## IC function ##########
    _write_initial_conditions(file, model)

    file.write("/* Functions for Python C API Extension */\n")
    file.write(f"static PyTypeObject {model['NAME']}_Type = {{\n")
    file.write("\t.ob_base = PyVarObject_HEAD_INIT(NULL, 0)\n")
    file.write(f'\t.tp_name =  "sund.Models.{model["NAME"]}.{model["NAME"]}",\n')
    file.write("\t.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,\n")

    # Add the docstring
    docstring = _build_model_docstring(model)
    file.write(f'\t.tp_doc = "{docstring}",\n')

    file.write(f"\t.tp_new = {model['NAME']}_new,\n")
    file.write("};\n\n")

    file.write(f"static ModelStructure {model['NAME']} = {{\n")
    file.write(f"\t.function = {model['NAME']}_modelfunction,\n")
    file.write(f"\t.initialcondition = {model['NAME']}_initialcondition,\n")
    file.write(f"\t.numberof = {model['NAME']}_numberof,\n")
    file.write(f"\t.statenames = {model['NAME']}_statenames,\n")
    file.write(f"\t.featurenames = {model['NAME']}_featurenames,\n")
    file.write(f"\t.featureunits = {model['NAME']}_featureunits,\n")
    file.write(f"\t.outputnames = {model['NAME']}_outputnames,\n")
    file.write(f"\t.inputnames = {model['NAME']}_inputnames,\n")
    file.write(f"\t.parameternames = {model['NAME']}_parameternames,\n")
    file.write(f"\t.eventnames = {model['NAME']}_eventnames,\n")
    file.write(f"\t.differentialstates = {model['NAME']}_differentialstates,\n")
    file.write(f"\t.inputdependency = {model['NAME']}_inputdependency,\n")
    file.write(f"\t.defaultparameters = {model['NAME']}_defaultparameters,\n")
    file.write(f"\t.timeunit = {model['NAME']}_timeunit,\n")
    file.write(f"\t.has_algebraic_eq = {1 if model['ALGEQUATIONS'] else 0},\n")
    file.write(f"\t.mandatoryinputs = {model['NAME']}_mandatoryinputs,\n")
    file.write(f"\t.defaultInputs = {model['NAME']}_defaultInputs\n")
    file.write("};\n\n")

    file.write("static PyObject *\n")
    file.write(f"{model['NAME']}_new(PyTypeObject *type, PyObject *args, PyObject *kwds){{\n")
    file.write("\tModelObject *self;\n")
    file.write("\tself = (ModelObject *) type->tp_alloc(type, 0);\n")
    file.write("\tif (self) {\n")
    file.write(f"\t\tself->model = &{model['NAME']};\n")
    file.write("\t\tif(Model_alloc(self) < 0){\n")
    file.write("\t\t\tPy_DECREF(self);\n")
    file.write("\t\t\treturn NULL;\n")
    file.write("\t\t}\n")
    file.write("\t}\n")
    file.write("\treturn (PyObject *) self;\n")
    file.write("}\n\n")

    file.write(f"static PyModuleDef {model['NAME']}Module = {{\n")
    file.write("\t.m_base = PyModuleDef_HEAD_INIT,\n")
    file.write(f'\t.m_name = "sund.Models.{model["NAME"]}",\n')
    file.write(f'\t.m_doc = "{model["NAME"]} Module",\n')
    file.write("\t.m_size = -1\n")
    file.write("};\n\n")

    file.write("PyMODINIT_FUNC\n")
    file.write(f"PyInit_{model['NAME']}(void){{\n")
    file.write("\tPyObject *m;\n\n")

    file.write(f"\tm = PyModule_Create(&{model['NAME']}Module);\n")
    file.write("\tif (m == NULL)\n")
    file.write("\t\treturn NULL;\n\n")

    file.write("\timport_ModelCoreAPI();\n")
    file.write(f"\t{model['NAME']}_Type.tp_base = Model_Base_Type;\n")
    file.write(f"\tif (PyType_Ready(&{model['NAME']}_Type) < 0){{\n")
    file.write("\t\tPy_DECREF(m);\n")
    file.write("\t\treturn NULL;\n")
    file.write("\t}\n\n")

    file.write(f"\tPy_INCREF(&{model['NAME']}_Type);\n")

    file.write(
        f'\tif (PyModule_AddObject(m, "{model["NAME"]}", (PyObject *) &{model["NAME"]}_Type) < 0){{\n',  ## noqa: E501
    )
    file.write(f"\t\tPy_DECREF(&{model['NAME']}_Type);\n")
    file.write("\t\tPy_DECREF(m);\n")
    file.write("\t\treturn NULL;\n")
    file.write("\t}\n\n")

    file.write("\treturn m;\n")
    file.write("}")


##################################################################################################
# Compile functions
##################################################################################################


def _compile_macros(txt):
    names, values = _name_value_pair(txt)
    return {
        name: {"expression": _replace_expr(value)}
        for name, value in zip(names, values, strict=False)
    }


def _compile_parameters(txt):
    names, values = _name_value_pair(txt)
    for name, value in zip(names, values, strict=False):
        if not _is_number(_replace_expr(value)):
            msg = f"Parameters can only be assigned to numbers, incorrect definition for parameter '{name}': '{value}'"  # noqa: E501
            raise ValueError(msg)
    return {
        name: {"expression": _replace_expr(value)}
        for name, value in zip(names, values, strict=False)
    }


def _compile_variables(model, txt):
    names, values = _name_value_pair(txt)
    variables = {
        name: {"expression": _replace_expr(value), "inputdependency": None, "statedependent": False}
        for name, value in zip(names, values, strict=False)
    }
    _get_variable_dependency(model, variables)
    return variables


def _compile_inputs(txt):
    names, values = _name_value_pair(txt)
    extvars = len(names) * [None]
    defvals = len(names) * [None]  # default values

    for i, value_raw in enumerate(values):
        # Handle default values (marked with @)
        parts = value_raw.split("@")
        if len(parts) > 1:
            defvals[i] = _replace_expr(parts[1])
            if defvals[i] == "":
                msg = f"Missing default input value for input {names[i]}!"
                raise SyntaxError(msg)
        else:
            defvals[i] = None

        # Remove whitespace
        value = parts[0].strip()
        values[i] = value

        # Check if value is a valid expression
        varinexpr = list(set(re.findall(r":?\b[a-zA-Z_][a-zA-Z0-9_:]*\b(?!\()", value)))

        if len(varinexpr) != 1:
            msg = f'Incorrect input definition for input {names[i]}: "{value}"'
            raise ValueError(msg)
        if varinexpr[0].count(":") > 1:
            msg = (
                f'Incorrect input definition for input {names[i]}: "{value}". Maximally one ":" is allowed in the input expression.',  # noqa: E501
            )
            raise ValueError(msg)
        if varinexpr[0].endswith(":") or value.endswith(":"):
            msg = (
                f'Incorrect input definition for input {names[i]}: "{value}". No input listed after container name (i.e. ":" not allowed as the last character in the input).',  # noqa: E501
            )
            raise ValueError(msg)
        extvars[i] = varinexpr[0]

    return {
        name: {"expression": _replace_expr(value), "externvariable": extvar, "defaultvalue": defval}
        for name, value, extvar, defval in zip(names, values, extvars, defvals, strict=False)
    }


def _compile_metadata(txt):
    names, values = _name_value_pair(txt)

    # Check for required time_unit
    if "time_unit" not in names:
        msg = "Metadata is missing mandatory 'time_unit' definition!"
        raise SyntaxError(msg)

    # Strip quotes from time_unit value
    time_unit_idx = names.index("time_unit")
    time_unit_value = _strip_quotes(values[time_unit_idx]).strip()
    # Normalize the string to MICRO SIGN (U+00B5) for microseconds.
    time_unit_value = time_unit_value.replace("µ", "µ")
    values[time_unit_idx] = time_unit_value

    # Check time_unit
    if time_unit_value not in ["ns", "µs", "ms", "s", "m", "h", "d", "y"]:
        msg = (
            f"Incorrect definition of argument 'time_unit' ('{time_unit_value}'). Use either of: 'ns', 'µs', 'ms', 's', 'm', 'h', 'd', 'w' or 'y'",  # noqa: E501
        )
        raise ValueError(msg)
    return dict(zip(names, values, strict=False))


def _compile_state_equations(txt):  # noqa: C901, PLR0912
    names, values = _name_value_pair(txt)
    # change old writing: d/dt(state) to new: ddt_state
    names = [_replaceddt(name) for name in names]
    # check names
    for name in names:
        # look for: derivative expression | algebraic expression | state IC | state derivative IC
        if not re.search(r"^(ddt_\w+|0|\w+\(0\)|ddt_\w+\(0\))$", name):
            msg = f"Incorrect definition in state section: '{name}'"
            raise ValueError(msg)
    # search for ODE states, here "expression" in the inner dict is the derivative expression,
    # i.e. RHS of d/dty = f(t,y)
    states = {
        state[0].group("state"): {
            "expression": _replace_expr(state[1]),
            "ic": 0,
            "deric": 0,
            "isalgebraic": False,
        }
        for state in (
            (re.search(r"^ddt_(?P<state>\w+)$", name), value)
            for name, value in zip(names, values, strict=False)
        )
        if state[0]
    }
    # search for algebraic equations
    algebraiceqs = [
        _replace_expr(value) for name, value in zip(names, values, strict=False) if name == "0"
    ]
    nrequations = len(states) + len(algebraiceqs)
    # search for state IC
    ics = {
        state[0].group("state"): _replace_expr(state[1])
        for state in (
            (re.search(r"^(?!ddt_)(?P<state>\w+)\(0\)$", name), value)
            for name, value in zip(names, values, strict=False)
        )
        if state[0]
    }
    # search for state derivative IC
    derics = {
        state[0].group("state"): _replace_expr(state[1])
        for state in (
            (re.search(r"^ddt_(?P<state>\w+)\(0\)$", name), value)
            for name, value in zip(names, values, strict=False)
        )
        if state[0]
    }

    # Check for initial conditions without corresponding derivative definitions (only ODE models)
    missing_states = []
    if not algebraiceqs:  # Only apply this validation to ODE models
        missing_states.extend([state_name for state_name in ics if state_name not in states])

    if len(missing_states) == 1:
        msg = (
            f"State '{missing_states[0]}' has an initial condition but no corresponding derivative definition (ddt_{missing_states[0]})",  # noqa: E501
        )
        raise ValueError(msg)

    if len(missing_states) > 1:
        msg = (
            f"States {missing_states} have initial conditions but no corresponding derivative definitions (ddt_{missing_states[0]} etc.)",  # noqa: E501
        )
        raise ValueError(msg)

    # add ODE state IC:s
    for state, itemdict in states.items():
        if state in ics:
            itemdict["ic"] = ics[state]
        else:
            msg = f"Missing initial condition for ODE state '{state}'"
            raise ValueError(msg)
        if state in derics:  # Optional for ODE state
            itemdict["deric"] = derics[state]
    # Check type alebraic equations present
    if algebraiceqs:  # DAE
        # add differential states, defined by having a IC, ddt_state(0), defined for the derivative
        for state, deric in derics.items():
            if state not in states:
                if state not in ics:  # diffstates also need a IC for the actual state: state(0)
                    msg = f"Missing initial condition for differential state '{state}'"
                    raise ValueError(msg)
                if not _contains_derivate(
                    state,
                    values,
                ):  # check that derivate is present for differential state
                    msg = f"Missing derivative for differential state '{state}' in state equations"
                    raise ValueError(msg)
                states[state] = {"ic": ics[state], "deric": deric, "isalgebraic": False}
        # add algebraic states
        for state, ic in ics.items():
            if state not in states:
                if _contains_derivate(
                    state,
                    values,
                ):  # check that derivate is not present for algebraic state
                    msg = f"Derivative for algebraic state '{state}' present in state equations"
                    raise ValueError(msg)
                # Check that the state appears in at least one algebraic equation
                appears_in_equations = any(
                    re.search(r"\b" + re.escape(state) + r"\b", eq) for eq in algebraiceqs
                )
                if not appears_in_equations:
                    msg = (
                        f"State '{state}' has an initial condition but does not appear in any derivative definition or algebraic equation",  # noqa: E501
                    )
                    raise ValueError(msg)
                # even though algebraic state have no derivative,
                # IDA need a IC for its derivative, i.e. 'deric'
                states[state] = {
                    "ic": ic,
                    "deric": 0,
                    "isalgebraic": True,
                }
    # check equal number of states as equations
    nrstates = len(states)
    if nrstates != nrequations:
        msg = f"Unequal number of states: {nrstates} and equations: {nrequations}"
        raise ValueError(msg)
    return states, algebraiceqs


def _compile_functions(txt):
    names, values = _name_value_pair(txt)
    functions = {}
    for name, value in zip(names, values, strict=False):
        g_start, g_end = _find_first_group(name)
        args = _split_expr(name[g_start:g_end], ",")
        functions[name[: g_start - 1]] = {"expression": _replace_expr(value), "args": args}
    return functions


def _compile_events(model, txt):
    statenames = list(model["STATES"].keys())
    parameternames = list(model["PARAMETERS"].keys())

    names, values = _name_value_pair(txt)
    events = {}
    for name, value in zip(names, values, strict=False):
        elements = _split_expr(value, ",")
        if (len(elements) % 2) == 0:
            msg = f"Incorrect event definition '{value}'"
            raise ValueError(msg)
        assignments = []
        i = 0
        while i < len(elements[1:]):
            assign = {
                "vartype": None,
                "varindex": None,
                "expression": None,
            }  # vartype: 0 = STATE, 1 = PARAMETER
            var = _remove_white_space(elements[1 + i])
            expr = _replace_expr(elements[2 + i])

            if var in statenames:
                assign["vartype"] = 0
                assign["varindex"] = statenames.index(var)
                assign["expression"] = expr
            elif var in parameternames:
                assign["vartype"] = 1
                assign["varindex"] = parameternames.index(var)
                assign["expression"] = expr
            else:
                msg = (
                    f"Incorrect definition of event assign to variable '{var}' which needs to be a parameter or state",  # noqa: E501
                )
                raise ValueError(msg)

            assignments.append(assign)
            i += 2

        events[name] = {"condition": _replace_expr(elements[0]), "assignments": assignments}
    return events


def _compile_outputs(txt):
    names, values = _name_value_pair(txt)
    return {
        name: {"expression": _replace_expr(value)}
        for name, value in zip(names, values, strict=False)
    }


def _compile_features(txt):
    names, values = _name_value_pair(txt, keepspace=True)
    features = {}

    for name, value in zip(names, values, strict=False):
        unit_start = value.find("[")
        unit_end = value.find("]")
        if unit_start < 0:
            unit = "1"
        elif unit_end < 0:
            msg = "Missing closing bracket of unit definition!"
            raise SyntaxError(msg)
        elif unit_start >= unit_end:
            msg = "Encountered closing bracket without precursory opening bracket!"
            raise SyntaxError(msg)
        else:
            unit = value[unit_start + 1 : unit_end]
            value = value[:unit_start]  # noqa: PLW2901
        features[name] = {"expression": _replace_expr(value), "unit": _remove_white_space(unit)}
    return features


##################################################################################################
# Helper functions
##################################################################################################
def _is_number(s):
    try:
        float(s)
        return True  # noqa: TRY300
    except ValueError:
        return False


def _find_file(name, path):
    path_obj = Path(path)
    for file_path in path_obj.rglob(name):
        return str(file_path)
    return ""


def _txt_parts(txt, section_names):
    # remove comments
    txt = _remove_comments(txt)

    # find section parts
    indices = [
        {"Section": section, "Span": _section_span(txt, section)} for section in section_names
    ]
    indices.append({"Section": "END", "Span": (len(txt) + 1, -1)})
    indices = sorted(indices, key=lambda x: x["Span"][0])

    section = {}
    for i in range(len(indices) - 1):
        section[indices[i]["Section"]] = txt[
            indices[i]["Span"][1] : indices[i + 1]["Span"][0] - 1
        ].strip()
    return section


def _section_span(txt, section):
    s = re.search(f"########## {section}", txt)
    if not s:
        msg = f"Textfile missing {section}-section."
        raise ValueError(msg)
    return s.span()


def _remove_white_space(txt):
    return txt.strip()


def _name_value_pair(txt, *, keepspace=False):
    indices = _declaration_indices(txt)
    indices.append(len(txt))
    names = []
    values = []
    for i in range(len(indices) - 1):
        txt_line = txt[indices[i] : indices[i + 1]]
        equal_index = txt_line.find("=")
        if keepspace:
            names.append(txt_line[0:equal_index].strip())
        else:
            names.append(_remove_white_space(txt_line[0:equal_index]))
        values.append(txt_line[equal_index + 1 :].strip())
    unique_names = set()
    for name in names:
        if name != "0" and name in unique_names:
            msg = f"Multiple definitions of: '{name}'"
            raise SyntaxError(msg)
        unique_names.add(name)
    return names, values


def _declaration_indices(txt):
    return [m.start() for m in re.finditer(r"\n[^\n]*=", "\n" + txt)]


def _convert_to_double(txt):
    return re.sub(r"\b(?<!\.)(?<![eE][-+])(\d+)(?!\.)(\b|[eE][\d+-])", r"\g<1>.0\g<2>", txt)


def _convert_power_expr(txt):
    txtorg = txt

    # Check for invalid expression
    if "* *" in txt:
        msg = f"Invalid expression: '* *' found in equation: '{txtorg}'"
        raise ValueError(msg)

    # Replace all spaces around power operators
    txt = txt.replace("**", "^")  # replace ** with ^ for easier handling
    txt = re.sub(r"\s*\^\s*", "^", txt)  # remove ALL spaces around ^

    # Check for invalid power operators (3 or more consecutive *)
    match = re.search(r"\*{3,}", txt)
    if match:
        msg = f"Invalid power operator '{match.group()}' found in equation: '{txtorg}'"
        raise ValueError(msg)

    while True:
        if "^" not in txt:
            break

        i = txt.index("^")

        pre_expr = txt[:i]
        post_expr = txt[i + 1 :]
        try:
            base_start = _find_base_start(pre_expr)
            exp_end = _find_exp_end(post_expr)
        except (ValueError, IndexError) as err:
            msg = f"Incorrect equation definition: '{txtorg}'"
            raise ValueError(msg) from err

        txt = f"{pre_expr[:base_start]}pow({pre_expr[base_start:]},{post_expr[:exp_end]}){post_expr[exp_end:]}"  # noqa: E501

    return txt


def _find_base_start(expr):
    m = re.search(r"(\d+(\.\d+)?|\w+)$", expr)
    if m:
        return len(expr) - len(m.group())
    g_start, _ = _find_first_group(expr, from_end=1)
    return g_start - 1


def _find_exp_end(expr):
    m = re.search(r"^([+-]?\d+(\.\d+)?|\w+)", expr)
    if m:
        return len(m.group())
    _, g_end = _find_first_group(expr, from_end=0)
    return g_end + 1


def _split_expr(txt, delimiter):
    elements = []
    next_element = 0
    open_par = 0
    for i, c in enumerate(txt):
        if c == "(":
            open_par += 1
        elif c == ")":
            open_par -= 1
        elif c == delimiter and open_par == 0:
            elements.append(txt[next_element:i])
            next_element = i + 1
    elements.append(txt[next_element:])
    return elements


def _find_first_group(txt, from_end=0):
    if from_end:
        txt = txt[::-1]
        g_open = ")"
        g_close = "("
    else:
        g_open = "("
        g_close = ")"

    index_start = txt.index(g_open) + 1
    open_par = 1
    for i in range(index_start, len(txt)):
        if txt[i] == g_open:
            open_par += 1
        elif txt[i] == g_close:
            open_par -= 1
        if open_par == 0:
            if from_end:
                return len(txt) - i, len(txt) - index_start
            return index_start, i
    if from_end:
        txt = txt[::-1]
    msg = f"Unable to parse equation: '{txt}'"
    raise ValueError(msg)


_MAXPERROW = 20


def _list_declaration(file, name, items, kind=0):  # noqa: C901, PLR0912, PLR0915
    nritems = len(items)
    if kind == 0:  # strings
        if nritems == 0:
            file.write(f"const char *{name}[1]{{}};\n")
        else:
            file.write(f"const char *{name}[{len(items)}] = {{\n")
            i = 0
            i_row = 0
            while i < len(items):
                if i_row >= _MAXPERROW:
                    file.write(",\n")
                    i_row = 0
                if i_row == 0:
                    file.write(f'\t"{items[i]}"')
                else:
                    file.write(f',"{items[i]}"')
                i += 1
                i_row += 1
            file.write("};\n")
    elif kind == 1:  # int
        if nritems == 0:
            file.write(f"const int {name}[1]{{}};\n")
        else:
            file.write(f"const int {name}[{len(items)}] = {{\n")
            i = 0
            i_row = 0
            while i < len(items):
                if i_row >= _MAXPERROW:
                    file.write(",\n")
                    i_row = 0
                if i_row == 0:
                    file.write(f"\t{items[i]}")
                else:
                    file.write(f",{items[i]}")
                i += 1
                i_row += 1
            file.write("};\n")
    elif kind == 2:  # double
        if nritems == 0:
            file.write(f"const double {name}[1]{{}};\n")
        else:
            file.write(f"const double {name}[{len(items)}] = {{\n")
            i = 0
            i_row = 0
            while i < len(items):
                if i_row >= _MAXPERROW:
                    file.write(",\n")
                    i_row = 0
                if i_row == 0:
                    file.write(f"\t{items[i]}")
                else:
                    file.write(f",{items[i]}")
                i += 1
                i_row += 1
            file.write("};\n")


def _get_variable_dependency(model, variables):
    for variable in variables:
        mandatory_input_dependencies = set()
        state_dependency = False
        expression = variables[variable]["expression"]
        references = re.findall(r"\b\w+\b(?!\()", expression)

        for reference in references:
            if reference in model["INPUTS"]:
                if model.get("INPUTS").get(reference).get("defaultvalue") is None:
                    mandatory_input_dependencies.add(list(model.get("INPUTS")).index(reference))
            elif reference in variables:
                if list(variables).index(reference) >= list(variables).index(variable):
                    msg = (
                        f"Variable '{variable}' depends on variable '{reference}' which is defined after variable '{variable}'",  # noqa: E501
                    )
                    raise ValueError(msg)
                if variables.get(reference).get("mandatory_input_dependencies"):
                    mandatory_input_dependencies.union(
                        variables.get(reference).get("mandatory_input_dependencies"),
                    )
                if variables[reference]["state_dependency"]:
                    state_dependency = True
            elif (
                reference in model["STATES"]
                or reference in ["ddt_" + state for state in model["STATES"]]
                or reference == "time"
            ):
                state_dependency = True

        variables[variable]["mandatory_input_dependencies"] = mandatory_input_dependencies
        variables[variable]["state_dependency"] = state_dependency


def _get_input_dependencies(model):
    dependencies = set()

    for itemdict in model["OUTPUTS"].values():
        expression = itemdict["expression"]
        references = re.findall(r"\b\w+\b(?!\()", expression)
        for reference in references:
            if reference in model["INPUTS"]:
                dependencies.add(list(model.get("INPUTS")).index(reference))
            elif reference in model["VARIABLES"]:
                dependencies.union(
                    model.get("VARIABLES").get(reference).get("mandatory_input_dependencies"),
                )
    return list(dependencies)


def _variable_declaration(file, items, *, is_input=False):
    if len(items) > 0:
        if is_input:
            file.write("\t[[maybe_unused]] double ")
        else:
            file.write("\tdouble ")
        i = 0
        i_row = 0
        while i < len(items):
            if i_row >= _MAXPERROW:
                file.write(";\n\tdouble ")
                i_row = 0
            if i_row == 0:
                file.write(f"{items[i]}")
            else:
                file.write(f",{items[i]}")
            i += 1
            i_row += 1
        file.write(";\n")


def _ic_variable_declaration(file, items):
    if len(items) > 0:
        file.write("\t[[maybe_unused]] double ")
        i = 0
        i_row = 0
        while i < len(items):
            if i_row >= _MAXPERROW:
                file.write(";\n\t[[maybe_unused]] double ")
                i_row = 0
            if i_row == 0:
                file.write(f"{items[i]}")
            else:
                file.write(f",{items[i]}")
            i += 1
            i_row += 1
        file.write(";\n")


def _replaceddt(txt):
    # replace d/dt(state) with ddt_state to make it a c valid name
    return re.sub(r"d/dt\((\w+)\)", r"ddt_\g<1>", txt)


def _convert_abs(txt):
    return re.sub(r"\babs\b", r"fabs", txt)


def _replace_expr(txt):
    comment = txt.find("//")
    if comment > -1:
        txt = txt[:comment]
    return _convert_abs(
        _convert_power_expr(_convert_to_double(_replaceddt(_remove_white_space(txt)))),
    )


def _contains_derivate(state, exprs):
    return any(re.search(r"(d/dt\(" + state + r"\)|ddt_" + state + r")", expr) for expr in exprs)


def _remove_comments(string):
    # Protect section markers and escaped hashes
    string = string.replace("##########", "__SECTION_MARKER__")
    string = string.replace(r"\#", "__ESCAPED_HASH__")

    # Remove all occurrences of streamed comments (/* ... */)
    string = re.sub(re.compile(r"/\*.*?\*/", re.DOTALL), "", string)

    # Remove all occurrences of single-line comments (// ...)
    string = re.sub(re.compile(r"//[^\n]*"), "", string)

    # Remove '#' comments (not at start of line, since section marker is protected)
    string = re.sub(re.compile(r"#.*$", re.MULTILINE), "", string)

    # Restore section markers and escaped hashes
    string = string.replace("__SECTION_MARKER__", "##########")
    string = string.replace("__ESCAPED_HASH__", "#")

    return string  # noqa: RET504
