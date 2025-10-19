#include "Models.h"
#include "Models_M_API.h"
#include "_StringList_C_API.h"
#include "pyarraymacros.h"

#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_2_3_API_VERSION
#include <numpy/arrayobject.h>

#include <cmath>

/*
==========================================================================================
Helper functions
==========================================================================================
*/

// allocation of model object
int MODEL::alloc(ModelObject *self) {
  npy_intp dims[1];
  // name
  Py_INCREF(Py_None);
  self->name = Py_None;
  // compartment
  Py_INCREF(Py_None);
  self->compartment = Py_None;
  // parametervalues
  dims[0] = self->model->numberof[MODEL_PARAMETER];
  self->parametervalues = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
  if (!self->parametervalues)
    return -1;
  // statevalues
  dims[0] = self->model->numberof[MODEL_STATE];
  self->statevalues = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
  if (!self->statevalues)
    return -1;
  // derivativevalues
  self->derivativevalues = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
  if (!self->derivativevalues)
    return -1;
  // idvector
  self->idvector = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
  if (!self->idvector)
    return -1;
  // statenames
  self->statenames = StringList_New(self->model->numberof[MODEL_STATE], 0);
  if (!self->statenames)
    return -1;
  // featurenames
  self->featurenames = StringList_New(self->model->numberof[MODEL_FEATURE], 0);
  if (!self->featurenames)
    return -1;
  // featureunits
  self->featureunits = StringList_New(self->model->numberof[MODEL_FEATURE], 1);
  if (!self->featureunits)
    return -1;
  // outputnames
  self->outputnames = StringList_New(self->model->numberof[MODEL_OUTPUT], 0);
  if (!self->outputnames)
    return -1;
  // inputnames
  self->inputnames = StringList_New(self->model->numberof[MODEL_INPUT], 0);
  if (!self->inputnames)
    return -1;
  // parameternames
  self->parameternames =
      StringList_New(self->model->numberof[MODEL_PARAMETER], 0);
  if (!self->parameternames)
    return -1;
  // eventnames
  self->eventnames = StringList_New(self->model->numberof[MODEL_EVENT], 0);
  if (!self->eventnames)
    return -1;
  // timeunit
  self->timeunit = PyUnicode_FromString(self->model->timeunit);

  return 0;
}

/*
==========================================================================================
GETTERS AND SETTERS
==========================================================================================
*/

PyObject *MODEL::getContainer(ModelObject *self) {
  // 'compartment' internal field remains storage until future PK refactor
  Py_INCREF(self->compartment);
  return self->compartment;
}

PyObject *MODEL::getCompartmentDeprecated(ModelObject *self) {
  if (PyErr_WarnEx(PyExc_DeprecationWarning,
                   "The 'compartment' attribute is deprecated; use 'container' "
                   "instead. In the future, 'compartment' will refer to volume "
                   "dependent compartments.",
                   1) < 0) {
    return NULL; // propagate if turned into error
  }
  Py_INCREF(self->compartment);
  return self->compartment;
}

PyObject *MODEL::getDerivativeValues(ModelObject *self) {
  Py_INCREF(self->derivativevalues);
  return self->derivativevalues;
}

PyObject *MODEL::getEventNames(ModelObject *self) {
  Py_INCREF(self->eventnames);
  return self->eventnames;
}

PyObject *MODEL::getFeatureNames(ModelObject *self) {
  Py_INCREF(self->featurenames);
  return self->featurenames;
}

PyObject *MODEL::getFeatureUnits(ModelObject *self) {
  Py_INCREF(self->featureunits);
  return self->featureunits;
}

PyObject *MODEL::getInputNames(ModelObject *self) {
  Py_INCREF(self->inputnames);
  return self->inputnames;
}

PyObject *MODEL::getName(ModelObject *self) {
  Py_INCREF(self->name);
  return self->name;
}

PyObject *MODEL::getOutputNames(ModelObject *self) {
  Py_INCREF(self->outputnames);
  return self->outputnames;
}

PyObject *MODEL::getParameterNames(ModelObject *self) {
  Py_INCREF(self->parameternames);
  return self->parameternames;
}

PyObject *MODEL::getParameterValues(ModelObject *self) {
  Py_INCREF(self->parametervalues);
  return self->parametervalues;
}

PyObject *MODEL::getStateNames(ModelObject *self) {
  Py_INCREF(self->statenames);
  return self->statenames;
}

PyObject *MODEL::getStateValues(ModelObject *self) {
  Py_INCREF(self->statevalues);
  return self->statevalues;
}

PyObject *MODEL::getTimeUnit(ModelObject *self) {
  Py_INCREF(self->timeunit);
  return self->timeunit;
}

int MODEL::setDerivativeValues(ModelObject *self, PyObject *value) {
  PyObject *tmp;
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError,
                    "Cannot delete the derivative_values attribute");
    return -1;
  }

  value = PyArray_FROM_OTF(value, NPY_DOUBLE,
                           NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!value) {
    PyErr_SetString(PyExc_TypeError,
                    "The given value does not match the derivative_values "
                    "attribute type. Expected a 1D list or array of numbers");
    Py_XDECREF(value);
    return -1;
  }

  // Check number of elements
  npy_intp expected = PyArray_DIMS((PyArrayObject *)self->derivativevalues)[0];
  npy_intp actual = PyArray_DIMS((PyArrayObject *)value)[0];
  if (actual < expected) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of derivative values: %i too few values!",
                 -(actual - expected));
    Py_XDECREF(value);
    return -1;
  } else if (actual > expected) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of derivative values: %i too many values!",
                 actual - expected);
    Py_XDECREF(value);
    return -1;
  }

  tmp = self->derivativevalues;
  self->derivativevalues = value;
  Py_DECREF(tmp);
  return 0;
}

int MODEL::setEventNames(ModelObject *self, PyObject *value) {
  return StringList_Update(self->eventnames, value);
}

int MODEL::setFeatureNames(ModelObject *self, PyObject *value) {
  return StringList_Update(self->featurenames, value);
}

int MODEL::setInputNames(ModelObject *self, PyObject *value) {
  return StringList_Update(self->inputnames, value);
}

int MODEL::setName(ModelObject *self, PyObject *value) {
  PyObject *tmp;
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the name attribute");
    return -1;
  }

  if (!PyUnicode_Check(value)) {
    PyErr_SetString(PyExc_TypeError,
                    "Only strings can be assigned the name attribute");
    return -1;
  }
  tmp = self->name;
  Py_INCREF(value);
  self->name = value;
  Py_DECREF(tmp);
  return 0;
}

int MODEL::setOutputNames(ModelObject *self, PyObject *value) {
  return StringList_Update(self->outputnames, value);
}

int MODEL::setParameterNames(ModelObject *self, PyObject *value) {
  return StringList_Update(self->parameternames, value);
}

int MODEL::setParameterValues(ModelObject *self, PyObject *value) {
  PyObject *tmp;
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError,
                    "Cannot delete the parametervalues attribute");
    return -1;
  }

  value = PyArray_FROM_OTF(value, NPY_DOUBLE,
                           NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!value) {
    PyErr_SetString(PyExc_TypeError,
                    "The given value does not match the parameter_values "
                    "attribute type. Expected a 1D list or array of numbers");
    Py_XDECREF(value);
    return -1;
  }

  // Check number of elements
  npy_intp expected = PyArray_DIMS((PyArrayObject *)self->parametervalues)[0];
  npy_intp actual = PyArray_DIMS((PyArrayObject *)value)[0];
  if (actual < expected) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of parameter values: %i too few values!",
                 -(actual - expected));
    Py_XDECREF(value);
    return -1;
  } else if (actual > expected) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of parameter values: %i too many values!",
                 actual - expected);
    Py_XDECREF(value);
    return -1;
  }

  tmp = self->parametervalues;
  self->parametervalues = value;
  Py_DECREF(tmp);
  return 0;
}

int MODEL::setStateNames(ModelObject *self, PyObject *value) {
  return StringList_Update(self->statenames, value);
}

int MODEL::setStateValues(ModelObject *self, PyObject *value) {
  PyObject *tmp;
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError,
                    "Cannot delete the state_values attribute");
    return -1;
  }

  value = PyArray_FROM_OTF(value, NPY_DOUBLE,
                           NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!value) {
    PyErr_SetString(PyExc_TypeError,
                    "The given value does not match the state_values attribute "
                    "type. Expected a 1D list or array of numbers");
    Py_XDECREF(value);
    return -1;
  }

  // Check number of elements
  npy_intp expected = PyArray_DIMS((PyArrayObject *)self->statevalues)[0];
  npy_intp actual = PyArray_DIMS((PyArrayObject *)value)[0];
  if (actual < expected) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of state values: %i too few values!",
                 -(actual - expected));
    Py_XDECREF(value);
    return -1;
  } else if (actual > expected) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of state values: %i too many values!",
                 actual - expected);
    Py_XDECREF(value);
    return -1;
  }

  tmp = self->statevalues;
  self->statevalues = value;
  Py_DECREF(tmp);
  return 0;
}

/*
==========================================================================================
PyMethods
==========================================================================================
*/

PyObject *MODEL::differentialStates(ModelObject *self, PyObject *args) {
  return PyArray_Cast((PyArrayObject *)self->idvector, NPY_BOOL);
}

PyObject *MODEL::hasAlgebraicEquations(ModelObject *self, PyObject *args) {
  if (self->model->has_algebraic_eq)
    Py_RETURN_TRUE;
  else
    Py_RETURN_FALSE;
}

PyObject *MODEL::mandatoryInputs(ModelObject *self, PyObject *args) {
  int k;
  npy_intp dims[1];
  char *data;
  PyObject *mandatoryinputs;

  dims[0] = self->model->numberof[MODEL_INPUT];
  mandatoryinputs = PyArray_SimpleNew(1, dims, NPY_BOOL);

  data = PyArray_BYTES((PyArrayObject *)mandatoryinputs);
  for (k = 0; k < dims[0]; k++) {
    if (self->model->mandatoryinputs[k] == 0)
      data[k] = 1;
    else
      data[k] = 0;
  }

  return mandatoryinputs;
}

PyObject *MODEL::reduce(ModelObject *self) {
  PyObject *ret, *args, *state;

  // Use canonical 'container' position in constructor arg tuple (first element)
  // while keeping underlying storage field 'compartment'. Older pickles
  // expecting 'compartment' are still readable because __setstate__ unpacks
  // positionally.
  state = Py_BuildValue(
      "OOOOOOOO", self->name, self->statenames, self->parameternames,
      self->featurenames, self->outputnames, self->inputnames, self->eventnames,
      Py_BuildValue("OOOO", self->compartment, self->statevalues,
                    self->derivativevalues, self->parametervalues));
  args = PyTuple_New(0); // Empty tuple for no positional args

  ret = Py_BuildValue("OOO", Py_TYPE(self), args, state);
  Py_DECREF(args);
  Py_DECREF(state);
  return ret;
}

PyObject *MODEL::resetStates(ModelObject *self, PyObject *args) {
  self->model->initialcondition(
      PYDATA(self->statevalues), PYDATA(self->derivativevalues),
      PYDATA(self->parametervalues), self->model->defaultInputs);
  Py_RETURN_NONE;
}

PyObject *MODEL::resetParameters(ModelObject *self, PyObject *args) {
  memcpy(PYDATA(self->parametervalues), self->model->defaultparameters,
         self->model->numberof[MODEL_PARAMETER] * sizeof(double));
  Py_RETURN_NONE;
}

PyObject *MODEL::setState(ModelObject *self, PyObject *statetuple) {
  PyObject *name, *statenames, *parameternames, *featurenames, *outputnames,
      *inputnames, *eventnames, *constructor_args;
  PyObject *compartment, *state_values, *derivative_values, *parameter_values;
  PyObject *tmp;

  if (!PyArg_Parse(statetuple, "((OOOOOOOO),)", &name, &statenames,
                   &parameternames, &featurenames, &outputnames, &inputnames,
                   &eventnames, &constructor_args))
    return NULL;

  // Extract constructor arguments
  if (!PyArg_Parse(constructor_args, "(OOOO)", &compartment, &state_values,
                   &derivative_values, &parameter_values))
    return NULL;

  // Set constructor arguments if they were set
  if (compartment && compartment != Py_None) {
    tmp = self->compartment;
    Py_INCREF(compartment);
    self->compartment = compartment;
    Py_DECREF(tmp);
  }

  if (state_values && state_values != Py_None) {
    if (MODEL::setStateValues(self, state_values) < 0)
      return NULL;
  }

  if (derivative_values && derivative_values != Py_None) {
    if (MODEL::setDerivativeValues(self, derivative_values) < 0)
      return NULL;
  }

  if (parameter_values && parameter_values != Py_None) {
    if (MODEL::setParameterValues(self, parameter_values) < 0)
      return NULL;
  }

  if (MODEL::setName(self, name) < 0)
    return NULL;
  if (MODEL::setStateNames(self, statenames) < 0)
    return NULL;
  if (MODEL::setParameterNames(self, parameternames) < 0)
    return NULL;
  if (MODEL::setFeatureNames(self, featurenames) < 0)
    return NULL;
  if (MODEL::setOutputNames(self, outputnames) < 0)
    return NULL;
  if (MODEL::setInputNames(self, inputnames) < 0)
    return NULL;
  if (MODEL::setEventNames(self, eventnames) < 0)
    return NULL;
  Py_RETURN_NONE;
}

/*
==========================================================================================
Model_Type definition
==========================================================================================
*/

static int Model_init(ModelObject *self, PyObject *args, PyObject *kwds) {
  // check input arguments
  static char *kwlist[] = {const_cast<char *>("container"),
                           const_cast<char *>("compartment"), /* deprecated */
                           const_cast<char *>("state_values"),
                           const_cast<char *>("derivative_values"),
                           const_cast<char *>("parameter_values"),
                           NULL};
  PyObject *container = NULL;   // canonical
  PyObject *compartment = NULL; // deprecated alias
  PyObject *state_values = NULL;
  PyObject *derivative_values = NULL;
  PyObject *parameter_values = NULL;
  PyObject *tmp;
  const char *name;
  int k;
  double *idvector;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|$OOOOO", kwlist, &container,
                                   &compartment, &state_values,
                                   &derivative_values, &parameter_values))
    return -1;

  // Handle parameter values
  if (parameter_values) {
    if (MODEL::setParameterValues(self, parameter_values) < 0)
      return -1;
  } else
    memcpy(PYDATA(self->parametervalues), self->model->defaultparameters,
           self->model->numberof[MODEL_PARAMETER] * sizeof(double));

  // statevalues and derivativevalues
  // Reset states derivative, need to be done first since both
  // states/derivatives are effected
  self->model->initialcondition(
      PYDATA(self->statevalues), PYDATA(self->derivativevalues),
      PYDATA(self->parametervalues), self->model->defaultInputs);

  // Handle state values
  if (state_values) {
    if (MODEL::setStateValues(self, state_values) < 0)
      return -1;
  }

  // Handle derivative values
  if (derivative_values) {
    if (MODEL::setDerivativeValues(self, derivative_values) < 0)
      return -1;
  }
  // idvector
  // 1.0: state is differential, 0.0: state is algebraic
  idvector = PYDATA(self->idvector);
  for (k = 1; k < self->model->differentialstates[0] + 1; k++) {
    idvector[self->model->differentialstates[k]] = 1.0;
  }
  // container (canonical) / deprecated compartment alias
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
  if (selected) {
    if (!PyUnicode_Check(selected)) {
      PyErr_SetString(PyExc_TypeError, "Container needs to be a string object");
      return -1;
    }
    if (selected == compartment) {
      if (PyErr_WarnEx(PyExc_DeprecationWarning,
                       "The 'compartment' argument is deprecated; use "
                       "'container' instead. In the future, 'compartment' will "
                       "refer to volume dependent compartments.",
                       1) < 0) {
        return -1;
      }
    }
    tmp = self->compartment;
    Py_INCREF(selected);
    self->compartment = selected;
    Py_DECREF(tmp);
  }
  // name
  name = Py_TYPE(self)->tp_name; // = sund.Models.modelname
  name = strrchr(name, '.') + 1; // = modelname
  tmp = self->name;
  self->name = self->compartment != Py_None
                   ? PyUnicode_FromFormat("%S:%s", self->compartment, name)
                   : PyUnicode_FromString(name);
  Py_DECREF(tmp);
  // statenames
  for (k = 0; k < self->model->numberof[MODEL_STATE]; k++) {
    tmp = self->compartment != Py_None
              ? PyUnicode_FromFormat("%S:%s", self->compartment,
                                     self->model->statenames[k])
              : PyUnicode_FromString(self->model->statenames[k]);
    if (!tmp || PyList_SetItem(self->statenames, k, tmp) < 0) {
      Py_XDECREF(tmp);
      return -1;
    }
  }
  // featurenames
  for (k = 0; k < self->model->numberof[MODEL_FEATURE]; k++) {
    tmp = self->compartment != Py_None
              ? PyUnicode_FromFormat("%S:%s", self->compartment,
                                     self->model->featurenames[k])
              : PyUnicode_FromString(self->model->featurenames[k]);
    if (!tmp || PyList_SetItem(self->featurenames, k, tmp) < 0) {
      Py_XDECREF(tmp);
      return -1;
    }
  }
  // featureunits
  for (k = 0; k < self->model->numberof[MODEL_FEATURE]; k++) {
    tmp = self->compartment != Py_None
              ? PyUnicode_FromFormat("%S:%s", self->compartment,
                                     self->model->featureunits[k])
              : PyUnicode_FromString(self->model->featureunits[k]);
    if (!tmp || PyList_SetItem(self->featureunits, k, tmp) < 0) {
      Py_XDECREF(tmp);
      return -1;
    }
  }
  // outputnames
  for (k = 0; k < self->model->numberof[MODEL_OUTPUT]; k++) {
    tmp = self->compartment != Py_None
              ? PyUnicode_FromFormat("%S:%s", self->compartment,
                                     self->model->outputnames[k])
              : PyUnicode_FromString(self->model->outputnames[k]);
    if (!tmp || PyList_SetItem(self->outputnames, k, tmp) < 0) {
      Py_XDECREF(tmp);
      return -1;
    }
  }
  // inputnames
  for (k = 0; k < self->model->numberof[MODEL_INPUT]; k++) {
    const char *original_name_ptr = self->model->inputnames[k];
    const char *name_to_use = original_name_ptr;
    bool had_leading_colon = false;

    // Check for and effectively remove leading colon for processing
    if (name_to_use[0] == ':') {
      name_to_use++;
      had_leading_colon = true;
    }

    // If a compartment is present AND the original name did NOT start with a
    // colon AND the (potentially stripped) name does not already contain a
    // colon, then prepend compartment.
    if (self->compartment != Py_None && !had_leading_colon &&
        strchr(name_to_use, ':') == NULL) {
      tmp = PyUnicode_FromFormat("%S:%s", self->compartment, name_to_use);
    } else {
      tmp = PyUnicode_FromString(name_to_use);
    }

    if (!tmp || PyList_SetItem(self->inputnames, k, tmp) < 0) {
      Py_XDECREF(tmp);
      return -1;
    }
  }
  // parameternames
  for (k = 0; k < self->model->numberof[MODEL_PARAMETER]; k++) {
    tmp = self->compartment != Py_None
              ? PyUnicode_FromFormat("%S:%s", self->compartment,
                                     self->model->parameternames[k])
              : PyUnicode_FromString(self->model->parameternames[k]);
    if (!tmp || PyList_SetItem(self->parameternames, k, tmp) < 0) {
      Py_XDECREF(tmp);
      return -1;
    }
  }
  // eventnames
  for (k = 0; k < self->model->numberof[MODEL_EVENT]; k++) {
    tmp = self->compartment != Py_None
              ? PyUnicode_FromFormat("%S:%s", self->compartment,
                                     self->model->eventnames[k])
              : PyUnicode_FromString(self->model->eventnames[k]);
    if (!tmp || PyList_SetItem(self->eventnames, k, tmp) < 0) {
      Py_XDECREF(tmp);
      return -1;
    }
  }

  return 0;
}

static void Model_dealloc(ModelObject *self) {
  Py_XDECREF(self->name);
  Py_XDECREF(self->compartment);
  Py_XDECREF(self->statevalues);
  Py_XDECREF(self->derivativevalues);
  Py_XDECREF(self->idvector);
  Py_XDECREF(self->parametervalues);
  Py_XDECREF(self->statenames);
  Py_XDECREF(self->featurenames);
  Py_XDECREF(self->featureunits);
  Py_XDECREF(self->outputnames);
  Py_XDECREF(self->inputnames);
  Py_XDECREF(self->parameternames);
  Py_XDECREF(self->eventnames);
  Py_XDECREF(self->timeunit);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyTypeObject Model_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "sund._Models.Model",
    .tp_basicsize = sizeof(ModelObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)Model_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "Model object",
    .tp_methods = Model_methods,
    .tp_getset = Model_getsetters,
    .tp_init = (initproc)Model_init,
};

/*
==========================================================================================
C_API
==========================================================================================
*/
static int Model_isModel(PyObject *obj) {
  if (Py_TYPE(obj)->tp_base == &Model_Type)
    return 1;
  else
    return 0;
}

static ModelFunction *Model_modelFunction(PyObject *obj) {
  return ((ModelObject *)obj)->model->function;
}

static PyObject *Model_parameters(PyObject *obj) {
  return ((ModelObject *)obj)->parametervalues;
}

static PyObject *Model_timeUnit(PyObject *obj) {
  return ((ModelObject *)obj)->timeunit;
}

static PyObject *Model_name(PyObject *obj) {
  return ((ModelObject *)obj)->name;
}

static const int *Model_numberof(PyObject *obj) {
  return ((ModelObject *)obj)->model->numberof;
}

static const int *Model_inputDependency(PyObject *obj) {
  return ((ModelObject *)obj)->model->inputdependency;
}

static PyObject *Model_stateNames(PyObject *obj) {
  return ((ModelObject *)obj)->statenames;
}

static PyObject *Model_stateValues(PyObject *obj) {
  return ((ModelObject *)obj)->statevalues;
}

static PyObject *Model_derivativeValues(PyObject *obj) {
  return ((ModelObject *)obj)->derivativevalues;
}

static PyObject *Model_featureNames(PyObject *obj) {
  return ((ModelObject *)obj)->featurenames;
}

static PyObject *Model_featureUnits(PyObject *obj) {
  return ((ModelObject *)obj)->featureunits;
}

static PyObject *Model_outputNames(PyObject *obj) {
  return ((ModelObject *)obj)->outputnames;
}

static PyObject *Model_inputNames(PyObject *obj) {
  return ((ModelObject *)obj)->inputnames;
}

static PyObject *Model_parameterNames(PyObject *obj) {
  return ((ModelObject *)obj)->parameternames;
}

static PyObject *Model_eventNames(PyObject *obj) {
  return ((ModelObject *)obj)->eventnames;
}

static PyObject *Model_idVector(PyObject *obj) {
  return ((ModelObject *)obj)->idvector;
}

static const int Model_hasAlgebraicEq(PyObject *obj) {
  return ((ModelObject *)obj)->model->has_algebraic_eq;
}

static const int *Model_mandatoryInputs(PyObject *obj) {
  return ((ModelObject *)obj)->model->mandatoryinputs;
}

/*
==========================================================================================
Model module definitions
==========================================================================================
*/
static PyModuleDef ModelsModule = {.m_base = PyModuleDef_HEAD_INIT,
                                   .m_name = "sund._Models",
                                   .m_doc = "Model definition module",
                                   .m_size = -1};

PyMODINIT_FUNC PyInit__Models(void) {
  PyObject *m;

  static void *Models_C_API[Models_C_API_pointers];
  static void *Models_M_API[Models_M_API_pointers];
  PyObject *c_api_object, *m_api_object;

  m = PyModule_Create(&ModelsModule);
  if (m == NULL)
    return NULL;

  /* Initialize the C API pointer array */
  Models_C_API[Model_isModel_NUM] = (void *)Model_isModel;
  Models_C_API[Model_modelFunction_NUM] = (void *)Model_modelFunction;
  Models_C_API[Model_parameters_NUM] = (void *)Model_parameters;
  Models_C_API[Model_timeUnit_NUM] = (void *)Model_timeUnit;
  Models_C_API[Model_name_NUM] = (void *)Model_name;
  Models_C_API[Model_numberof_NUM] = (void *)Model_numberof;
  Models_C_API[Model_inputDependency_NUM] = (void *)Model_inputDependency;
  Models_C_API[Model_stateValues_NUM] = (void *)Model_stateValues;
  Models_C_API[Model_featureNames_NUM] = (void *)Model_featureNames;
  Models_C_API[Model_featureUnits_NUM] = (void *)Model_featureUnits;
  Models_C_API[Model_outputNames_NUM] = (void *)Model_outputNames;
  Models_C_API[Model_inputNames_NUM] = (void *)Model_inputNames;
  Models_C_API[Model_parameterNames_NUM] = (void *)Model_parameterNames;
  Models_C_API[Model_eventNames_NUM] = (void *)Model_eventNames;
  Models_C_API[Model_derivativeValues_NUM] = (void *)Model_derivativeValues;
  Models_C_API[Model_stateNames_NUM] = (void *)Model_stateNames;
  Models_C_API[Model_idVector_NUM] = (void *)Model_idVector;
  Models_C_API[Model_hasAlgebraicEq_NUM] = (void *)Model_hasAlgebraicEq;
  Models_C_API[Model_mandatoryInputs_NUM] = (void *)Model_mandatoryInputs;

  /* Initialize the M API pointer array */
  Models_M_API[Model_alloc_NUM] = (void *)MODEL::alloc;
  Models_M_API[Model_Base_Type_NUM] = (void *)&Model_Type;

  /* Create a Capsule containing the API pointer array's address */
  c_api_object =
      PyCapsule_New((void *)Models_C_API, "sund._Models._C_API", NULL);
  m_api_object =
      PyCapsule_New((void *)Models_M_API, "sund._Models._M_API", NULL);

  if (PyModule_AddObject(m, "_C_API", c_api_object) < 0) {
    Py_XDECREF(c_api_object);
    Py_DECREF(m);
    return NULL;
  }
  if (PyModule_AddObject(m, "_M_API", m_api_object) < 0) {
    Py_XDECREF(m_api_object);
    Py_XDECREF(c_api_object);
    Py_DECREF(m);
    return NULL;
  }
  // if(addModels(m, nrModels_Type, Models_Type) < 0){
  //     Py_DECREF(c_api_object);
  //     Py_DECREF(m);
  //     return NULL;
  // }
  import_array();
  import_StringList();
  return m;
}
