#ifndef ACTIVITY_API
#define ACTIVITY_API

#define NPY_NO_DEPRECATED_API NPY_2_3_API_VERSION
#include "Python.h"
#include <numpy/arrayobject.h>

#define ACTIVITY_OUTPUT 0
#define ACTIVITY_FEATURE 1

/* C API defines */
#define isActivity_NUM 0
using isActivityPointer = bool (*)(PyObject *obj);

#define outputFeature_NUM 1
using outputFeaturePointer = void (*)(PyObject *self, double time_local,
                                      double *outputvector,
                                      double *featurevector, int DOflag);

#define nrOutputs_NUM 2
using nrOutputsPointer = int (*)(PyObject *self);

#define nrFeatures_NUM 3
using nrFeaturesPointer = int (*)(PyObject *self);

#define outputNames_NUM 4
using outputNamesPointer = PyObject *(*)(PyObject * self);

#define featureNames_NUM 5
using featureNamesPointer = PyObject *(*)(PyObject * self);

#define featureUnits_NUM 6
using featureUnitsPointer = PyObject *(*)(PyObject * self);

#define timeUnit_NUM 7
using timeUnitPointer = PyObject *(*)(PyObject * self);

#define setNonEditable_NUM 8
using setNonEditablePointer = void (*)(PyObject *self);

#define getTValues_NUM 9
using getTValuesPointer = PyArrayObject *(*)(PyObject * self, int index);

#define getOutputType_NUM 10
using getOutputTypePointer = int (*)(PyObject *activityObject, int outputIndex);

#define getManipulationMode_NUM 11
using getManipulationModePointer = int (*)(PyObject *activityObject,
                                           const char *stateName);

#define manipulationNames_NUM 12
using manipulationNamesPointer = PyObject *(*)(PyObject * self);

#define manipulationValues_NUM 13
using manipulationValuesPointer = void (*)(PyObject *self, double time_local,
                                           double *manipvector);

/* Total number of C API pointers */
#define Activity_API_pointers 14

/*
==========================================================================================
C_API
==========================================================================================
*/
#define import_Activity()                                                      \
  {                                                                            \
    if (_import_Activity() < 0) {                                              \
      PyErr_Print();                                                           \
      PyErr_SetString(PyExc_ImportError,                                       \
                      "sund._Activity._C_API failed to import");               \
      return NULL;                                                             \
    }                                                                          \
  }
#define isActivity (*(isActivityPointer)Activity_API[isActivity_NUM])
#define outputFeature (*(outputFeaturePointer)Activity_API[outputFeature_NUM])
#define nrOutputs (*(nrOutputsPointer)Activity_API[nrOutputs_NUM])
#define nrFeatures (*(nrFeaturesPointer)Activity_API[nrFeatures_NUM])
#define outputNames (*(outputNamesPointer)Activity_API[outputNames_NUM])
#define featureNames (*(featureNamesPointer)Activity_API[featureNames_NUM])
#define featureUnits (*(featureUnitsPointer)Activity_API[featureUnits_NUM])
#define timeUnit_API (*(timeUnitPointer)Activity_API[timeUnit_NUM])
#define setNonEditable                                                         \
  (*(setNonEditablePointer)Activity_API[setNonEditable_NUM])
#define getTValues (*(getTValuesPointer)Activity_API[getTValues_NUM])
#define getOutputType (*(getOutputTypePointer)Activity_API[getOutputType_NUM])
#define getManipulationMode                                                    \
  (*(getManipulationModePointer)Activity_API[getManipulationMode_NUM])
#define manipulationNames                                                      \
  (*(manipulationNamesPointer)Activity_API[manipulationNames_NUM])
#define manipulationValues                                                     \
  (*(manipulationValuesPointer)Activity_API[manipulationValues_NUM])

/* Return -1 on error, 0 on success.
 * PyCapsule_Import will set an exception if there's an error.
 */
static void **Activity_API;
static int _import_Activity(void) {
  Activity_API = (void **)PyCapsule_Import("sund._Activity._C_API", 0);
  return (Activity_API != NULL) ? 0 : -1;
}

// Add these constants for the output types
#define CONSTANT 0
#define PIECEWISE_CONSTANT 1
#define PIECEWISE_LINEAR 2
#define CUBIC_SPLINE 3

#endif
