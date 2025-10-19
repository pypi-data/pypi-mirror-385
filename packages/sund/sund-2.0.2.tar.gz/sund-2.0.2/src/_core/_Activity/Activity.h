#ifndef ACTIVITY_H
#define ACTIVITY_H

#define NPY_NO_DEPRECATED_API NPY_2_3_API_VERSION
#include "Python.h"
#include <numpy/arrayobject.h>

#define ACTIVITY_OUTPUT 0
#define ACTIVITY_FEATURE 1

/* C API defines */
#define isActivity_NUM 0
#define outputFeature_NUM 1

#define nrOutputs_NUM 2

#define nrFeatures_NUM 3

#define outputNames_NUM 4

#define featureNames_NUM 5

#define featureUnits_NUM 6

#define timeUnit_NUM 7

#define setNonEditable_NUM 8

#define getTValues_NUM 9

#define getOutputType_NUM 10

#define getManipulationMode_NUM 11

#define manipulationNames_NUM 12

#define manipulationValues_NUM 13

/* Total number of C API pointers */
#define Activity_API_pointers 14

/*
==========================================================================================
Structure definitions
==========================================================================================
*/
// Output Objects
typedef double (*OutputFunction)(void *output, double time_local);

typedef struct {
  OutputFunction out_function;
  destructor out_dealloc;
  int type;
  int isFeature;
  double output;
} ActivityOutput;

typedef struct {
  ActivityOutput base;
  double constant;
} ConstantOutput;

typedef struct {
  ActivityOutput base;
  PyObject *tvalues;
  PyObject *fvalues;
} PiecewiseOutput;

typedef struct {
  ActivityOutput base;
  PyObject *tvalues;
  PyObject *fvalues;
  double *b;
  double *c;
  double *d;
  int last;
} CubicSplineOutput;

typedef struct {
  ActivityOutput base;
  PyObject *tvalues;
  PyObject *fvalues;
  int mode; // 0 = set, 1 = add
} ActivityStateManipulation;

// Activity Objects
typedef struct {
  PyObject_HEAD int nroutputs; // Count of outputs (excludes manipulations)
  int nrfeatures;
  int editable; // only editable before added to a simulations object
  PyObject *outputNames;
  PyObject *manipulationNames;
  PyObject *featureNames;
  PyObject *featureUnits;
  ActivityOutput **outputs;
  ActivityOutput **features;
  ActivityStateManipulation **stateManipulations;
  PyObject *timeUnit;
  PyObject *compartment;
} ActivityObject;

/*
==========================================================================================
Function declaration
==========================================================================================
*/
static void Constant_dealloc(ConstantOutput *self);
static void Piecewise_dealloc(PiecewiseOutput *self);
static void CubicInterpolate_dealloc(CubicSplineOutput *self);
static void StateManipulation_dealloc(ActivityStateManipulation *self);
static ActivityOutput *Activity_ConstantOutput(PyObject *constant);
static ActivityOutput *Activity_PiecewiseConstantOutput(PyObject *tvalues,
                                                        PyObject *fvalues);
static ActivityOutput *Activity_PiecewiseLinearOutput(PyObject *tvalues,
                                                      PyObject *fvalues);
static ActivityOutput *Activity_CubicSplineOutput(PyObject *tvalues,
                                                  PyObject *fvalues);
static ActivityOutput *Activity_StateManipulationOutput(PyObject *tvalues,
                                                        PyObject *fvalues,
                                                        int mode);

bool isActivity(PyObject *obj);
void outputFeature(PyObject *self, double time_local, double *outputvector,
                   double *featurevector, int DOflag);
void manipulationValues(PyObject *self, double time_local, double *manipvector);
int nrOutputs(PyObject *self);
int nrFeatures(PyObject *self);
PyObject *outputNames(PyObject *self);
PyObject *manipulationNames(PyObject *self);
PyObject *featureNames(PyObject *self);
PyObject *featureUnits(PyObject *self);
PyObject *timeUnit(PyObject *self);
void setNonEditable(PyObject *self);
PyArrayObject *getTValues(PyObject *self, int index);

namespace ACTIVITY {
PyObject *addOutput(ActivityObject *self, PyObject *args, PyObject *kwds);
PyObject *add_state_manipulation(ActivityObject *self, PyObject *args,
                                 PyObject *kwds);
PyObject *removeOutputs(ActivityObject *self, PyObject *args, PyObject *kwds);
PyObject *removeManipulations(ActivityObject *self, PyObject *args,
                              PyObject *kwds);
PyObject *getOutputs(ActivityObject *self, PyObject *args, PyObject *kwds);
PyObject *getManipulations(ActivityObject *self, PyObject *args,
                           PyObject *kwds);
PyObject *reduce(ActivityObject *self);
PyObject *setState(ActivityObject *self, PyObject *stateTuple);
PyObject *factory(PyObject *cls, PyObject *args, PyObject *kwds);
} // namespace ACTIVITY

static PyMethodDef Activity_methods[] = {
    {"add_output", (PyCFunction)ACTIVITY::addOutput,
     METH_VARARGS | METH_KEYWORDS, "Add new output"},
    {"add_state_manipulation", (PyCFunction)ACTIVITY::add_state_manipulation,
     METH_VARARGS | METH_KEYWORDS,
     "Add new state manipulation (mode: 'set' or 'add')"},
    {"get_outputs", (PyCFunction)ACTIVITY::getOutputs,
     METH_VARARGS | METH_KEYWORDS,
     "Return activity outputs for provided time points"},
    {"get_manipulations", (PyCFunction)ACTIVITY::getManipulations,
     METH_VARARGS | METH_KEYWORDS,
     "Return activity manipulations for provided time points"},
    {"remove_outputs", (PyCFunction)ACTIVITY::removeOutputs,
     METH_VARARGS | METH_KEYWORDS, "Remove one or more existing outputs"},
    {"remove_manipulations", (PyCFunction)ACTIVITY::removeManipulations,
     METH_VARARGS | METH_KEYWORDS, "Remove one or more existing manipulations"},
    {"__reduce__", (PyCFunction)ACTIVITY::reduce, METH_NOARGS,
     "__reduce__ function"},
    {"__setstate__", (PyCFunction)ACTIVITY::setState, METH_VARARGS,
     "__setstate__ function"},
    {"_factory", (PyCFunction)ACTIVITY::factory,
     METH_VARARGS | METH_KEYWORDS | METH_CLASS,
     "Factory function for pickle reconstruction"},
    {NULL} /* Sentinel */
};

#endif
