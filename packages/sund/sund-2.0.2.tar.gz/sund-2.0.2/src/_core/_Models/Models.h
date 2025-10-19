#ifndef _MODELS_H
#define _MODELS_H

#include "model_structure.h"

#include "Python.h"

#define MODEL_STATE 0
#define MODEL_FEATURE 1
#define MODEL_OUTPUT 2
#define MODEL_INPUT 3
#define MODEL_EVENT 4
#define MODEL_PARAMETER 5

/*
==========================================================================================
C_API
==========================================================================================
*/
#define Model_isModel_NUM 0
#define Model_isModel_RETURN int
#define Model_isModel_PROTO (PyObject * obj)

#define Model_modelFunction_NUM 1
#define Model_modelFunction_RETURN ModelFunction *
#define Model_modelFunction_PROTO (PyObject * obj)

#define Model_parameters_NUM 2
#define Model_parameters_RETURN PyObject *
#define Model_parameters_PROTO (PyObject * obj)

#define Model_timeUnit_NUM 3
#define Model_timeUnit_RETURN PyObject *
#define Model_timeUnit_PROTO (PyObject * obj)

#define Model_name_NUM 4
#define Model_name_RETURN PyObject *
#define Model_name_PROTO (PyObject * obj)

#define Model_numberof_NUM 5
#define Model_numberof_RETURN const int *
#define Model_numberof_PROTO (PyObject * obj)

#define Model_inputDependency_NUM 6
#define Model_inputDependency_RETURN const int *
#define Model_inputDependency_PROTO (PyObject * obj)

#define Model_stateValues_NUM 7
#define Model_stateValues_RETURN PyObject *
#define Model_stateValues_PROTO (PyObject * obj)

#define Model_featureNames_NUM 8
#define Model_featureNames_RETURN PyObject *
#define Model_featureNames_PROTO (PyObject * obj)

#define Model_featureUnits_NUM 9
#define Model_featureUnits_RETURN PyObject *
#define Model_featureUnits_PROTO (PyObject * obj)

#define Model_outputNames_NUM 10
#define Model_outputNames_RETURN PyObject *
#define Model_outputNames_PROTO (PyObject * obj)

#define Model_inputNames_NUM 11
#define Model_inputNames_RETURN PyObject *
#define Model_inputNames_PROTO (PyObject * obj)

#define Model_parameterNames_NUM 12
#define Model_parameterNames_RETURN PyObject *
#define Model_parameterNames_PROTO (PyObject * obj)

#define Model_eventNames_NUM 13
#define Model_eventNames_RETURN PyObject *
#define Model_eventNames_PROTO (PyObject * obj)

#define Model_derivativeValues_NUM 14
#define Model_derivativeValues_RETURN PyObject *
#define Model_derivativeValues_PROTO (PyObject * obj)

#define Model_stateNames_NUM 15
#define Model_stateNames_RETURN PyObject *
#define Model_stateNames_PROTO (PyObject * obj)

#define Model_idVector_NUM 16
#define Model_idVector_RETURN PyObject *
#define Model_idVector_PROTO (PyObject * obj)

#define Model_hasAlgebraicEq_NUM 17
#define Model_hasAlgebraicEq_RETURN const int
#define Model_hasAlgebraicEq_PROTO (PyObject * obj)

#define Model_mandatoryInputs_NUM 18
#define Model_mandatoryInputs_RETURN const int *
#define Model_mandatoryInputs_PROTO (PyObject * obj)

/* Total number of C API pointers */
#define Models_C_API_pointers 19

/*
==========================================================================================
Function declaration
==========================================================================================
*/

namespace MODEL {
int alloc(ModelObject *self);

/*
==========================================================================================
GETTERS AND SETTERS
==========================================================================================
*/
// New getter for the canonical 'container' name (no warning)
PyObject *getContainer(ModelObject *self);
// Deprecated getter for 'compartment' that emits a DeprecationWarning
PyObject *getCompartmentDeprecated(ModelObject *self);

PyObject *getDerivativeValues(ModelObject *self);

PyObject *getEventNames(ModelObject *self);

PyObject *getFeatureNames(ModelObject *self);

PyObject *getFeatureUnits(ModelObject *self);

PyObject *getInputNames(ModelObject *self);

PyObject *getName(ModelObject *self);

PyObject *getOutputNames(ModelObject *self);

PyObject *getParameterNames(ModelObject *self);

PyObject *getParameterValues(ModelObject *self);

PyObject *getStateNames(ModelObject *self);

PyObject *getStateValues(ModelObject *self);

PyObject *getTimeUnit(ModelObject *self);

int setDerivativeValues(ModelObject *self, PyObject *value);

int setEventNames(ModelObject *self, PyObject *value);

int setFeatureNames(ModelObject *self, PyObject *value);

int setInputNames(ModelObject *self, PyObject *value);

int setName(ModelObject *self, PyObject *value);

int setOutputNames(ModelObject *self, PyObject *value);

int setParameterNames(ModelObject *self, PyObject *value);

int setParameterValues(ModelObject *self, PyObject *value);

int setStateNames(ModelObject *self, PyObject *value);

int setStateValues(ModelObject *self, PyObject *value);

/*
==========================================================================================
PyMethods
==========================================================================================
*/
PyObject *resetStates(ModelObject *self, PyObject *args);

PyObject *resetParameters(ModelObject *self, PyObject *args);

PyObject *hasAlgebraicEquations(ModelObject *self, PyObject *args);

PyObject *differentialStates(ModelObject *self, PyObject *args);

PyObject *mandatoryInputs(ModelObject *self, PyObject *args);

PyObject *reduce(ModelObject *self);

PyObject *setState(ModelObject *self, PyObject *statetuple);
} // namespace MODEL

static PyGetSetDef Model_getsetters[] = {
    {"container", (getter)MODEL::getContainer, NULL,
     "Model container (formerly called 'compartment')", NULL},
    {"compartment", (getter)MODEL::getCompartmentDeprecated, NULL,
     "DEPRECATED: use 'container' instead. Will be repurposed for PK "
     "compartments in a future release.",
     NULL},
    {"derivative_values", (getter)MODEL::getDerivativeValues,
     (setter)MODEL::setDerivativeValues, "Model state values", NULL},
    {"event_names", (getter)MODEL::getEventNames, (setter)MODEL::setEventNames,
     "Model events names", NULL},
    {"feature_names", (getter)MODEL::getFeatureNames,
     (setter)MODEL::setFeatureNames, "Model feature names", NULL},
    {"feature_units", (getter)MODEL::getFeatureUnits, NULL,
     "Model feature units", NULL},
    {"input_names", (getter)MODEL::getInputNames, (setter)MODEL::setInputNames,
     "Model input names", NULL},
    {"name", (getter)MODEL::getName, (setter)MODEL::setName, "Model name",
     NULL},
    {"output_names", (getter)MODEL::getOutputNames,
     (setter)MODEL::setOutputNames, "Model output names", NULL},
    {"parameter_names", (getter)MODEL::getParameterNames,
     (setter)MODEL::setParameterNames, "Model parameter names", NULL},
    {"parameter_values", (getter)MODEL::getParameterValues,
     (setter)MODEL::setParameterValues, "Model parameter values", NULL},
    {"state_names", (getter)MODEL::getStateNames, (setter)MODEL::setStateNames,
     "Model state names", NULL},
    {"state_values", (getter)MODEL::getStateValues,
     (setter)MODEL::setStateValues, "Model state values", NULL},
    {"time_unit", (getter)MODEL::getTimeUnit, NULL, "Model time unit", NULL},
    {NULL} /* Sentinel */
};

static PyMethodDef Model_methods[] = {
    {"__reduce__", (PyCFunction)MODEL::reduce, METH_NOARGS,
     "__reduce__ function"},
    {"__setstate__", (PyCFunction)MODEL::setState, METH_VARARGS,
     "__setstate__ function"},
    {"differential_states", (PyCFunction)MODEL::differentialStates, METH_NOARGS,
     "Return an array of boolean, holds the value True if respective state is "
     "a differential state"},
    {"has_algebraic_equations", (PyCFunction)MODEL::hasAlgebraicEquations,
     METH_NOARGS, "Check if model contains algebraic equations"},
    {"mandatory_inputs", (PyCFunction)MODEL::mandatoryInputs, METH_NOARGS,
     "Return an array of boolean, holds the value True if respective input is "
     "mandatory for the model"},
    {"reset_parameters", (PyCFunction)MODEL::resetParameters, METH_NOARGS,
     "Reset parameter values"},
    {"reset_states", (PyCFunction)MODEL::resetStates, METH_NOARGS,
     "Reset state and derivative values"},
    {NULL} /* Sentinel */
};

#endif
