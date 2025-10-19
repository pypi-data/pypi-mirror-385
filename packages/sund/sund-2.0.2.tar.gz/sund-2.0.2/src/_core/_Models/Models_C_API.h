#ifndef _MODELS_C_API_H
#define _MODELS_C_API_H

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
Model Introspection (read/accessor) C API
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
C_API
==========================================================================================
*/

static void *
    *Models_API; /* shared pointer table for full (extended) model API */
/* Import the full (extended) accessor API (idempotent). Fatal on failure. */
static inline void import_ModelFullAPI(void) {
  if (!Models_API) {
    Models_API = (void **)PyCapsule_Import("sund._Models._C_API", 0);
    if (!Models_API) {
      Py_FatalError("sund: failed to import capsule 'sund._Models._C_API'");
    }
  }
}
#define Model_isModel                                                          \
  (*(Model_isModel_RETURN(*) Model_isModel_PROTO)Models_API[Model_isModel_NUM])
#define Model_modelFunction                                                    \
  (*(Model_modelFunction_RETURN(*)                                             \
         Model_modelFunction_PROTO)Models_API[Model_modelFunction_NUM])
#define Model_parameters                                                       \
  (*(Model_parameters_RETURN(*)                                                \
         Model_parameters_PROTO)Models_API[Model_parameters_NUM])
#define Model_timeUnit                                                         \
  (*(Model_timeUnit_RETURN(*)                                                  \
         Model_timeUnit_PROTO)Models_API[Model_timeUnit_NUM])
#define Model_name                                                             \
  (*(Model_name_RETURN(*) Model_name_PROTO)Models_API[Model_name_NUM])
#define Model_numberof                                                         \
  (*(Model_numberof_RETURN(*)                                                  \
         Model_numberof_PROTO)Models_API[Model_numberof_NUM])
#define Model_inputDependency                                                  \
  (*(Model_inputDependency_RETURN(*)                                           \
         Model_inputDependency_PROTO)Models_API[Model_inputDependency_NUM])
#define Model_stateValues                                                      \
  (*(Model_stateValues_RETURN(*)                                               \
         Model_stateValues_PROTO)Models_API[Model_stateValues_NUM])
#define Model_featureNames                                                     \
  (*(Model_featureNames_RETURN(*)                                              \
         Model_featureNames_PROTO)Models_API[Model_featureNames_NUM])
#define Model_featureUnits                                                     \
  (*(Model_featureUnits_RETURN(*)                                              \
         Model_featureUnits_PROTO)Models_API[Model_featureUnits_NUM])
#define Model_outputNames                                                      \
  (*(Model_outputNames_RETURN(*)                                               \
         Model_outputNames_PROTO)Models_API[Model_outputNames_NUM])
#define Model_inputNames                                                       \
  (*(Model_inputNames_RETURN(*)                                                \
         Model_inputNames_PROTO)Models_API[Model_inputNames_NUM])
#define Model_parameterNames                                                   \
  (*(Model_parameterNames_RETURN(*)                                            \
         Model_parameterNames_PROTO)Models_API[Model_parameterNames_NUM])
#define Model_eventNames                                                       \
  (*(Model_eventNames_RETURN(*)                                                \
         Model_eventNames_PROTO)Models_API[Model_eventNames_NUM])
#define Model_derivativeValues                                                 \
  (*(Model_derivativeValues_RETURN(*)                                          \
         Model_derivativeValues_PROTO)Models_API[Model_derivativeValues_NUM])
#define Model_stateNames                                                       \
  (*(Model_stateNames_RETURN(*)                                                \
         Model_stateNames_PROTO)Models_API[Model_stateNames_NUM])
#define Model_idVector                                                         \
  (*(Model_idVector_RETURN(*)                                                  \
         Model_idVector_PROTO)Models_API[Model_idVector_NUM])
#define Model_hasAlgebraicEq                                                   \
  (*(Model_hasAlgebraicEq_RETURN(*)                                            \
         Model_hasAlgebraicEq_PROTO)Models_API[Model_hasAlgebraicEq_NUM])
#define Model_mandatoryInputs                                                  \
  (*(Model_mandatoryInputs_RETURN(*)                                           \
         Model_mandatoryInputs_PROTO)Models_API[Model_mandatoryInputs_NUM])

#endif
