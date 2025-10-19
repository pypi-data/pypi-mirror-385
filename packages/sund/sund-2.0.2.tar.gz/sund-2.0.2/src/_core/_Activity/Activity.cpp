#include "Activity.h"
#include "_StringList_C_API.h"
#include "pyarraymacros.h"
#include "pyerrors.h"
#include "pysplineaddon.h"
#include "sund_sundials_interface.h"

#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_2_3_API_VERSION
#include <cstring>
#include <numpy/arrayobject.h>

/// Constants for type declaration
#define CONSTANT 0
#define PIECEWISE_CONSTANT 1
#define PIECEWISE_LINEAR 2
#define CUBIC_SPLINE 3
#define STATE_MANIPULATION 4

/*
==========================================================================================
Helper functions
==========================================================================================
*/

// Convert string type to integer constant for internal use
static int getTypeFromString(const char *type_str) {
  if (strcmp(type_str, "constant") == 0) {
    return CONSTANT;
  } else if (strcmp(type_str, "piecewise_constant") == 0) {
    return PIECEWISE_CONSTANT;
  } else if (strcmp(type_str, "piecewise_linear") == 0) {
    return PIECEWISE_LINEAR;
  } else if (strcmp(type_str, "cubic_spline") == 0) {
    return CUBIC_SPLINE;
  } else {
    return -1; // Invalid type
  }
}

// Convert integer constant back to string type
static const char *getStringFromType(int type) {
  switch (type) {
  case CONSTANT:
    return "constant";
  case PIECEWISE_CONSTANT:
    return "piecewise_constant";
  case PIECEWISE_LINEAR:
    return "piecewise_linear";
  case CUBIC_SPLINE:
    return "cubic_spline";
  case STATE_MANIPULATION:
    return "state_manipulation";
  default:
    return "unknown";
  }
}

/*
==========================================================================================
Output functions
==========================================================================================
*/
static double Constant_function(ConstantOutput *self, double time_local) {
  return self->constant;
}

static double PiecewiseConstant_function(PiecewiseOutput *self,
                                         double time_local) {
  return piecewise(PYSIZE(self->tvalues), time_local, PYDATA(self->tvalues),
                   PYDATA(self->fvalues));
}

static double PiecewiseLinear_function(PiecewiseOutput *self,
                                       double time_local) {
  return linearInterpolate(PYSIZE(self->tvalues), time_local,
                           PYDATA(self->tvalues), PYDATA(self->fvalues));
}

static double CubicInterpolate_function(CubicSplineOutput *self,
                                        double time_local) {
  return seval(PYSIZE(self->tvalues), time_local, PYDATA(self->tvalues),
               PYDATA(self->fvalues), self->b, self->c, self->d, &self->last);
}

static double StateManipulation_function(ActivityStateManipulation *self,
                                         double time_local) {
  return stateManipulation(PYSIZE(self->tvalues), time_local,
                           PYDATA(self->tvalues), PYDATA(self->fvalues),
                           self->mode);
}

/*
==========================================================================================
GETTERS AND SETTERS
==========================================================================================
*/

static PyObject *Activity_GetManipulationNames(ActivityObject *self,
                                               void *closure) {
  // Simply return the separate manipulationNames list
  Py_INCREF(self->manipulationNames);
  return self->manipulationNames;
}

static PyObject *Activity_GetOutputs(ActivityObject *self, void *closure) {
  Py_INCREF(self->outputNames);
  return self->outputNames;
}

static int Activity_SetOutputs(ActivityObject *self, PyObject *value,
                               void *closure) {
  return StringList_Update(self->outputNames, value);
}

static int Activity_SetManipulationNames(ActivityObject *self, PyObject *value,
                                         void *closure) {
  return StringList_Update(self->manipulationNames, value);
}

static PyObject *Activity_GetFeatures(ActivityObject *self, void *closure) {
  Py_INCREF(self->featureNames);
  return self->featureNames;
}

static int Activity_SetFeatures(ActivityObject *self, PyObject *value,
                                void *closure) {
  return StringList_Update(self->featureNames, value);
}

static PyObject *Activity_GetFeatureunits(ActivityObject *self, void *closure) {
  Py_INCREF(self->featureUnits);
  return self->featureUnits;
}

static int Activity_SetFeatureunits(ActivityObject *self, PyObject *value,
                                    void *closure) {
  return StringList_Update(self->featureUnits, value);
}

static PyObject *Activity_GetTimeUnit(ActivityObject *self, void *closure) {
  Py_INCREF(self->timeUnit);
  return self->timeUnit;
}

static PyObject *Activity_GetContainer(ActivityObject *self, void *closure) {
  Py_INCREF(self->compartment); // internal storage reused
  return self->compartment;
}

static PyObject *Activity_GetCompartment(ActivityObject *self, void *closure) {
  // Emit a proper DeprecationWarning (stacklevel=2 so user code line is shown)
  if (PyErr_WarnEx(PyExc_DeprecationWarning,
                   "The 'compartment' attribute is deprecated; use 'container' "
                   "instead. In the future, 'compartment' will refer to volume "
                   "dependent compartments.",
                   1) < 0) {
    return NULL; // Propagate error if warning turned into exception
  }
  Py_INCREF(self->compartment);
  return self->compartment;
}

static PyGetSetDef Activity_getsetters[] = {
    {"output_names", (getter)Activity_GetOutputs, (setter)Activity_SetOutputs,
     "Output names", NULL},
    {"manipulation_names", (getter)Activity_GetManipulationNames,
     (setter)Activity_SetManipulationNames, "Manipulation names", NULL},
    {"feature_names", (getter)Activity_GetFeatures,
     (setter)Activity_SetFeatures, "Feature names", NULL},
    {"feature_units", (getter)Activity_GetFeatureunits,
     (setter)Activity_SetFeatureunits, "Feature units", NULL},
    {"time_unit", (getter)Activity_GetTimeUnit, NULL, "Activity time unit",
     NULL},
    {"container", (getter)Activity_GetContainer, NULL,
     "Activity container (formerly 'compartment')", NULL},
    {"compartment", (getter)Activity_GetCompartment, NULL,
     "DEPRECATED: use 'container' instead.", NULL},
    {NULL} /* Sentinel */
};

/*
==========================================================================================
PyMethods
==========================================================================================
*/

static bool Activity_UpdateOutput(ActivityObject *self, int outputIndex,
                                  ActivityOutput *newOutput, PyObject *name,
                                  PyObject *unit) {
  // Clean up the old output
  ActivityOutput *oldOutput = self->outputs[outputIndex];
  oldOutput->out_dealloc((PyObject *)oldOutput);

  // Update with new output
  self->outputs[outputIndex] = newOutput;

  // Update unit if provided
  if (unit) {
    PyObject *oldUnit = PyList_GetItem(self->featureUnits, outputIndex);
    if (oldUnit) {
      if (PyList_SetItem(self->featureUnits, outputIndex, unit) < 0) {
        return false;
      }
      Py_INCREF(unit); // Because SetItem steals the reference
    }
  }

  return true;
}

static void Activity_AddFeature(ActivityObject *self, ActivityOutput *activity,
                                PyObject *name, PyObject *unit) {
  PyObject *tmp;

  PyList_Append(self->featureNames, name);
  if (unit)
    PyList_Append(self->featureUnits, unit);
  else {
    tmp = PyUnicode_FromString("1");
    PyList_Append(self->featureUnits, tmp);
    Py_DECREF(tmp);
  }

  self->nrfeatures++;
  self->features = (ActivityOutput **)PyMem_Realloc(
      self->features, self->nrfeatures * sizeof(ActivityOutput *));
  self->features[self->nrfeatures - 1] = activity;
}

// allocation functions
PyObject *ACTIVITY::addOutput(ActivityObject *self, PyObject *args,
                              PyObject *kwds) {
  ActivityOutput *newOutput;
  static char *kwlist[] = {const_cast<char *>("type"),
                           const_cast<char *>("name"),
                           const_cast<char *>("t"),
                           const_cast<char *>("f"),
                           const_cast<char *>("unit"),
                           const_cast<char *>("feature"),
                           NULL};

  PyObject *type_obj{};
  PyObject *name{};
  PyObject *t{};
  PyObject *f{};
  PyObject *unit{};
  PyObject *feature{};

  if (!self->editable) {
    PyErr_SetString(PyExc_RuntimeError,
                    "The activity object is not editable since it has been "
                    "added to a simulation object.");
    return NULL;
  }

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|$OOOOOO", kwlist, &type_obj,
                                   &name, &t, &f, &unit, &feature)) {
    return NULL;
  }

  // Validate required arguments
  if (!type_obj) {
    PyErr_SetString(PyExc_TypeError, "The 'type' argument is required");
    return NULL;
  }

  if (!name) {
    PyErr_SetString(PyExc_TypeError, "The 'name' argument is required");
    return NULL;
  }

  if (!PyUnicode_Check(name)) {
    PyErr_SetString(PyExc_TypeError,
                    "The name of the output has to be a string");
    return NULL;
  }

  if (unit && !PyUnicode_Check(unit)) {
    PyErr_SetString(PyExc_TypeError,
                    "The unit of the output has to be a string");
    return NULL;
  }

  if (!PyUnicode_Check(type_obj)) {
    PyErr_SetString(PyExc_TypeError, "The 'type' argument must be a string.");
    return NULL;
  }

  const char *type_str = PyUnicode_AsUTF8(type_obj);
  if (!type_str) {
    return NULL;
  }

  // Convert string to type constant and validate
  int output_type = getTypeFromString(type_str);
  if (output_type == -1) {
    PyErr_SetString(
        PyExc_ValueError,
        "Invalid output type. Use one of: 'constant', 'piecewise_constant', "
        "'piecewise_linear', 'cubic_spline'.");
    return NULL;
  }

  // Create output based on type
  switch (output_type) {
  case CONSTANT:
    newOutput = Activity_ConstantOutput(f);
    break;
  case PIECEWISE_CONSTANT:
    newOutput = Activity_PiecewiseConstantOutput(t, f);
    break;
  case PIECEWISE_LINEAR:
    newOutput = Activity_PiecewiseLinearOutput(t, f);
    break;
  case CUBIC_SPLINE:
    newOutput = Activity_CubicSplineOutput(t, f);
    break;
  default:
    // This should never happen due to our validation above
    PyErr_SetString(PyExc_RuntimeError,
                    "Internal error: unexpected output type");
    return NULL;
  }

  if (!newOutput)
    return NULL;

  // Check if output with this name already exists among outputs only
  for (int i = 0; i < self->nroutputs; i++) {
    PyObject *existing_name = PyList_GetItem(self->outputNames, i);
    if (PyUnicode_Compare(name, existing_name) == 0) {
      // Name exists, update the output instead of adding new one
      if (!Activity_UpdateOutput(self, i, newOutput, name, unit)) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to update existing output");
        return NULL;
      }
      Py_DECREF(name);
      Py_RETURN_NONE;
    }
  }

  // check if compartment is set
  if (self->compartment != Py_None)
    name = PyUnicode_FromFormat("%S:%S", self->compartment, name);
  else
    Py_INCREF(name);

  PyList_Append(self->outputNames, name);
  self->nroutputs++;
  self->outputs = (ActivityOutput **)PyMem_Realloc(
      self->outputs, self->nroutputs * sizeof(ActivityOutput *));
  self->outputs[self->nroutputs - 1] = newOutput;
  if (feature && PyObject_IsTrue(feature)) {
    newOutput->isFeature = 1;
    Activity_AddFeature(self, newOutput, name, unit);
  } else
    newOutput->isFeature = 0;

  Py_DECREF(name);

  Py_RETURN_NONE;
}

static ActivityOutput *Activity_ConstantOutput(PyObject *constant) {
  ConstantOutput *newOutput;
  double c;

  // check constant = fvalues
  if (!constant) {
    PyErr_SetString(PyExc_ValueError, "No constant value given, please specify "
                                      "a constant using the 'f' argument");
    return NULL;
  }

  // Handle case where constant might be a sequence with single element
  PyObject *float_obj;
  if (PySequence_Check(constant) && !PyUnicode_Check(constant)) {
    // If it's a sequence (like list/tuple), try to get the first element
    if (PySequence_Size(constant) == 1) {
      PyObject *first_element = PySequence_GetItem(constant, 0);
      if (!first_element) {
        PyErr_SetString(PyExc_ValueError,
                        "Cannot extract element from sequence for 'f'. "
                        "Expected a single element sequence");
        return NULL;
      }
      float_obj = PyNumber_Float(first_element);
      Py_DECREF(first_element);
    } else {
      PyErr_SetString(
          PyExc_ValueError,
          "Constant sequence must contain exactly one element for 'f'");
      return NULL;
    }
  } else {
    // Convert to float directly (handles both int and float)
    float_obj = PyNumber_Float(constant);
  }

  if (!float_obj) {
    PyErr_SetString(PyExc_ValueError,
                    "Invalid value for 'f'. Expected a number (int or float)");
    return NULL;
  }
  c = PyFloat_AsDouble(float_obj);
  Py_DECREF(float_obj);
  if (PyErr_Occurred()) {
    PyErr_Clear();
    PyErr_SetString(PyExc_ValueError,
                    "Invalid value for 'f'. Expected a number (int or float)");
    return NULL;
  }

  newOutput = (ConstantOutput *)PyMem_Malloc(sizeof(ConstantOutput));
  newOutput->base.type = CONSTANT;
  newOutput->base.out_function = (OutputFunction)Constant_function;
  newOutput->base.out_dealloc = (destructor)Constant_dealloc;
  newOutput->constant = c;

  return (ActivityOutput *)newOutput;
}

static ActivityOutput *Activity_PiecewiseConstantOutput(PyObject *tvalues,
                                                        PyObject *fvalues) {
  PiecewiseOutput *newOutput;

  // check tvalues fvalues
  if (!tvalues) {
    PyErr_SetString(
        PyExc_ValueError,
        "No t-values given, please specify t-values using the 't' argument");
    return NULL;
  }
  if (!fvalues) {
    PyErr_SetString(
        PyExc_ValueError,
        "No f-values given, please specify f-values using the 'f' argument");
    return NULL;
  }

  tvalues = PyArray_FROM_OTF(tvalues, NPY_DOUBLE,
                             NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!tvalues) {
    PyErr_SetString(PyExc_ValueError, "Cannot convert tvalues to numpy array");
    return NULL;
  }
  fvalues = PyArray_FROM_OTF(fvalues, NPY_DOUBLE,
                             NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!fvalues) {
    Py_DECREF(tvalues);
    PyErr_SetString(PyExc_ValueError, "Cannot convert fvalues to numpy array");
    return NULL;
  }

  if (PYSIZE(fvalues) != PYSIZE(tvalues) + 1) {
    Py_DECREF(tvalues);
    Py_DECREF(fvalues);
    PyErr_SetString(PyExc_ValueError, "Incorrect number of t- and f-values");
    return NULL;
  }

  newOutput = (PiecewiseOutput *)PyMem_Malloc(sizeof(PiecewiseOutput));
  newOutput->base.type = PIECEWISE_CONSTANT;
  newOutput->base.out_function = (OutputFunction)PiecewiseConstant_function;
  newOutput->base.out_dealloc = (destructor)Piecewise_dealloc;
  newOutput->tvalues = tvalues;
  newOutput->fvalues = fvalues;

  return (ActivityOutput *)newOutput;
}

static ActivityOutput *Activity_PiecewiseLinearOutput(PyObject *tvalues,
                                                      PyObject *fvalues) {
  PiecewiseOutput *newOutput;

  // check tvalues fvalues
  if (!tvalues) {
    PyErr_SetString(
        PyExc_ValueError,
        "No t-values given, please specify t-values using the 't' argument");
    return NULL;
  }
  if (!fvalues) {
    PyErr_SetString(
        PyExc_ValueError,
        "No f-values given, please specify f-values using the 'f' argument");
    return NULL;
  }

  tvalues = PyArray_FROM_OTF(tvalues, NPY_DOUBLE,
                             NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!tvalues) {
    PyErr_SetString(PyExc_ValueError, "Cannot convert tvalues to numpy array");
    return NULL;
  }
  fvalues = PyArray_FROM_OTF(fvalues, NPY_DOUBLE,
                             NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!fvalues) {
    Py_DECREF(tvalues);
    PyErr_SetString(PyExc_ValueError, "Cannot convert fvalues to numpy array");
    return NULL;
  }

  if (PYSIZE(tvalues) < 2 || PYSIZE(tvalues) != PYSIZE(fvalues)) {
    Py_DECREF(tvalues);
    Py_DECREF(fvalues);
    PyErr_SetString(PyExc_ValueError, "Incorrect number of t- and f-values");
    return NULL;
  }

  newOutput = (PiecewiseOutput *)PyMem_Malloc(sizeof(PiecewiseOutput));
  newOutput->base.type = PIECEWISE_LINEAR;
  newOutput->base.out_function = (OutputFunction)PiecewiseLinear_function;
  newOutput->base.out_dealloc = (destructor)Piecewise_dealloc;
  newOutput->tvalues = tvalues;
  newOutput->fvalues = fvalues;

  return (ActivityOutput *)newOutput;
}

static ActivityOutput *Activity_CubicSplineOutput(PyObject *tvalues,
                                                  PyObject *fvalues) {
  int n, r;
  CubicSplineOutput *newOutput;

  // check tvalues fvalues
  if (!tvalues) {
    PyErr_SetString(
        PyExc_ValueError,
        "No t-values given, please specify t-values using the 't' argument");
    return NULL;
  }
  if (!fvalues) {
    PyErr_SetString(
        PyExc_ValueError,
        "No f-values given, please specify f-values using the 'f' argument");
    return NULL;
  }

  tvalues = PyArray_FROM_OTF(tvalues, NPY_DOUBLE,
                             NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!tvalues) {
    PyErr_SetString(PyExc_ValueError,
                    "Cannot convert 'tvalues' to numpy array.");
    return NULL;
  }
  fvalues = PyArray_FROM_OTF(fvalues, NPY_DOUBLE,
                             NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!fvalues) {
    Py_DECREF(tvalues);
    PyErr_SetString(PyExc_ValueError,
                    "Cannot convert 'fvalues' to numpy array.");
    return NULL;
  }

  if (PYSIZE(tvalues) < 2 || PYSIZE(tvalues) != PYSIZE(fvalues)) {
    Py_DECREF(tvalues);
    Py_DECREF(fvalues);
    PyErr_SetString(PyExc_ValueError, "Incorrect number of t and f values.");
    return NULL;
  }

  n = PYSIZE(tvalues);
  newOutput = (CubicSplineOutput *)PyMem_Malloc(sizeof(CubicSplineOutput));
  newOutput->base.type = CUBIC_SPLINE;
  newOutput->base.out_function = (OutputFunction)CubicInterpolate_function;
  newOutput->base.out_dealloc = (destructor)CubicInterpolate_dealloc;
  newOutput->tvalues = tvalues;
  newOutput->fvalues = fvalues;
  newOutput->b = (double *)PyMem_Malloc(n * sizeof(double));
  newOutput->c = (double *)PyMem_Malloc(n * sizeof(double));
  newOutput->d = (double *)PyMem_Malloc(n * sizeof(double));
  newOutput->last = 0;

  r = cubicCalcCoef(n, 0, 0, 0, PYDATA(tvalues), PYDATA(fvalues), newOutput->b,
                    newOutput->c, newOutput->d);

  if (r < 0)
    return NULL;
  return (ActivityOutput *)newOutput;
}

static ActivityOutput *Activity_StateManipulationOutput(PyObject *tvalues,
                                                        PyObject *fvalues,
                                                        int mode) {
  ActivityStateManipulation *newOutput;

  // check tvalues fvalues
  if (!tvalues) {
    PyErr_SetString(
        PyExc_ValueError,
        "No t-values given, please specify t-values using the 't' argument");
    return NULL;
  }
  if (!fvalues) {
    PyErr_SetString(
        PyExc_ValueError,
        "No f-values given, please specify f-values using the 'f' argument");
    return NULL;
  }

  tvalues = PyArray_FROM_OTF(tvalues, NPY_DOUBLE,
                             NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!tvalues) {
    PyErr_SetString(PyExc_ValueError, "Cannot convert tvalues to numpy array");
    return NULL;
  }
  fvalues = PyArray_FROM_OTF(fvalues, NPY_DOUBLE,
                             NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!fvalues) {
    Py_DECREF(tvalues);
    PyErr_SetString(PyExc_ValueError, "Cannot convert fvalues to numpy array");
    return NULL;
  }

  // For state manipulations: len(t) must equal len(f)
  if (PYSIZE(tvalues) != PYSIZE(fvalues)) {
    Py_DECREF(tvalues);
    Py_DECREF(fvalues);
    PyErr_SetString(
        PyExc_ValueError,
        "For state assignment, t and f must have the same number of elements.");
    return NULL;
  }

  if (PYSIZE(tvalues) < 1) {
    Py_DECREF(tvalues);
    Py_DECREF(fvalues);
    PyErr_SetString(PyExc_ValueError,
                    "State assignment require at least one time-value pair");
    return NULL;
  }

  newOutput = (ActivityStateManipulation *)PyMem_Malloc(
      sizeof(ActivityStateManipulation));
  newOutput->base.type = STATE_MANIPULATION;
  newOutput->base.out_function = (OutputFunction)StateManipulation_function;
  newOutput->base.out_dealloc = (destructor)StateManipulation_dealloc;
  newOutput->base.isFeature = 0;
  newOutput->base.output = 0.0;
  newOutput->tvalues = tvalues;
  newOutput->fvalues = fvalues;
  newOutput->mode = mode;

  return (ActivityOutput *)newOutput;
}

PyObject *ACTIVITY::getOutputs(ActivityObject *self, PyObject *args,
                               PyObject *kwds) {
  int k;
  npy_intp dims[2];
  double *times, *outputdata;
  static char *kwlist[] = {const_cast<char *>("time_vector"), NULL};
  PyObject *time_vector{};
  PyObject *ret{};

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|$O", kwlist, &time_vector)) {
    return NULL;
  }

  if (time_vector == nullptr) {
    PyErr_SetString(PyExc_SyntaxError, "Missing 'time_vector' argument!");
    return nullptr;
  }

  PyObject *timeVector = PyArray_FROM_OTF(
      time_vector, NPY_DOUBLE, NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!timeVector) {
    PyErr_SetString(PyExc_TypeError,
                    "Could not convert 'time_vector' to numpy array");
    return NULL;
  }

  times = PYDATA(timeVector);
  int nOutputs = self->nroutputs;
  outputdata = (double *)malloc(nOutputs * PYSIZE(timeVector) * sizeof(double));
  // Temporary buffer for outputs only
  double *tmpOut = (double *)malloc(nOutputs * sizeof(double));
  for (k = 0; k < PYSIZE(timeVector); k++) {
    outputFeature((PyObject *)self, times[k], tmpOut, NULL, -1);
    if (nOutputs > 0) {
      memcpy(&outputdata[k * nOutputs], tmpOut, nOutputs * sizeof(double));
    }
  }
  free(tmpOut);

  dims[0] = PYSIZE(timeVector);
  dims[1] = self->nroutputs;
  ret = PyArray_SimpleNewFromData(2, dims, NPY_DOUBLE, (void *)outputdata);
  PyArray_ENABLEFLAGS((PyArrayObject *)ret, NPY_ARRAY_OWNDATA);

  Py_DECREF(timeVector);

  return ret;
}

PyObject *ACTIVITY::getManipulations(ActivityObject *self, PyObject *args,
                                     PyObject *kwds) {
  int k;
  npy_intp dims[2];
  double *times, *manipulationdata;
  static char *kwlist[] = {const_cast<char *>("time_vector"), NULL};
  PyObject *time_vector{};
  PyObject *ret{};

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|$O", kwlist, &time_vector)) {
    return NULL;
  }

  if (time_vector == nullptr) {
    PyErr_SetString(PyExc_SyntaxError, "Missing 'time_vector' argument!");
    return nullptr;
  }

  PyObject *timeVector = PyArray_FROM_OTF(
      time_vector, NPY_DOUBLE, NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!timeVector) {
    PyErr_SetString(PyExc_TypeError,
                    "Could not convert 'time_vector' to numpy array");
    return NULL;
  }

  times = PYDATA(timeVector);

  // Get only manipulations - use separate manipulation count
  int nrManipulations = PyList_Size(self->manipulationNames);
  manipulationdata =
      (double *)malloc(nrManipulations * PYSIZE(timeVector) * sizeof(double));

  // Compute manipulations directly
  double *tmpManip = (double *)malloc(nrManipulations * sizeof(double));
  for (k = 0; k < PYSIZE(timeVector); k++) {
    manipulationValues((PyObject *)self, times[k], tmpManip);
    if (nrManipulations > 0) {
      memcpy(&manipulationdata[k * nrManipulations], tmpManip,
             nrManipulations * sizeof(double));
    }
  }
  free(tmpManip);

  dims[0] = PYSIZE(timeVector);
  dims[1] = nrManipulations;
  ret =
      PyArray_SimpleNewFromData(2, dims, NPY_DOUBLE, (void *)manipulationdata);
  PyArray_ENABLEFLAGS((PyArrayObject *)ret, NPY_ARRAY_OWNDATA);

  Py_DECREF(timeVector);

  return ret;
}

PyObject *ACTIVITY::factory(PyObject *cls, PyObject *args, PyObject *kwargs) {
  // This function is used by __reduce__ to reconstruct Activity objects
  PyObject *constructor_kwargs;
  if (!PyArg_ParseTuple(args, "O", &constructor_kwargs)) {
    return NULL;
  }

  if (!PyDict_Check(constructor_kwargs)) {
    PyErr_SetString(PyExc_TypeError,
                    "Expected dictionary for constructor kwargs");
    return NULL;
  }

  // Create a new Activity with the provided kwargs, then __setstate__ will
  // restore the outputs
  return PyObject_Call(cls, PyTuple_New(0), constructor_kwargs);
}

PyObject *ACTIVITY::reduce(ActivityObject *self) {
  // Initialize featureIndex to avoid maybe-uninitialized warning from some
  // compilers
  int featureIndex = 0, stateIndex;
  PyObject *ret, *args, *state, *kwds, *tmp;
  ActivityOutput *AO;
  ConstantOutput *CO;
  PiecewiseOutput *PO;
  CubicSplineOutput *SO;
  ActivityStateManipulation *SM;

  int nrManipulations = PyList_Size(self->manipulationNames);
  state = PyList_New(self->nroutputs + nrManipulations);
  int outPos = 0;

  // Outputs
  for (int outputIndex = 0; outputIndex < self->nroutputs; outputIndex++) {
    kwds = PyDict_New();
    AO = self->outputs[outputIndex];
    const char *type_str = getStringFromType(AO->type);
    tmp = PyUnicode_FromString(type_str);
    PyDict_SetItemString(kwds, "type", tmp);
    Py_DECREF(tmp);

    PyObject *output_name = PyList_GetItem(self->outputNames, outputIndex);
    PyDict_SetItemString(kwds, "name", output_name);

    if (AO->isFeature) {
      PyDict_SetItemString(kwds, "feature", Py_True);
      tmp = PyList_GetItem(self->featureUnits, featureIndex);
      PyDict_SetItemString(kwds, "unit", tmp);
      featureIndex++;
    } else {
      PyDict_SetItemString(kwds, "feature", Py_False);
      PyDict_SetItemString(kwds, "unit", Py_None);
    }
    switch (AO->type) {
    case CONSTANT:
      CO = (ConstantOutput *)AO;
      PyDict_SetItemString(kwds, "t", Py_None);
      tmp = PyFloat_FromDouble(CO->constant);
      PyDict_SetItemString(kwds, "f", tmp);
      Py_DECREF(tmp);
      break;
    case PIECEWISE_CONSTANT:
    case PIECEWISE_LINEAR:
      PO = (PiecewiseOutput *)AO;
      PyDict_SetItemString(kwds, "t", PO->tvalues);
      PyDict_SetItemString(kwds, "f", PO->fvalues);
      break;
    case CUBIC_SPLINE:
      SO = (CubicSplineOutput *)AO;
      PyDict_SetItemString(kwds, "t", SO->tvalues);
      PyDict_SetItemString(kwds, "f", SO->fvalues);
      break;
    }
    PyList_SetItem(state, outPos++, kwds);
  }

  // Manipulations
  for (stateIndex = 0; stateIndex < PyList_Size(self->manipulationNames);
       stateIndex++) {
    kwds = PyDict_New();
    SM = self->stateManipulations[stateIndex];
    tmp = PyUnicode_FromString("state_manipulation");
    PyDict_SetItemString(kwds, "type", tmp);
    Py_DECREF(tmp);
    PyObject *name_obj = PyList_GetItem(self->manipulationNames, stateIndex);
    PyDict_SetItemString(kwds, "name", name_obj);
    PyDict_SetItemString(kwds, "t", SM->tvalues);
    PyDict_SetItemString(kwds, "f", SM->fvalues);
    PyList_SetItem(state, outPos++, kwds);
  }

  // Create kwargs for constructor (time_unit and container keyword-only)
  PyObject *kwargs = PyDict_New();
  PyDict_SetItemString(kwargs, "time_unit", self->timeUnit);
  // Emit new canonical 'container' key for pickle protocol moving forward.
  // If an older pickle contained 'compartment', __init__ still accepts it (with
  // deprecation warning).
  if (self->compartment && self->compartment != Py_None) {
    PyDict_SetItemString(kwargs, "container", self->compartment);
  }

  // Get the factory method from the class
  PyObject *factory_func =
      PyObject_GetAttrString((PyObject *)Py_TYPE(self), "_factory");
  if (!factory_func) {
    Py_DECREF(kwargs);
    Py_DECREF(state);
    return NULL;
  }

  // Create args tuple containing the kwargs
  args = PyTuple_New(1);
  PyTuple_SetItem(args, 0, kwargs);

  ret = Py_BuildValue("(OOO)", factory_func, args, state);
  Py_DECREF(args);
  Py_DECREF(state);
  Py_DECREF(factory_func);
  return ret;
}

PyObject *ACTIVITY::setState(ActivityObject *self, PyObject *stateTuple) {
  int k, l;
  PyObject *kwds, *state, *tmp, *args;

  // Required keys for outputs only (manipulations handled separately above)
  char *keys[] = {const_cast<char *>("type"),
                  const_cast<char *>("name"),
                  const_cast<char *>("t"),
                  const_cast<char *>("f"),
                  const_cast<char *>("unit"),
                  const_cast<char *>("feature"),
                  NULL};

  if (!PyArg_Parse(stateTuple, "(O,)", &state))
    return NULL;

  if (!PyList_Check(state)) {
    PyErr_SetString(PyExc_TypeError, "State needs to be a list type");
    return NULL;
  }

  // Add outputs
  args = PyTuple_New(0);
  for (k = 0; k < PyList_Size(state); k++) {
    kwds = PyList_GetItem(state, k);
    if (!PyDict_Check(kwds)) {
      PyErr_SetString(PyExc_TypeError,
                      "State needs to be a list of keyword argument");
      return NULL;
    }

    // Check if this is a state manipulation by looking at the type
    PyObject *type_obj = PyDict_GetItemString(kwds, "type");
    if (type_obj && PyUnicode_Check(type_obj)) {
      const char *type_str = PyUnicode_AsUTF8(type_obj);
      if (type_str && strcmp(type_str, "state_manipulation") == 0) {
        // This is a state manipulation - handle differently
        PyObject *name = PyDict_GetItemString(kwds, "name");
        PyObject *t = PyDict_GetItemString(kwds, "t");
        PyObject *f = PyDict_GetItemString(kwds, "f");

        if (!name || !t || !f) {
          PyErr_SetString(
              PyExc_ValueError,
              "State manipulation missing required parameters: name, t, f");
          Py_DECREF(args);
          return NULL;
        }

        // Create keyword arguments for add_state_manipulation
        PyObject *state_kwds = PyDict_New();
        if (!state_kwds) {
          Py_DECREF(args);
          return NULL;
        }

        PyObject *set_mode = PyUnicode_FromString("set");
        PyDict_SetItemString(state_kwds, "mode", set_mode);
        Py_DECREF(set_mode);
        PyDict_SetItemString(state_kwds, "name", name);
        PyDict_SetItemString(state_kwds, "t", t);
        PyDict_SetItemString(state_kwds, "f", f);

        // Call add_state_manipulation
        PyObject *result =
            ACTIVITY::add_state_manipulation(self, args, state_kwds);
        Py_DECREF(state_kwds);

        if (!result) {
          Py_DECREF(args);
          return NULL;
        }
        Py_DECREF(result);
        continue;
      }
    }

    // Validate required keys exist and remove Py_None for those
    l = 0;
    while (keys[l]) {
      tmp = PyDict_GetItemString(kwds, keys[l]);
      if (!tmp) {
        PyErr_SetObject(PyExc_TypeError,
                        PyUnicode_FromFormat(
                            "Keyword '%s' missing in state list", keys[l]));
        return NULL;
      }
      if (tmp == Py_None)
        PyDict_DelItemString(kwds, keys[l]);
      l++;
    }

    // Check if the name already has compartment prefix and remove it
    // This prevents double prefixing during state restoration
    PyObject *name_obj = PyDict_GetItemString(kwds, "name");
    if (name_obj && self->compartment != Py_None && PyUnicode_Check(name_obj) &&
        PyUnicode_Check(self->compartment)) {
      const char *name_str = PyUnicode_AsUTF8(name_obj);
      const char *compartment_str = PyUnicode_AsUTF8(self->compartment);

      if (name_str && compartment_str) {
        // Check if name starts with "compartment:"
        size_t compartment_len = strlen(compartment_str);
        if (strncmp(name_str, compartment_str, compartment_len) == 0 &&
            name_str[compartment_len] == ':') {
          // Strip the compartment prefix
          PyObject *stripped_name =
              PyUnicode_FromString(name_str + compartment_len + 1);
          if (stripped_name) {
            PyDict_SetItemString(kwds, "name", stripped_name);
            Py_DECREF(stripped_name);
          }
        }
      }
    }

    ACTIVITY::addOutput(self, args, kwds);
  }
  Py_DECREF(args);

  Py_RETURN_NONE;
}

PyObject *ACTIVITY::add_state_manipulation(ActivityObject *self, PyObject *args,
                                           PyObject *kwds) {
  static char *kwlist[] = {const_cast<char *>("mode"),
                           const_cast<char *>("name"), const_cast<char *>("t"),
                           const_cast<char *>("f"), NULL};

  PyObject *mode{};
  PyObject *name{};
  PyObject *t{};
  PyObject *f{};

  if (!self->editable) {
    PyErr_SetString(PyExc_RuntimeError,
                    "The activity object is not editable since it has been "
                    "added to a simulation object.");
    return NULL;
  }

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|$OOOO", kwlist, &mode, &name,
                                   &t, &f)) {
    return NULL;
  }
  // Validate required arguments
  if (!mode) {
    PyErr_SetString(PyExc_TypeError, "The 'mode' argument is required");
    return NULL;
  }
  if (!name) {
    PyErr_SetString(PyExc_TypeError, "The 'name' argument is required");
    return NULL;
  }

  if (!PyUnicode_Check(mode)) {
    PyErr_SetString(PyExc_TypeError, "The 'mode' argument must be a string");
    return NULL;
  }
  if (!PyUnicode_Check(name)) {
    PyErr_SetString(PyExc_TypeError, "The 'name' argument must be a string");
    return NULL;
  }

  if (!t && !f) {
    PyErr_SetString(PyExc_ValueError,
                    "State assignment requires both 't' and 'f' values.");
    return NULL;
  } else if (!t) {
    PyErr_SetString(PyExc_ValueError, "State assignment requires 't' values.");
    return NULL;
  } else if (!f) {
    PyErr_SetString(PyExc_ValueError, "State assignment requires 'f' values.");
    return NULL;
  }

  // Validate mode is either "set" or "add"
  const char *mode_str = PyUnicode_AsUTF8(mode);
  if (!mode_str) {
    return NULL;
  }

  bool is_set_mode = strcmp(mode_str, "set") == 0;
  bool is_add_mode = strcmp(mode_str, "add") == 0;

  if (!is_set_mode && !is_add_mode) {
    PyErr_SetString(PyExc_ValueError, "Mode must be either 'set' or 'add'");
    return NULL;
  }

  // Create state manipulation using dedicated function (returns ActivityOutput*
  // for compatibility)
  int mode_int = is_set_mode ? 0 : 1; // 0 = set, 1 = add
  ActivityOutput *tempOutput = Activity_StateManipulationOutput(t, f, mode_int);

  if (!tempOutput)
    return NULL;

  // Cast to the actual independent structure
  ActivityStateManipulation *stateManipulation =
      (ActivityStateManipulation *)tempOutput;

  // Add manipulation name directly
  PyObject *manipulation_name;
  if (self->compartment != Py_None)
    manipulation_name = PyUnicode_FromFormat("%S:%S", self->compartment, name);
  else {
    manipulation_name = name;
    Py_INCREF(manipulation_name);
  }

  // Remove existing manipulation for this name if present
  int nrStateManipulations = PyList_Size(self->manipulationNames);
  for (int i = 0; i < nrStateManipulations; i++) {
    PyObject *existing_name = PyList_GetItem(self->manipulationNames, i);
    if (PyUnicode_Compare(existing_name, manipulation_name) == 0) {
      PyObject *remove_args = Py_BuildValue("(O)", manipulation_name);
      PyObject *remove_result =
          ACTIVITY::removeManipulations(self, remove_args, NULL);
      Py_XDECREF(remove_args);
      Py_XDECREF(remove_result);
      break;
    }
  }

  // Add to manipulationNames for separate tracking
  PyList_Append(self->manipulationNames, manipulation_name);

  // Store ONLY in separate state manipulations array
  nrStateManipulations = PyList_Size(self->manipulationNames);
  self->stateManipulations = (ActivityStateManipulation **)PyMem_Realloc(
      self->stateManipulations,
      nrStateManipulations * sizeof(ActivityStateManipulation *));
  self->stateManipulations[nrStateManipulations - 1] = stateManipulation;

  Py_DECREF(manipulation_name);
  Py_RETURN_NONE;
}

PyObject *ACTIVITY::removeOutputs(ActivityObject *self, PyObject *args,
                                  PyObject *kwds) {
  static char *kwlist[] = {const_cast<char *>("names"), NULL};

  PyObject *names = nullptr;

  if (!self->editable) {
    PyErr_SetString(PyExc_RuntimeError,
                    "The activity object is not editable since it has been "
                    "added to a simulation object.");
    return NULL;
  }

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &names))
    return NULL;

  // Determine which parameter was provided
  PyObject *target_names = nullptr;
  if (names) {
    target_names = names;
  } else {
    PyErr_SetString(PyExc_TypeError, "Must specify 'names' parameter");
    return NULL;
  }

  // Handle both single string and list of strings
  PyObject *names_list = nullptr;

  if (PyUnicode_Check(target_names)) {
    // Single string - create a list with one element
    names_list = PyList_New(1);
    if (!names_list) {
      return NULL;
    }
    Py_INCREF(target_names);
    PyList_SetItem(names_list, 0, target_names);
  } else if (PyList_Check(target_names)) {
    // Already a list
    names_list = target_names;
    Py_INCREF(names_list);
  } else {
    PyErr_SetString(PyExc_TypeError,
                    "The names argument must be a string or a list of strings");
    return NULL;
  }

  // Validate all names are strings
  Py_ssize_t list_size = PyList_Size(names_list);
  for (Py_ssize_t i = 0; i < list_size; i++) {
    PyObject *name_item = PyList_GetItem(names_list, i);
    if (!PyUnicode_Check(name_item)) {
      Py_DECREF(names_list);
      PyErr_SetString(PyExc_TypeError, "All names must be strings");
      return NULL;
    }
  }

  // Collect indices of outputs to remove (in reverse order to avoid index
  // shifting issues)
  PyObject *indices_to_remove = PyList_New(0);
  if (!indices_to_remove) {
    Py_DECREF(names_list);
    return NULL;
  }

  for (Py_ssize_t i = 0; i < list_size; i++) {
    PyObject *name_item = PyList_GetItem(names_list, i);
    int index = -1;

    // Find the output with the given name among outputs only
    for (int j = 0; j < self->nroutputs; j++) {
      PyObject *existing_name = PyList_GetItem(self->outputNames, j);
      if (PyUnicode_Compare(name_item, existing_name) == 0) {
        index = j;
        break;
      }
    }

    if (index == -1) {
      Py_DECREF(names_list);
      Py_DECREF(indices_to_remove);
      PyErr_Format(PyExc_ValueError, "No output found with name '%S'",
                   name_item);
      return NULL;
    }

    // Add index to removal list
    PyObject *index_obj = PyLong_FromLong(index);
    if (!index_obj) {
      Py_DECREF(names_list);
      Py_DECREF(indices_to_remove);
      return NULL;
    }
    PyList_Append(indices_to_remove, index_obj);
    Py_DECREF(index_obj);
  }

  // Sort indices in descending order to remove from back to front
  PyList_Sort(indices_to_remove);
  PyList_Reverse(indices_to_remove);

  // Remove outputs
  Py_ssize_t removal_count = PyList_Size(indices_to_remove);
  for (Py_ssize_t i = 0; i < removal_count; i++) {
    PyObject *index_obj = PyList_GetItem(indices_to_remove, i);
    int index = PyLong_AsLong(index_obj);
    {
      if (index < self->nroutputs) {
        // Clean up the output
        ActivityOutput *output = self->outputs[index];
        output->out_dealloc((PyObject *)output);

        // If this was also a feature, remove it from features
        if (output->isFeature) {
          // Find and remove from features array
          int feature_index = -1;
          for (int j = 0; j < self->nrfeatures; j++) {
            if (self->features[j] == output) {
              feature_index = j;
              break;
            }
          }

          if (feature_index != -1) {
            // Remove from feature arrays
            PySequence_DelItem(self->featureNames, feature_index);
            PySequence_DelItem(self->featureUnits, feature_index);

            // Shift remaining features
            for (int j = feature_index; j < self->nrfeatures - 1; j++) {
              self->features[j] = self->features[j + 1];
            }
            self->nrfeatures--;
            if (self->nrfeatures > 0) {
              self->features = (ActivityOutput **)PyMem_Realloc(
                  self->features, self->nrfeatures * sizeof(ActivityOutput *));
            } else {
              PyMem_Free(self->features);
              self->features = NULL;
            }
          }
        }

        // Shift remaining outputs
        for (int j = index; j < self->nroutputs - 1; j++) {
          self->outputs[j] = self->outputs[j + 1];
        }

        self->nroutputs--;

        if (self->nroutputs > 0) {
          self->outputs = (ActivityOutput **)PyMem_Realloc(
              self->outputs, self->nroutputs * sizeof(ActivityOutput *));
        } else {
          PyMem_Free(self->outputs);
          self->outputs = NULL;
        }
      }
    }

    // Remove from outputNames (updates the outputs list count)
    PySequence_DelItem(self->outputNames, index);
    /* total outputs equals nroutputs */
  }

  Py_DECREF(names_list);
  Py_DECREF(indices_to_remove);

  Py_RETURN_NONE;
}

PyObject *ACTIVITY::removeManipulations(ActivityObject *self, PyObject *args,
                                        PyObject *kwds) {
  static char *kwlist[] = {const_cast<char *>("names"), NULL};

  PyObject *names = nullptr;

  if (!self->editable) {
    PyErr_SetString(PyExc_RuntimeError,
                    "The activity object is not editable since it has been "
                    "added to a simulation object.");
    return NULL;
  }

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &names))
    return NULL;

  // Determine which parameter was provided
  PyObject *target_names = nullptr;
  if (names) {
    target_names = names;
  } else {
    PyErr_SetString(PyExc_TypeError, "Must specify 'names' parameter");
    return NULL;
  }

  // Handle both single string and list of strings
  PyObject *names_list = nullptr;

  if (PyUnicode_Check(target_names)) {
    // Single string - create a list with one element
    names_list = PyList_New(1);
    if (!names_list) {
      return NULL;
    }
    Py_INCREF(target_names);
    PyList_SetItem(names_list, 0, target_names);
  } else if (PyList_Check(target_names)) {
    // Already a list
    names_list = target_names;
    Py_INCREF(names_list);
  } else {
    PyErr_SetString(PyExc_TypeError,
                    "The names argument must be a string or a list of strings");
    return NULL;
  }

  // Validate all names are strings
  Py_ssize_t list_size = PyList_Size(names_list);
  for (Py_ssize_t i = 0; i < list_size; i++) {
    PyObject *name_item = PyList_GetItem(names_list, i);
    if (!PyUnicode_Check(name_item)) {
      Py_DECREF(names_list);
      PyErr_SetString(PyExc_TypeError, "All names must be strings");
      return NULL;
    }
  }

  // Collect indices of manipulations to remove (in reverse order to avoid index
  // shifting issues)
  PyObject *indices_to_remove = PyList_New(0);
  if (!indices_to_remove) {
    Py_DECREF(names_list);
    return NULL;
  }

  for (Py_ssize_t i = 0; i < list_size; i++) {
    PyObject *name_item = PyList_GetItem(names_list, i);
    int stateIndex = -1;

    // Build an alternative name with compartment prefix if needed
    PyObject *alt_with_compartment = NULL;
    if (self->compartment != Py_None) {
      const char *name_c = PyUnicode_AsUTF8(name_item);
      if (name_c) {
        // Only create prefixed variant if not already namespaced
        if (strchr(name_c, ':') == NULL) {
          alt_with_compartment =
              PyUnicode_FromFormat("%S:%s", self->compartment, name_c);
        }
      }
    }

    // Find the manipulation with the given name in manipulationNames
    int nrStateManipulations = PyList_Size(self->manipulationNames);
    for (int j = 0; j < nrStateManipulations; j++) {
      PyObject *existing_name = PyList_GetItem(self->manipulationNames, j);
      if (PyUnicode_Compare(name_item, existing_name) == 0 ||
          (alt_with_compartment &&
           PyUnicode_Compare(alt_with_compartment, existing_name) == 0)) {
        stateIndex = j;
        break;
      }
    }

    Py_XDECREF(alt_with_compartment);

    if (stateIndex == -1) {
      Py_DECREF(names_list);
      Py_DECREF(indices_to_remove);
      PyErr_Format(PyExc_ValueError, "No manipulation found with name '%S'",
                   name_item);
      return NULL;
    }

    // Add index to removal list
    PyObject *index_obj = PyLong_FromLong(stateIndex);
    if (!index_obj) {
      Py_DECREF(names_list);
      Py_DECREF(indices_to_remove);
      return NULL;
    }
    PyList_Append(indices_to_remove, index_obj);
    Py_DECREF(index_obj);
  }

  // Sort indices in descending order to remove from back to front
  PyList_Sort(indices_to_remove);
  PyList_Reverse(indices_to_remove);

  // Remove manipulations (only state manipulations)
  Py_ssize_t removal_count = PyList_Size(indices_to_remove);
  for (Py_ssize_t i = 0; i < removal_count; i++) {
    PyObject *index_obj = PyList_GetItem(indices_to_remove, i);
    int stateIndex = PyLong_AsLong(index_obj);

    int nrStateManipulations = PyList_Size(self->manipulationNames);
    if (stateIndex < nrStateManipulations) {
      // Clean up the state manipulation
      ActivityStateManipulation *stateManip =
          self->stateManipulations[stateIndex];
      stateManip->base.out_dealloc((PyObject *)stateManip);

      // Shift remaining state manipulations
      for (int j = stateIndex; j < nrStateManipulations - 1; j++) {
        self->stateManipulations[j] = self->stateManipulations[j + 1];
      }
      nrStateManipulations--;
      if (nrStateManipulations > 0) {
        self->stateManipulations = (ActivityStateManipulation **)PyMem_Realloc(
            self->stateManipulations,
            nrStateManipulations * sizeof(ActivityStateManipulation *));
      } else {
        PyMem_Free(self->stateManipulations);
        self->stateManipulations = NULL;
      }

      // Remove from manipulationNames list
      PySequence_DelItem(self->manipulationNames, stateIndex);

      // No total counter to decrement
    }
  }

  Py_DECREF(names_list);
  Py_DECREF(indices_to_remove);

  Py_RETURN_NONE;
}

/*
==========================================================================================
ActivityType definition
==========================================================================================
*/

static int Activity_init(ActivityObject *self, PyObject *args, PyObject *kwds) {
  // Initialize all fields first to ensure safe deallocation if constructor
  // fails
  self->nroutputs = 0;
  self->nrfeatures = 0;
  self->editable = 1;
  self->outputNames = NULL;
  self->manipulationNames = NULL;
  self->featureNames = NULL;
  self->featureUnits = NULL;
  self->outputs = NULL;
  self->features = NULL;
  self->stateManipulations = NULL;
  self->timeUnit = NULL;
  self->compartment = NULL;

  static char *kwlist[] = {const_cast<char *>("time_unit"),
                           const_cast<char *>("container"),
                           const_cast<char *>("compartment"), /* deprecated */
                           NULL};
  PyObject *time_unit{};
  PyObject *container{};
  PyObject *compartment{}; // deprecated

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|$OOO", kwlist, &time_unit,
                                   &container, &compartment))
    return -1;

  if (time_unit == nullptr) {
    PyErr_SetString(PyExc_ValueError, "The 'time_unit' argument must be set!");
    return -1;
  }

  if (!PyUnicode_Check(time_unit)) {
    PyErr_SetString(PyExc_TypeError,
                    "The time_unit argument has to be a string!");
    return -1;
  } else {
    // Normalize Greek mu (U+03BC, 'μ') to micro sign (U+00B5, 'µ') so both are
    // accepted
    PyObject *normalized = time_unit; // borrowed
    const char *tu = PyUnicode_AsUTF8(time_unit);
    if (tu != nullptr && std::strcmp(tu, "μs") == 0) {
      normalized = PyUnicode_FromString("µs"); // new ref
      if (!normalized) {
        return -1;
      }
      // Assign new object without INCREF since it's already a new reference
      self->timeUnit = normalized;
    } else {
      // Keep the provided object and INCREF since it's a borrowed reference
      Py_INCREF(normalized);
      self->timeUnit = normalized;
    }
  }

  // Mutual exclusivity: cannot provide both canonical 'container' and
  // deprecated 'compartment'
  if (container && container != Py_None && compartment &&
      compartment != Py_None) {
    PyErr_SetString(PyExc_TypeError,
                    "Cannot specify both 'container' and deprecated "
                    "'compartment'; use only 'container'.");
    return -1;
  }
  PyObject *selected = NULL;
  if (container && container != Py_None)
    selected = container;
  else if (compartment && compartment != Py_None)
    selected = compartment;
  if (!selected) {
    Py_INCREF(Py_None);
    self->compartment = Py_None;
  } else {
    if (!PyUnicode_Check(selected)) {
      PyErr_SetString(PyExc_TypeError, "The container has to be a string");
      return -1;
    }
    if (selected == compartment) {
      // Emit a proper DeprecationWarning (stacklevel=2 so user code line is
      // shown)
      if (PyErr_WarnEx(PyExc_DeprecationWarning,
                       "The 'compartment' argument is deprecated; use "
                       "'container' instead. In the future, 'compartment' will "
                       "refer to volume dependent compartments.",
                       1) < 0) {
        return NULL; // Propagate error if warning turned into exception
      }
    }
    Py_INCREF(selected);
    self->compartment = selected;
  }

  // Initialize the StringList objects after all error checking is done
  self->outputNames = StringList_New(0, 0);
  self->manipulationNames = StringList_New(0, 0);
  self->featureNames = StringList_New(0, 0);
  self->featureUnits = StringList_New(0, 0);
  return 0;
}

static void Constant_dealloc(ConstantOutput *self) { PyMem_Free(self); }

static void Piecewise_dealloc(PiecewiseOutput *self) {
  Py_XDECREF(self->tvalues);
  Py_XDECREF(self->fvalues);
  PyMem_Free(self);
}

static void CubicInterpolate_dealloc(CubicSplineOutput *self) {
  Py_XDECREF(self->tvalues);
  Py_XDECREF(self->fvalues);
  PyMem_Free(self->b);
  PyMem_Free(self->c);
  PyMem_Free(self->d);
  PyMem_Free(self);
}

static void StateManipulation_dealloc(ActivityStateManipulation *self) {
  Py_XDECREF(self->tvalues);
  Py_XDECREF(self->fvalues);
  PyMem_Free(self);
}

static void Activity_dealloc(ActivityObject *self) {
  int k;
  Py_XDECREF(self->outputNames);
  Py_XDECREF(self->manipulationNames);
  Py_XDECREF(self->featureNames);
  Py_XDECREF(self->featureUnits);
  Py_XDECREF(self->timeUnit);
  Py_XDECREF(self->compartment);

  // Only deallocate outputs if they exist
  if (self->outputs) {
    for (k = 0; k < self->nroutputs; k++) {
      if (self->outputs[k]) {
        self->outputs[k]->out_dealloc((PyObject *)self->outputs[k]);
      }
    }
    PyMem_Free(self->outputs);
  }

  // Only deallocate state manipulations if they exist
  if (self->stateManipulations && self->manipulationNames) {
    int nrStateManipulations = PyList_Size(self->manipulationNames);
    for (k = 0; k < nrStateManipulations; k++) {
      if (self->stateManipulations[k]) {
        self->stateManipulations[k]->base.out_dealloc(
            (PyObject *)self->stateManipulations[k]);
      }
    }
    PyMem_Free(self->stateManipulations);
  }

  if (self->features) {
    PyMem_Free(self->features);
  }

  Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyTypeObject ActivityType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
        "sund._Activity.Activity",
    .tp_basicsize = sizeof(ActivityObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)Activity_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "Activity object",
    .tp_methods = Activity_methods,
    .tp_getset = Activity_getsetters,
    .tp_init = (initproc)Activity_init,
    .tp_new = PyType_GenericNew,
};

/*
==========================================================================================
C_API FUNCTIONS
==========================================================================================
*/
void outputFeature(PyObject *tmp, double time, double *outputvector,
                   double *featurevector, int DOflag) {
  ActivityObject *self;
  int k;

  self = (ActivityObject *)tmp;

  // Fill outputs only (manipulations are separate)
  for (k = 0; k < self->nroutputs; k++) {
    ActivityOutput *output = self->outputs[k];
    output->output = output->out_function(output, time);
    outputvector[k] = output->output;
  }
  // check flag
  if (DOflag == DOFLAG_FEATURE) {
    for (k = 0; k < self->nrfeatures; k++) {
      featurevector[k] = self->features[k]->output;
    }
  }
}

void manipulationValues(PyObject *tmp, double time, double *manipvector) {
  ActivityObject *self = (ActivityObject *)tmp;
  int nrStateManipulations = PyList_Size(self->manipulationNames);
  for (int k = 0; k < nrStateManipulations; k++) {
    ActivityStateManipulation *sm = self->stateManipulations[k];
    manipvector[k] = sm->base.out_function(sm, time);
  }
}

int nrOutputs(PyObject *tmp) {
  ActivityObject *self;

  self = (ActivityObject *)tmp;
  return self->nroutputs;
}

int nrFeatures(PyObject *tmp) {
  ActivityObject *self;

  self = (ActivityObject *)tmp;
  return self->nrfeatures;
}

PyObject *outputNames(PyObject *tmp) {
  return ((ActivityObject *)tmp)->outputNames;
}

PyObject *manipulationNames(PyObject *tmp) {
  return ((ActivityObject *)tmp)->manipulationNames;
}

PyObject *featureNames(PyObject *tmp) {
  return ((ActivityObject *)tmp)->featureNames;
}

PyObject *featureUnits(PyObject *tmp) {
  return ((ActivityObject *)tmp)->featureUnits;
}

bool isActivity(PyObject *obj) {
  if (Py_TYPE(obj) == &ActivityType) {
    return true;
  } else {
    return false;
  }
}

PyObject *timeUnit(PyObject *obj) { return ((ActivityObject *)obj)->timeUnit; }

void setNonEditable(PyObject *obj) { ((ActivityObject *)obj)->editable = 0; }

/*
 * Returns a PyArrayObject with the tvalues of the activity output with the
 * given index. Returns NULL if there are no tvalues to return or there is an
 * error with the input, along with a Python exception. obj is a PyObject* to
 * the ActivityObject to get the output tvalues from.
 */
PyArrayObject *getTValues(PyObject *obj, int index) {
  ActivityObject *activity = (ActivityObject *)obj;
  if (activity != NULL) {
    int total = activity->nroutputs + PyList_Size(activity->manipulationNames);
    if (index < 0 || index > total - 1) {
      PyErr_Format(PyExc_IndexError, "index: %i is out of bounds!", index);
      return NULL;
    } else {
      if (index < activity->nroutputs) {
        // Output (manipulations are handled separately)
        switch (activity->outputs[index]->type) {
        case CONSTANT:
          return NULL;
        case PIECEWISE_CONSTANT:
        case PIECEWISE_LINEAR: {
          PiecewiseOutput *piecewiseCastedOutput =
              (PiecewiseOutput *)activity->outputs[index];
          return (PyArrayObject *)piecewiseCastedOutput->tvalues;
        }
        case CUBIC_SPLINE: {
          CubicSplineOutput *cubicCastedOutput =
              (CubicSplineOutput *)activity->outputs[index];
          return (PyArrayObject *)cubicCastedOutput->tvalues;
        }
        default:
          return NULL;
        }
      } else {
        // Manipulation index
        int stateIndex = index - activity->nroutputs;
        int nrStateManipulations = PyList_Size(activity->manipulationNames);
        if (stateIndex < nrStateManipulations) {
          return (PyArrayObject *)activity->stateManipulations[stateIndex]
              ->tvalues;
        }
        return NULL;
      }
    }
  } else {
    PyErr_SetString(
        PyExc_TypeError,
        "The obj input has to be a PyObject pointer to an ActivityObject!");
    return NULL;
  }
}

int getOutputType(PyObject *obj, int index) {
  ActivityObject *activity = (ActivityObject *)obj;
  if (activity != NULL) {
    int total = activity->nroutputs + PyList_Size(activity->manipulationNames);
    if (index >= 0 && index < total) {
      if (index < activity->nroutputs) {
        return activity->outputs[index]->type;
      } else {
        return STATE_MANIPULATION;
      }
    } else {
      PyErr_Format(PyExc_IndexError, "Output index %i is out of bounds!",
                   index);
      return -1;
    }
  } else {
    PyErr_SetString(
        PyExc_TypeError,
        "The obj input has to be a PyObject pointer to an ActivityObject!");
    return -1;
  }
}

int getManipulationMode(PyObject *obj, const char *stateName) {
  ActivityObject *activity = (ActivityObject *)obj;
  if (activity != NULL) {
    // Search through state manipulations names
    int nrStateManipulations = PyList_Size(activity->manipulationNames);
    for (int i = 0; i < nrStateManipulations; i++) {
      PyObject *name_obj = PyList_GetItem(activity->manipulationNames, i);
      const char *name_str = PyUnicode_AsUTF8(name_obj);
      if (!name_str)
        continue;

      if (strcmp(name_str, stateName) == 0) {
        return activity->stateManipulations[i]->mode;
      }

      // Also check compartment prefixes
      const char *colonPos = strchr(name_str, ':');
      if (colonPos != NULL && strcmp(colonPos + 1, stateName) == 0) {
        return activity->stateManipulations[i]->mode;
      }
    }

    // State manipulation not found
    return -1;
  } else {
    PyErr_SetString(
        PyExc_TypeError,
        "The obj input has to be a PyObject pointer to an ActivityObject!");
    return -1;
  }
}

/*
==========================================================================================
Activity module definition
==========================================================================================
*/

static PyModuleDef ActivityModule = {.m_base = PyModuleDef_HEAD_INIT,
                                     .m_name = "sund._Activity",
                                     .m_doc = "Activity Module",
                                     .m_size = -1};

PyMODINIT_FUNC PyInit__Activity(void) {
  PyObject *m;

  static void *Activity_API[Activity_API_pointers];
  PyObject *c_api_object;

  m = PyModule_Create(&ActivityModule);
  if (m == NULL)
    return NULL;

  /* Initialize the C API pointer array */
  Activity_API[isActivity_NUM] = (void *)isActivity;
  Activity_API[outputFeature_NUM] = (void *)outputFeature;
  Activity_API[nrOutputs_NUM] = (void *)nrOutputs;
  Activity_API[nrFeatures_NUM] = (void *)nrFeatures;
  Activity_API[outputNames_NUM] = (void *)outputNames;
  Activity_API[featureNames_NUM] = (void *)featureNames;
  Activity_API[featureUnits_NUM] = (void *)featureUnits;
  Activity_API[timeUnit_NUM] = (void *)timeUnit;
  Activity_API[setNonEditable_NUM] = (void *)setNonEditable;
  Activity_API[getTValues_NUM] = (void *)getTValues;
  Activity_API[getOutputType_NUM] = (void *)getOutputType;
  Activity_API[getManipulationMode_NUM] = (void *)getManipulationMode;
  Activity_API[manipulationNames_NUM] = (void *)manipulationNames;
  Activity_API[manipulationValues_NUM] = (void *)manipulationValues;

  /* Create a Capsule containing the API pointer array's address */
  c_api_object =
      PyCapsule_New((void *)Activity_API, "sund._Activity._C_API", NULL);

  // Activity/Simulation
  if (PyType_Ready(&ActivityType) < 0) {
    Py_DECREF(m);
    return NULL;
  }

  Py_INCREF(&ActivityType);

  if (PyModule_AddObject(m, "Activity", (PyObject *)&ActivityType) < 0 ||
      PyModule_AddObject(m, "_C_API", c_api_object) < 0 ||
      PyModule_AddIntMacro(m, CONSTANT) < 0 ||
      PyModule_AddIntMacro(m, PIECEWISE_CONSTANT) < 0 ||
      PyModule_AddIntMacro(m, PIECEWISE_LINEAR) < 0 ||
      PyModule_AddIntMacro(m, CUBIC_SPLINE) < 0 ||
      PyModule_AddIntMacro(m, STATE_MANIPULATION) < 0) {
    Py_DECREF(&ActivityType);
    Py_XDECREF(c_api_object);
    Py_DECREF(m);
    return NULL;
  }

  import_array();
  import_StringList();
  return m;
}
